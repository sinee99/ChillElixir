import os
import cv2
import numpy as np
import torch
import tensorflow as tf
from flask import Flask, request, jsonify
from PIL import Image
import io
import base64
import sys
from pathlib import Path
import logging

# Flask 앱 초기화
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DogNoseAIService:
    def __init__(self):
        """AI 모델 초기화"""
        self.yolo_model = None
        self.siamese_model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # 모델 로드
        self.load_models()
    
    def load_models(self):
        """YOLOv5와 Siamese 모델 로드"""
        try:
            # YOLOv5 모델 로드 (강아지 코 탐지)
            model_path = './models/yolo_best.pt'
            if os.path.exists(model_path):
                self.yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                               path=model_path, device=self.device)
                self.yolo_model.conf = 0.25  # 신뢰도 임계값
                self.yolo_model.iou = 0.45   # NMS IoU 임계값
                logger.info("YOLOv5 model loaded successfully")
            else:
                logger.warning(f"YOLOv5 model not found at {model_path}")
            
            # Siamese Neural Network 모델 로드 (비문 인식)
            # 사용 가능한 Siamese 모델들 확인
            siamese_models = {
                'original': './models/siamese_original.h5',
                'canny': './models/siamese_canny.h5', 
                'laplacian': './models/siamese_laplacian.h5',
                'sobel': './models/siamese_sobel.h5'
            }
            
            self.available_siamese_models = {}
            
            for model_name, model_path in siamese_models.items():
                if os.path.exists(model_path):
                    try:
                        model = tf.keras.models.load_model(model_path)
                        self.available_siamese_models[model_name] = model
                        logger.info(f"Siamese model '{model_name}' loaded successfully")
                    except Exception as e:
                        logger.warning(f"Failed to load Siamese model '{model_name}': {str(e)}")
                else:
                    logger.warning(f"Siamese model '{model_name}' not found at {model_path}")
            
            # 기본 모델 설정 (우선순위: original > canny > laplacian > sobel)
            for preferred_model in ['original', 'canny', 'laplacian', 'sobel']:
                if preferred_model in self.available_siamese_models:
                    self.siamese_model = self.available_siamese_models[preferred_model]
                    self.current_siamese_model = preferred_model
                    logger.info(f"Using '{preferred_model}' as default Siamese model")
                    break
            
            if not hasattr(self, 'siamese_model'):
                logger.error("No Siamese models could be loaded")
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    def preprocess_image(self, image_data):
        """이미지 전처리"""
        try:
            # Base64 디코딩 또는 바이너리 데이터 처리
            if isinstance(image_data, str):
                # Base64 문자열인 경우
                image_bytes = base64.b64decode(image_data)
            else:
                # 바이너리 데이터인 경우
                image_bytes = image_data
            
            # PIL Image로 변환
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert('RGB')
            
            # OpenCV 형식으로 변환
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return None
    
    def crop_dog_nose(self, image):
        """YOLOv5를 사용하여 강아지 코 영역 크롭"""
        try:
            if self.yolo_model is None:
                return None, "YOLOv5 model not loaded"
            
            # YOLOv5로 추론
            results = self.yolo_model(image)
            
            # 결과 파싱
            detections = results.pandas().xyxy[0]
            
            if len(detections) == 0:
                return None, "No dog nose detected"
            
            # 가장 높은 신뢰도의 탐지 결과 선택
            best_detection = detections.loc[detections['confidence'].idxmax()]
            
            # 바운딩 박스 좌표
            x1, y1, x2, y2 = int(best_detection['xmin']), int(best_detection['ymin']), \
                           int(best_detection['xmax']), int(best_detection['ymax'])
            
            # 코 영역 크롭
            cropped_nose = image[y1:y2, x1:x2]
            
            # 96x96으로 리사이즈 (Siamese 모델 입력 크기)
            cropped_nose = cv2.resize(cropped_nose, (96, 96))
            
            return cropped_nose, None
            
        except Exception as e:
            logger.error(f"Error cropping dog nose: {str(e)}")
            return None, str(e)
    
    def preprocess_for_siamese(self, image, model_type='original'):
        """Siamese 모델을 위한 이미지 전처리"""
        try:
            # 그레이스케일 변환
            if len(image.shape) == 3:
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = image
            
            # 모델 타입에 따른 전처리 적용
            if model_type == 'canny':
                # Canny 에지 검출
                processed_image = cv2.Canny(gray_image, 50, 150)
            elif model_type == 'laplacian':
                # Laplacian 에지 검출
                processed_image = cv2.Laplacian(gray_image, cv2.CV_64F)
                processed_image = np.absolute(processed_image)
                processed_image = np.uint8(processed_image)
            elif model_type == 'sobel':
                # Sobel 에지 검출
                sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
                processed_image = np.sqrt(sobelx**2 + sobely**2)
                processed_image = np.uint8(processed_image)
            else:  # original
                # 원본 그레이스케일 이미지 사용
                processed_image = gray_image
            
            # 가우시안 블러 적용 (노이즈 제거)
            processed_image = cv2.GaussianBlur(processed_image, (3, 3), 0)
            
            # 정규화 (0-255 -> 0-1)
            normalized = processed_image.astype(np.float32) / 255.0
            
            # 차원 추가 (batch dimension)
            processed = np.expand_dims(normalized, axis=0)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preprocessing for Siamese ({model_type}): {str(e)}")
            return None
    
    def extract_nose_features(self, nose_image, model_type='original'):
        """비문 특징 추출"""
        try:
            # 모델 선택
            if hasattr(self, 'available_siamese_models') and model_type in self.available_siamese_models:
                selected_model = self.available_siamese_models[model_type]
            elif self.siamese_model is not None:
                selected_model = self.siamese_model
            else:
                return None, "No Siamese model available"
            
            # 전처리 (모델 타입에 따라 다른 전처리 적용)
            processed_image = self.preprocess_for_siamese(nose_image, model_type)
            if processed_image is None:
                return None, "Failed to preprocess image"
            
            # Siamese 모델에서 특징 추출
            features = selected_model.predict(processed_image)
            
            return features.flatten(), None
            
        except Exception as e:
            logger.error(f"Error extracting nose features: {str(e)}")
            return None, str(e)
    
    def compare_noses(self, nose_image1, nose_image2, model_type='original'):
        """두 비문 이미지 비교"""
        try:
            # 모델 선택
            if hasattr(self, 'available_siamese_models') and model_type in self.available_siamese_models:
                selected_model = self.available_siamese_models[model_type]
            elif self.siamese_model is not None:
                selected_model = self.siamese_model
            else:
                return None, "No Siamese model available"
            
            # 전처리
            processed1 = self.preprocess_for_siamese(nose_image1, model_type)
            processed2 = self.preprocess_for_siamese(nose_image2, model_type)
            
            if processed1 is None or processed2 is None:
                return None, "Failed to preprocess images"
            
            # Siamese 모델로 유사도 계산
            similarity = selected_model.predict([processed1, processed2])
            
            return float(similarity[0][0]), None
            
        except Exception as e:
            logger.error(f"Error comparing noses: {str(e)}")
            return None, str(e)

# AI 서비스 인스턴스 생성
ai_service = DogNoseAIService()

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'yolo_loaded': ai_service.yolo_model is not None,
        'siamese_loaded': ai_service.siamese_model is not None,
        'device': str(ai_service.device),
        'available_siamese_models': list(ai_service.available_siamese_models.keys()) if hasattr(ai_service, 'available_siamese_models') else [],
        'current_siamese_model': getattr(ai_service, 'current_siamese_model', None),
        'total_models_loaded': len(getattr(ai_service, 'available_siamese_models', {})) + (1 if ai_service.yolo_model else 0)
    })

@app.route('/crop_nose', methods=['POST'])
def crop_nose():
    """강아지 코 크롭 API"""
    try:
        # 이미지 데이터 받기
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # 이미지 전처리
        image = ai_service.preprocess_image(image_data)
        if image is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # 코 영역 크롭
        cropped_nose, error = ai_service.crop_dog_nose(image)
        
        if error:
            return jsonify({'error': error}), 400
        
        # 결과 이미지를 Base64로 인코딩
        _, buffer = cv2.imencode('.jpg', cropped_nose)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'cropped_nose': encoded_image,
            'size': cropped_nose.shape
        })
        
    except Exception as e:
        logger.error(f"Error in crop_nose: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/extract_features', methods=['POST'])
def extract_features():
    """비문 특징 추출 API"""
    try:
        # 이미지 데이터 받기
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # 이미지 전처리
        image = ai_service.preprocess_image(image_data)
        if image is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # 코 영역 크롭
        cropped_nose, error = ai_service.crop_dog_nose(image)
        
        if error:
            return jsonify({'error': error}), 400
        
        # 특징 추출
        features, error = ai_service.extract_nose_features(cropped_nose)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'features': features.tolist(),
            'feature_size': len(features)
        })
        
    except Exception as e:
        logger.error(f"Error in extract_features: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/compare_noses', methods=['POST'])
def compare_noses():
    """두 비문 이미지 비교 API"""
    try:
        # 두 이미지 데이터 받기
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({'error': 'Two images required'}), 400
        
        image1_data = request.files['image1'].read()
        image2_data = request.files['image2'].read()
        
        # 선택적 모델 지정
        model_type = request.form.get('model_type', 'original')
        
        # 이미지 전처리
        image1 = ai_service.preprocess_image(image1_data)
        image2 = ai_service.preprocess_image(image2_data)
        
        if image1 is None or image2 is None:
            return jsonify({'error': 'Failed to process images'}), 400
        
        # 코 영역 크롭
        nose1, error1 = ai_service.crop_dog_nose(image1)
        nose2, error2 = ai_service.crop_dog_nose(image2)
        
        if error1 or error2:
            return jsonify({'error': f'Crop failed: {error1 or error2}'}), 400
        
        # 비문 비교 (선택된 모델 사용)
        similarity, error = ai_service.compare_noses(nose1, nose2, model_type)
        
        if error:
            return jsonify({'error': error}), 400
        
        # 결과 판정 (임계값 0.5 사용)
        is_same_dog = similarity > 0.5
        
        return jsonify({
            'success': True,
            'similarity': similarity,
            'is_same_dog': is_same_dog,
            'confidence': 'high' if abs(similarity - 0.5) > 0.3 else 'medium',
            'model_used': model_type
        })
        
    except Exception as e:
        logger.error(f"Error in compare_noses: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/process_full', methods=['POST'])
def process_full():
    """전체 프로세스 (크롭 + 특징 추출) API"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # 선택적 모델 지정
        model_type = request.form.get('model_type', 'original')
        
        # 이미지 전처리
        image = ai_service.preprocess_image(image_data)
        if image is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # 코 영역 크롭
        cropped_nose, error = ai_service.crop_dog_nose(image)
        if error:
            return jsonify({'error': error}), 400
        
        # 특징 추출 (선택된 모델 사용)
        features, error = ai_service.extract_nose_features(cropped_nose, model_type)
        if error:
            return jsonify({'error': error}), 400
        
        # 크롭된 이미지를 Base64로 인코딩
        _, buffer = cv2.imencode('.jpg', cropped_nose)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'cropped_nose': encoded_image,
            'features': features.tolist(),
            'crop_size': cropped_nose.shape,
            'feature_size': len(features),
            'model_used': model_type
        })
        
    except Exception as e:
        logger.error(f"Error in process_full: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/switch_model', methods=['POST'])
def switch_model():
    """Siamese 모델 변경 API"""
    try:
        data = request.get_json()
        if not data or 'model_type' not in data:
            return jsonify({'error': 'model_type is required'}), 400
        
        model_type = data['model_type']
        
        if not hasattr(ai_service, 'available_siamese_models'):
            return jsonify({'error': 'No Siamese models available'}), 500
        
        if model_type not in ai_service.available_siamese_models:
            return jsonify({
                'error': f'Model type "{model_type}" not available',
                'available_models': list(ai_service.available_siamese_models.keys())
            }), 400
        
        # 모델 변경
        ai_service.siamese_model = ai_service.available_siamese_models[model_type]
        ai_service.current_siamese_model = model_type
        
        logger.info(f"Switched to Siamese model: {model_type}")
        
        return jsonify({
            'success': True,
            'current_model': model_type,
            'available_models': list(ai_service.available_siamese_models.keys())
        })
        
    except Exception as e:
        logger.error(f"Error in switch_model: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """사용 가능한 모델 목록 API"""
    try:
        return jsonify({
            'yolo_available': ai_service.yolo_model is not None,
            'siamese_models': {
                'available': list(ai_service.available_siamese_models.keys()) if hasattr(ai_service, 'available_siamese_models') else [],
                'current': getattr(ai_service, 'current_siamese_model', None),
                'descriptions': {
                    'original': 'Original preprocessing (no edge detection)',
                    'canny': 'Canny edge detection preprocessing', 
                    'laplacian': 'Laplacian edge detection preprocessing',
                    'sobel': 'Sobel edge detection preprocessing'
                }
            },
            'total_models': len(getattr(ai_service, 'available_siamese_models', {})) + (1 if ai_service.yolo_model else 0)
        })
        
    except Exception as e:
        logger.error(f"Error in list_models: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 