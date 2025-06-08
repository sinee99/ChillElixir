#!/usr/bin/env python3
"""
강아지 특징 분석기 사용 예제

이 스크립트는 DogFeatureAnalyzer 클래스를 사용하여 
강아지 이미지의 특징을 분석하는 방법을 보여줍니다.
"""

from dog_feature_analyzer import DogFeatureAnalyzer
import os

def main():
    print("🐕 강아지 특징 분석기 예제 🐕")
    print("=" * 50)
    
    # 1. 분석기 초기화
    print("\n1. 분석기 초기화...")
    analyzer = DogFeatureAnalyzer(model_path="model_training/Dog_feature/best.pt")
    
    # 2. 단일 이미지 분석 예제
    print("\n2. 단일 이미지 분석 예제...")
    
    # 테스트 이미지 경로 (존재하는 경우)
    test_image_paths = [
        "test_images/dog1.jpg",
        "test_images/dog2.jpg", 
        "test_images/sample_dog.png",
        "images.jpg"  # 루트 디렉토리의 이미지
    ]
    
    found_image = None
    for path in test_image_paths:
        if os.path.exists(path):
            found_image = path
            break
    
    if found_image:
        print(f"테스트 이미지 발견: {found_image}")
        result = analyzer.analyze_image(found_image, conf_threshold=0.3)
        
        if result and result['detections']:
            print(f"\n분석 결과: {len(result['detections'])}개의 특징 감지됨")
            for detection in result['detections']:
                print(f"- {detection['class_name']}: {detection['confidence']:.2f}")
        else:
            print("감지된 특징이 없습니다. 신뢰도 임계값을 낮춰보세요.")
    else:
        print("테스트 이미지를 찾을 수 없습니다.")
        print("다음 중 하나에 강아지 이미지를 배치하세요:")
        for path in test_image_paths:
            print(f"  - {path}")
    
    # 3. 배치 분석 예제
    print("\n3. 배치 분석 예제...")
    
    if os.path.exists("test_images") and os.listdir("test_images"):
        print("test_images 폴더에서 배치 분석을 시작합니다...")
        batch_results = analyzer.analyze_batch("test_images", conf_threshold=0.3)
        
        if batch_results:
            print(f"\n배치 분석 완료: {len(batch_results)}개 이미지 처리됨")
            
            # 전체 통계
            total_detections = sum(len(result['detections']) for result in batch_results)
            print(f"총 감지된 특징: {total_detections}개")
            
            # 가장 많이 감지된 특징 찾기
            all_classes = {}
            for result in batch_results:
                for class_name, count in result['summary'].items():
                    all_classes[class_name] = all_classes.get(class_name, 0) + count
            
            if all_classes:
                most_common = max(all_classes.items(), key=lambda x: x[1])
                print(f"가장 많이 감지된 특징: {most_common[0]} ({most_common[1]}개)")
        else:
            print("배치 분석 결과가 없습니다.")
    else:
        print("test_images 폴더가 없거나 비어있습니다.")
        print("test_images 폴더에 강아지 이미지들을 넣어보세요.")
    
    # 4. 결과 확인
    print("\n4. 결과 확인...")
    results_dir = "results"
    if os.path.exists(results_dir):
        result_files = [f for f in os.listdir(results_dir) if f.endswith('.jpg')]
        if result_files:
            print(f"분석 결과 이미지 {len(result_files)}개가 '{results_dir}' 폴더에 저장되었습니다:")
            for file in result_files[:5]:  # 최대 5개만 표시
                print(f"  - {file}")
            if len(result_files) > 5:
                print(f"  ... 그 외 {len(result_files) - 5}개 더")
        else:
            print(f"'{results_dir}' 폴더에 결과 이미지가 없습니다.")
    else:
        print("결과 폴더가 생성되지 않았습니다.")
    
    print("\n=" * 50)
    print("예제 실행 완료!")
    print("\n사용 방법:")
    print("1. 단일 이미지: python dog_feature_analyzer.py --image your_image.jpg")
    print("2. 폴더 분석: python dog_feature_analyzer.py --folder your_folder")
    print("3. 신뢰도 조정: python dog_feature_analyzer.py --image your_image.jpg --conf 0.3")

if __name__ == "__main__":
    main() 