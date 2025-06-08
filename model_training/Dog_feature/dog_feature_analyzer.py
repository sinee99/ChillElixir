import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
import os
from PIL import Image
import argparse

class DogFeatureAnalyzer:
    def __init__(self, model_path="best.pt"):
        """
        강아지 특징 분석기 초기화
        
        Args:
            model_path (str): YOLOv8 모델 파일 경로
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """YOLOv8 모델 로드"""
        try:
            self.model = YOLO(self.model_path)
            print(f"[✓] 모델 로드 성공: {self.model_path}")
            print(f"[INFO] 모델 클래스: {self.model.names}")
        except Exception as e:
            print(f"[ERROR] 모델 로드 실패: {e}")
            return False
        return True
    
    def analyze_image(self, image_path, conf_threshold=0.5, save_result=True):
        """
        단일 이미지 분석
        
        Args:
            image_path (str): 분석할 이미지 경로
            conf_threshold (float): 신뢰도 임계값
            save_result (bool): 결과 이미지 저장 여부
            
        Returns:
            dict: 분석 결과
        """
        if not os.path.exists(image_path):
            print(f"[ERROR] 이미지 파일을 찾을 수 없습니다: {image_path}")
            return None
        
        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print(f"[ERROR] 이미지를 읽을 수 없습니다: {image_path}")
            return None
        
        # 모델 추론
        results = self.model(image_path, conf=conf_threshold)
        
        # 결과 분석
        analysis_result = {
            'image_path': image_path,
            'detections': [],
            'summary': {}
        }
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # 바운딩 박스 좌표
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # 신뢰도와 클래스
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    detection = {
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'class_id': class_id,
                        'class_name': class_name
                    }
                    analysis_result['detections'].append(detection)
        
        # 클래스별 요약
        class_counts = {}
        for detection in analysis_result['detections']:
            class_name = detection['class_name']
            if class_name not in class_counts:
                class_counts[class_name] = 0
            class_counts[class_name] += 1
        
        analysis_result['summary'] = class_counts
        
        # 결과 출력
        self.print_analysis_result(analysis_result)
        
        # 결과 이미지 저장
        if save_result:
            self.save_annotated_image(image_path, analysis_result)
        
        return analysis_result
    
    def analyze_batch(self, image_folder, conf_threshold=0.5):
        """
        폴더 내 모든 이미지 배치 분석
        
        Args:
            image_folder (str): 이미지 폴더 경로
            conf_threshold (float): 신뢰도 임계값
            
        Returns:
            list: 모든 분석 결과 리스트
        """
        if not os.path.exists(image_folder):
            print(f"[ERROR] 폴더를 찾을 수 없습니다: {image_folder}")
            return []
        
        # 지원하는 이미지 확장자
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        image_files = []
        
        for file in os.listdir(image_folder):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(image_folder, file))
        
        if not image_files:
            print(f"[WARNING] 폴더에서 이미지 파일을 찾을 수 없습니다: {image_folder}")
            return []
        
        print(f"[INFO] {len(image_files)}개의 이미지를 분석합니다...")
        
        batch_results = []
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 분석 중: {os.path.basename(image_path)}")
            result = self.analyze_image(image_path, conf_threshold, save_result=True)
            if result:
                batch_results.append(result)
        
        # 배치 분석 요약
        self.print_batch_summary(batch_results)
        
        return batch_results
    
    def print_analysis_result(self, result):
        """분석 결과 출력"""
        print(f"\n{'='*50}")
        print(f"이미지: {os.path.basename(result['image_path'])}")
        print(f"{'='*50}")
        
        if not result['detections']:
            print("[INFO] 감지된 특징이 없습니다.")
            return
        
        print(f"총 감지된 특징: {len(result['detections'])}개")
        print("\n[감지된 특징 목록]")
        for i, detection in enumerate(result['detections'], 1):
            print(f"{i}. {detection['class_name']} (신뢰도: {detection['confidence']:.2f})")
            x1, y1, x2, y2 = detection['bbox']
            print(f"   위치: ({x1}, {y1}) - ({x2}, {y2})")
        
        print("\n[클래스별 요약]")
        for class_name, count in result['summary'].items():
            print(f"- {class_name}: {count}개")
    
    def print_batch_summary(self, batch_results):
        """배치 분석 요약 출력"""
        if not batch_results:
            return
        
        print(f"\n{'='*60}")
        print("배치 분석 요약")
        print(f"{'='*60}")
        
        total_images = len(batch_results)
        total_detections = sum(len(result['detections']) for result in batch_results)
        
        # 전체 클래스 통계
        overall_summary = {}
        for result in batch_results:
            for class_name, count in result['summary'].items():
                if class_name not in overall_summary:
                    overall_summary[class_name] = 0
                overall_summary[class_name] += count
        
        print(f"총 분석된 이미지: {total_images}개")
        print(f"총 감지된 특징: {total_detections}개")
        print(f"평균 특징 수: {total_detections/total_images:.1f}개/이미지")
        
        print("\n[전체 클래스별 통계]")
        for class_name, count in sorted(overall_summary.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_detections) * 100 if total_detections > 0 else 0
            print(f"- {class_name}: {count}개 ({percentage:.1f}%)")
    
    def save_annotated_image(self, image_path, analysis_result):
        """분석 결과가 표시된 이미지 저장"""
        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            return
        
        # 바운딩 박스와 레이블 그리기
        for detection in analysis_result['detections']:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # 바운딩 박스 그리기
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 레이블 텍스트
            label = f"{class_name} {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # 레이블 배경
            cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            
            # 레이블 텍스트
            cv2.putText(image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # 결과 저장
        output_dir = "results"
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_analyzed.jpg")
        
        cv2.imwrite(output_path, image)
        print(f"[✓] 분석 결과 이미지 저장: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="강아지 특징 분석기")
    parser.add_argument("--image", type=str, help="분석할 단일 이미지 경로")
    parser.add_argument("--folder", type=str, help="분석할 이미지 폴더 경로")
    parser.add_argument("--model", type=str, default="model_training/Dog_feature/best.pt", 
                       help="YOLOv8 모델 파일 경로")
    parser.add_argument("--conf", type=float, default=0.5, help="신뢰도 임계값")
    
    args = parser.parse_args()
    
    # 분석기 초기화
    analyzer = DogFeatureAnalyzer(model_path=args.model)
    
    if args.image:
        # 단일 이미지 분석
        print("단일 이미지 분석을 시작합니다...")
        analyzer.analyze_image(args.image, conf_threshold=args.conf)
    elif args.folder:
        # 폴더 내 모든 이미지 분석
        print("배치 이미지 분석을 시작합니다...")
        analyzer.analyze_batch(args.folder, conf_threshold=args.conf)
    else:
        # 테스트 이미지가 있는지 확인
        test_folder = "test_images"
        if os.path.exists(test_folder):
            print(f"테스트 폴더({test_folder})에서 이미지를 분석합니다...")
            analyzer.analyze_batch(test_folder, conf_threshold=args.conf)
        else:
            print("사용법:")
            print("  단일 이미지: python dog_feature_analyzer.py --image path/to/image.jpg")
            print("  폴더 분석: python dog_feature_analyzer.py --folder path/to/folder")
            print("  테스트: test_images 폴더에 이미지를 넣고 실행하세요")

if __name__ == "__main__":
    main() 