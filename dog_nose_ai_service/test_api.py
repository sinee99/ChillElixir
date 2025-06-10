#!/usr/bin/env python3
"""
강아지 비문 인식 API 테스트 스크립트
"""

import requests
import json
import base64
import io
from pathlib import Path

# API 서버 설정
API_BASE_URL = "http://localhost:5000"  # Nginx를 통한 경우: http://localhost
DIRECT_API_URL = "http://localhost:5000"  # 직접 연결

def test_health_check():
    """헬스 체크 테스트"""
    print("🔍 헬스 체크 테스트...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ 헬스 체크 성공!")
            print(f"   상태: {data['status']}")
            print(f"   YOLO 모델: {'로드됨' if data['yolo_loaded'] else '로드 안됨'}")
            print(f"   Siamese 모델: {'로드됨' if data['siamese_loaded'] else '로드 안됨'}")
            print(f"   디바이스: {data['device']}")
            print(f"   사용 가능한 모델: {data['available_siamese_models']}")
            print(f"   현재 모델: {data['current_siamese_model']}")
            return True
        else:
            print(f"❌ 헬스 체크 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 헬스 체크 오류: {str(e)}")
        return False

def test_models_list():
    """모델 목록 조회 테스트"""
    print("\n🔍 모델 목록 조회 테스트...")
    try:
        response = requests.get(f"{API_BASE_URL}/models")
        if response.status_code == 200:
            data = response.json()
            print("✅ 모델 목록 조회 성공!")
            print(f"   YOLO 사용 가능: {data['yolo_available']}")
            print(f"   Siamese 모델들: {data['siamese_models']['available']}")
            print(f"   현재 Siamese 모델: {data['siamese_models']['current']}")
            print(f"   총 모델 수: {data['total_models']}")
            return True
        else:
            print(f"❌ 모델 목록 조회 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 모델 목록 조회 오류: {str(e)}")
        return False

def test_switch_model(model_type="canny"):
    """모델 전환 테스트"""
    print(f"\n🔍 모델 전환 테스트 ({model_type})...")
    try:
        data = {"model_type": model_type}
        response = requests.post(f"{API_BASE_URL}/switch_model", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ 모델 전환 성공!")
            print(f"   현재 모델: {result['current_model']}")
            print(f"   사용 가능한 모델: {result['available_models']}")
            return True
        else:
            print(f"❌ 모델 전환 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 모델 전환 오류: {str(e)}")
        return False

def test_crop_nose(image_path):
    """코 크롭 테스트"""
    print(f"\n🔍 코 크롭 테스트 ({image_path})...")
    try:
        if not Path(image_path).exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return False
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_BASE_URL}/crop_nose", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 코 크롭 성공!")
            print(f"   크롭 이미지 크기: {data['size']}")
            
            # 크롭된 이미지 저장 (선택사항)
            cropped_image_data = base64.b64decode(data['cropped_nose'])
            output_path = f"cropped_nose_{Path(image_path).stem}.jpg"
            with open(output_path, 'wb') as f:
                f.write(cropped_image_data)
            print(f"   크롭된 이미지 저장: {output_path}")
            return True
        else:
            print(f"❌ 코 크롭 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 코 크롭 오류: {str(e)}")
        return False

def test_extract_features(image_path):
    """특징 추출 테스트"""
    print(f"\n🔍 특징 추출 테스트 ({image_path})...")
    try:
        if not Path(image_path).exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return False
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_BASE_URL}/extract_features", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 특징 추출 성공!")
            print(f"   특징 벡터 크기: {data['feature_size']}")
            print(f"   특징 벡터 샘플: {data['features'][:5]}...")
            return True
        else:
            print(f"❌ 특징 추출 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 특징 추출 오류: {str(e)}")
        return False

def test_compare_noses(image1_path, image2_path, model_type="original"):
    """비문 비교 테스트"""
    print(f"\n🔍 비문 비교 테스트 ({image1_path} vs {image2_path})...")
    try:
        if not Path(image1_path).exists() or not Path(image2_path).exists():
            print("❌ 이미지 파일 중 하나 이상을 찾을 수 없습니다")
            return False
        
        with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
            files = {'image1': f1, 'image2': f2}
            data = {'model_type': model_type}
            response = requests.post(f"{API_BASE_URL}/compare_noses", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 비문 비교 성공!")
            print(f"   유사도: {result['similarity']:.4f}")
            print(f"   같은 개체: {'예' if result['is_same_dog'] else '아니오'}")
            print(f"   신뢰도: {result['confidence']}")
            print(f"   사용된 모델: {result['model_used']}")
            return True
        else:
            print(f"❌ 비문 비교 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 비문 비교 오류: {str(e)}")
        return False

def test_process_full(image_path, model_type="original"):
    """전체 프로세스 테스트"""
    print(f"\n🔍 전체 프로세스 테스트 ({image_path})...")
    try:
        if not Path(image_path).exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return False
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'model_type': model_type}
            response = requests.post(f"{API_BASE_URL}/process_full", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 전체 프로세스 성공!")
            print(f"   크롭 이미지 크기: {result['crop_size']}")
            print(f"   특징 벡터 크기: {result['feature_size']}")
            print(f"   사용된 모델: {result['model_used']}")
            
            # 결과 이미지 저장 (선택사항)
            cropped_image_data = base64.b64decode(result['cropped_nose'])
            output_path = f"full_process_{Path(image_path).stem}_{model_type}.jpg"
            with open(output_path, 'wb') as f:
                f.write(cropped_image_data)
            print(f"   결과 이미지 저장: {output_path}")
            return True
        else:
            print(f"❌ 전체 프로세스 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 전체 프로세스 오류: {str(e)}")
        return False

def main():
    """메인 테스트 함수"""
    print("🐕 강아지 비문 인식 API 테스트 시작")
    print("=" * 50)
    
    # 기본 테스트
    if not test_health_check():
        print("❌ 서버가 응답하지 않습니다. Docker 컨테이너가 실행 중인지 확인하세요.")
        return
    
    test_models_list()
    test_switch_model("canny")
    
    # 이미지 테스트 (테스트 이미지가 있는 경우)
    test_images = [
        "test_dog1.jpg",
        "test_dog2.jpg",
        "sample_dog.jpg"
    ]
    
    available_images = [img for img in test_images if Path(img).exists()]
    
    if available_images:
        print(f"\n📸 발견된 테스트 이미지: {available_images}")
        
        # 첫 번째 이미지로 테스트
        first_image = available_images[0]
        test_crop_nose(first_image)
        test_extract_features(first_image)
        test_process_full(first_image, "original")
        test_process_full(first_image, "canny")
        
        # 두 개 이상의 이미지가 있으면 비교 테스트
        if len(available_images) >= 2:
            test_compare_noses(available_images[0], available_images[1], "original")
            test_compare_noses(available_images[0], available_images[1], "canny")
    else:
        print("\n📸 테스트할 이미지가 없습니다.")
        print("   test_dog1.jpg, test_dog2.jpg 등의 강아지 이미지를 추가하여 테스트해보세요.")
    
    print("\n🎉 API 테스트 완료!")

if __name__ == "__main__":
    main() 