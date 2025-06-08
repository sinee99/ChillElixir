#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import warnings
from pathlib import Path

# 모든 경고 메시지 숨기기
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from nose import DogNosePreprocessorYOLOv5

def quick_test():
    print("🐕 강아지 코 탐지 - 빠른 테스트")
    print("=" * 40)
    
    # 입력 폴더 확인
    input_folder = "test_images"
    if not Path(input_folder).exists():
        print(f"❌ {input_folder} 폴더가 없습니다!")
        print("테스트 이미지를 넣을 폴더를 만들겠습니다.")
        Path(input_folder).mkdir(exist_ok=True)
        print(f"📁 {input_folder} 폴더를 생성했습니다.")
        print("강아지 이미지를 넣고 다시 실행해주세요.")
        return
    
    # 이미지 파일 확인
    image_files = list(Path(input_folder).glob("*.jpg")) + \
                 list(Path(input_folder).glob("*.jpeg")) + \
                 list(Path(input_folder).glob("*.png"))
    
    if not image_files:
        print(f"❌ {input_folder}에 이미지가 없습니다!")
        print("jpg, jpeg, png 파일을 넣어주세요.")
        return
    
    print(f"📸 {len(image_files)}개 이미지 발견")
    
    try:
        print("🤖 모델 로딩... (최초 실행시 시간이 걸릴 수 있습니다)")
        
        # 간단한 설정으로 전처리기 생성
        preprocessor = DogNosePreprocessorYOLOv5(
            confidence_threshold=0.3,  # 낮은 신뢰도로 더 많이 탐지
            target_size=(224, 224)
        )
        
        output_folder = "quick_results"
        Path(output_folder).mkdir(exist_ok=True)
        
        print("🔍 이미지 처리 중...")
        success_count = 0
        
        for i, img_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] {img_file.name}")
            
            result = preprocessor.process_image(img_file)
            if result is not None:
                import cv2
                save_path = Path(output_folder) / f"nose_{img_file.stem}.jpg"
                cv2.imwrite(str(save_path), (result * 255).astype('uint8'))
                print(f"  ✅ 저장: {save_path}")
                success_count += 1
            else:
                print(f"  ❌ 실패")
        
        print(f"\n📊 결과: {success_count}/{len(image_files)} 성공")
        if success_count > 0:
            print(f"📁 결과 폴더: {output_folder}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        print("문제가 계속되면 패키지 설치를 확인해주세요:")
        print("pip install torch torchvision opencv-python seaborn")

if __name__ == "__main__":
    quick_test() 