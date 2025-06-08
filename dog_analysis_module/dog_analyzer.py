from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import os
import logging
from config import Config

class DogAnalyzer:
    def __init__(self):
        """YOLOv8 모델 초기화"""
        try:
            self.model = YOLO(Config.MODEL_PATH)
            self.confidence_threshold = Config.CONFIDENCE_THRESHOLD
            self.dog_classes = Config.DOG_CLASSES
            
            logging.info(f"모델이 성공적으로 로드되었습니다: {Config.MODEL_PATH}")
            
        except Exception as e:
            logging.error(f"모델 로드 중 오류 발생: {str(e)}")
            raise e
    
    def preprocess_image(self, image_path: str):
        """
        이미지 전처리
        
        Args:
            image_path (str): 이미지 파일 경로
            
        Returns:
            numpy.ndarray: 전처리된 이미지
        """
        try:
            # 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("이미지를 로드할 수 없습니다.")
            
            # RGB로 변환 (OpenCV는 BGR을 사용하므로)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return image
            
        except Exception as e:
            logging.error(f"이미지 전처리 중 오류 발생: {str(e)}")
            raise e
    
    def analyze_dog_image(self, image_path: str):
        """
        강아지 이미지 분석
        
        Args:
            image_path (str): 분석할 이미지 파일 경로
            
        Returns:
            tuple: (predictions_dict, confidence_scores_dict, raw_results)
        """
        try:
            # 이미지 전처리
            image = self.preprocess_image(image_path)
            
            # YOLOv8 모델로 예측 수행
            results = self.model(image, conf=self.confidence_threshold)
            
            predictions = {}
            confidence_scores = {}
            
            # 결과 처리
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # 클래스 ID와 신뢰도 추출
                        class_id = int(box.cls.cpu().numpy()[0])
                        confidence = float(box.conf.cpu().numpy()[0])
                        
                        # 클래스 이름 매핑
                        if class_id in self.dog_classes:
                            class_name = self.dog_classes[class_id]
                            predictions[class_id] = class_name
                            confidence_scores[class_id] = confidence
                        else:
                            # 알려지지 않은 클래스의 경우
                            predictions[class_id] = f"Unknown_Class_{class_id}"
                            confidence_scores[class_id] = confidence
            
            if not predictions:
                logging.warning("이미지에서 강아지를 감지하지 못했습니다.")
                return {}, {}, results
            
            # 결과 로깅
            best_class_id = max(confidence_scores.keys(), key=lambda x: confidence_scores[x])
            logging.info(f"분석 완료 - 예측: {predictions[best_class_id]}, 신뢰도: {confidence_scores[best_class_id]:.3f}")
            
            return predictions, confidence_scores, results
            
        except Exception as e:
            logging.error(f"강아지 이미지 분석 중 오류 발생: {str(e)}")
            raise e
    
    def validate_image_file(self, file_path: str):
        """
        이미지 파일 유효성 검증
        
        Args:
            file_path (str): 검증할 파일 경로
            
        Returns:
            bool: 유효성 여부
        """
        try:
            # 파일 존재 여부 확인
            if not os.path.exists(file_path):
                logging.error(f"파일이 존재하지 않습니다: {file_path}")
                return False
            
            # 파일 확장자 확인
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in Config.ALLOWED_EXTENSIONS:
                logging.error(f"지원되지 않는 파일 형식입니다: {file_ext}")
                return False
            
            # 파일 크기 확인
            file_size = os.path.getsize(file_path)
            if file_size > Config.MAX_FILE_SIZE:
                logging.error(f"파일 크기가 너무 큽니다: {file_size} bytes")
                return False
            
            # PIL로 이미지 열기 시도
            try:
                with Image.open(file_path) as img:
                    img.verify()
                return True
            except Exception as e:
                logging.error(f"이미지 파일이 손상되었습니다: {str(e)}")
                return False
                
        except Exception as e:
            logging.error(f"파일 검증 중 오류 발생: {str(e)}")
            return False
    
    def get_model_info(self):
        """
        모델 정보 반환
        
        Returns:
            dict: 모델 정보
        """
        return {
            "model_path": Config.MODEL_PATH,
            "confidence_threshold": self.confidence_threshold,
            "supported_classes": self.dog_classes,
            "model_type": "YOLOv8"
        } 