import cv2
import torch
import numpy as np
from pathlib import Path
import warnings
import os

# 경고 메시지 숨기기
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

class DogNosePreprocessorYOLOv5:
    def __init__(self, model_path='model_training/Dog_nose/best.pt', target_size=(224, 224), confidence_threshold=0.5, nose_class_id=0):
        """
        model_path: YOLOv5로 학습된 모델 경로
        target_size: 출력 이미지 크기
        confidence_threshold: 탐지 신뢰도 임계값
        nose_class_id: 코 클래스 ID
        """
        try:
            # 경고 메시지 임시 억제
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, verbose=False)
            
            # CUDA 호환성 문제 방지 - CPU 모드로 강제 실행
            if hasattr(self.model, 'cpu'):
                self.model = self.model.cpu()
            
            print(f"✅ 모델 로드 성공: {model_path} (CPU 모드)")
        except FileNotFoundError:
            print(f"⚠️  커스텀 모델을 찾을 수 없습니다: {model_path}")
            print("기본 YOLOv5s 모델을 사용합니다.")
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', verbose=False)
                
                # CPU 모드로 강제 실행
                if hasattr(self.model, 'cpu'):
                    self.model = self.model.cpu()
                    
                print("✅ 기본 모델 로드 성공! (CPU 모드)")
            except Exception as e:
                print(f"❌ 모델 로드 실패: {e}")
                print("\n🔧 해결 방법:")
                print("1. pip install seaborn matplotlib pandas scipy")
                print("2. 또는: pip install -r requirements.txt")
                raise e
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            if "seaborn" in str(e):
                print("\n🔧 seaborn 모듈이 필요합니다!")
                print("다음 명령어를 실행해주세요:")
                print("pip install seaborn matplotlib pandas scipy")
            else:
                print("기본 YOLOv5s 모델을 시도합니다.")
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', verbose=False)
                    print("✅ 기본 모델 로드 성공!")
                except Exception as e2:
                    print(f"❌ 기본 모델도 로드 실패: {e2}")
                    print("\n🔧 해결 방법:")
                    print("1. pip install seaborn matplotlib pandas scipy")
                    print("2. 또는: pip install -r requirements.txt")
                    raise e2
        
        self.target_size = target_size
        self.conf_threshold = confidence_threshold
        self.nose_class_id = nose_class_id

    def detect_nose(self, image):
        """강아지 코 탐지"""
        results = self.model(image)
        detections = results.xyxy[0].cpu().numpy()

        best_conf = 0
        best_box = None
        
        # 강아지(person) 클래스도 확인 (기본 모델 사용시)
        valid_classes = [self.nose_class_id, 16]  # 16은 dog 클래스 (COCO dataset)
        
        for det in detections:
            x1, y1, x2, y2, conf, cls_id = det[:6]
            cls_id = int(cls_id)
            
            # 커스텀 모델이면 nose_class_id만 확인, 기본 모델이면 dog 클래스 확인
            if conf >= self.conf_threshold and (cls_id == self.nose_class_id or cls_id == 16):
                if conf > best_conf:
                    best_conf = conf
                    best_box = [int(x1), int(y1), int(x2), int(y2)]

        if best_box:
            x1, y1, x2, y2 = best_box
            
            # 박스 크기 확장 (코 주변 영역 포함)
            h, w = image.shape[:2]
            margin = 20
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(w, x2 + margin)
            y2 = min(h, y2 + margin)
            
            cropped = image[y1:y2, x1:x2]
            print(f"  ✅ 탐지 성공! 신뢰도: {best_conf:.3f}, 박스: ({x1},{y1},{x2},{y2})")
            return cropped
        else:
            return None

    def preprocess(self, nose_crop):
        gray = cv2.cvtColor(nose_crop, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        resized = cv2.resize(enhanced, self.target_size)
        normalized = resized.astype(np.float32) / 255.0
        return normalized

    def process_image(self, image_path):
        """단일 이미지 처리"""
        print(f"  📖 이미지 로딩 중...")
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"  ❌ 이미지 로드 실패: {image_path}")
            return None

        print(f"  🔍 코 탐지 중... (이미지 크기: {image.shape[1]}x{image.shape[0]})")
        nose_crop = self.detect_nose(image)
        if nose_crop is not None:
            print(f"  🎨 전처리 중...")
            preprocessed = self.preprocess(nose_crop)
            return preprocessed
        else:
            print(f"  ⚠️  코 탐지 실패: {image_path.name}")
            return None

    def process_directory(self, input_dir, output_dir):
        """디렉토리 내 모든 이미지 처리"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 지원하는 이미지 확장자
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_files = [f for f in input_dir.glob("*.*") if f.suffix.lower() in valid_extensions]
        
        if not image_files:
            print(f"⚠️  {input_dir}에서 이미지 파일을 찾을 수 없습니다.")
            return
        
        print(f"📸 총 {len(image_files)}개의 이미지를 처리합니다.")
        
        success_count = 0
        fail_count = 0
        
        for i, img_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 처리 중: {img_file.name}")
            
            result = self.process_image(img_file)
            if result is not None:
                save_path = output_dir / f"nose_{img_file.stem}.jpg"
                cv2.imwrite(str(save_path), (result * 255).astype(np.uint8))
                print(f"  💾 저장 완료: {save_path}")
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n📊 처리 결과: 성공 {success_count}개, 실패 {fail_count}개")

if __name__ == "__main__":
    # 사용 예시
    preprocessor = DogNosePreprocessorYOLOv5(
        model_path='model_training/Dog_nose/best.pt',  # YOLOv5로 학습된 모델 경로 (없으면 기본 모델 사용)
        target_size=(224, 224),
        confidence_threshold=0.5,
        nose_class_id=0  # 강아지 코 클래스 ID (기본 모델 사용시 무시됨)
    )

    # 입력 및 출력 폴더 설정
    input_folder = 'input_images'        # 원본 이미지 폴더
    output_folder = 'processed_noses'    # 전처리된 코 이미지 저장 폴더
    
    print("🐕 강아지 코 탐지 및 전처리 시작...")
    print(f"📁 입력 폴더: {input_folder}")
    print(f"📁 출력 폴더: {output_folder}")
    
    # 폴더가 없으면 생성
    Path(input_folder).mkdir(exist_ok=True)
    Path(output_folder).mkdir(exist_ok=True)

    preprocessor.process_directory(input_folder, output_folder)
    
    print("✅ 처리 완료!")
