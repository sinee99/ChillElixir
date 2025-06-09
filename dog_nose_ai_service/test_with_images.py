#!/usr/bin/env python3
"""
test_images 폴더의 이미지들로 강아지 비문 인식 API 테스트
"""

import requests
import json
import os
from pathlib import Path
import time

class DogNoseAPITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_images_dir = Path("test_images")
        
    def get_test_images(self):
        """테스트 이미지 목록 가져오기"""
        if not self.test_images_dir.exists():
            print(f"❌ {self.test_images_dir} 폴더를 찾을 수 없습니다.")
            return []
        
        # 이미지 파일 확장자
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        images = []
        for file_path in self.test_images_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                images.append(file_path)
        
        return sorted(images)
    
    def test_health(self):
        """헬스 체크"""
        print("🔍 서비스 헬스 체크...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 상태: {data.get('status')}")
                print(f"   🧠 YOLO 모델: {'✅' if data.get('yolo_loaded') else '❌'}")
                print(f"   🤖 Siamese 모델: {'✅' if data.get('siamese_loaded') else '❌'}")
                print(f"   💻 디바이스: {data.get('device')}")
                return True
            else:
                print(f"   ❌ 헬스 체크 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 연결 실패: {e}")
            return False
    
    def test_crop_nose(self, image_path):
        """코 크롭 테스트"""
        print(f"\n🐕 코 크롭 테스트: {image_path.name}")
        
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(f"{self.base_url}/crop_nose", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"   ✅ 성공! 크롭 크기: {data.get('size')}")
                    return True
                else:
                    print(f"   ❌ 실패: {data.get('error')}")
                    return False
            else:
                print(f"   ❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 예외 발생: {e}")
            return False
    
    def test_extract_features(self, image_path):
        """특징 추출 테스트"""
        print(f"\n🧠 특징 추출 테스트: {image_path.name}")
        
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(f"{self.base_url}/extract_features", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    feature_size = data.get('feature_size', 0)
                    print(f"   ✅ 성공! 특징 벡터 크기: {feature_size}")
                    return True, data.get('features')
                else:
                    print(f"   ❌ 실패: {data.get('error')}")
                    return False, None
            else:
                print(f"   ❌ HTTP 오류: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ 예외 발생: {e}")
            return False, None
    
    def test_compare_noses(self, image1_path, image2_path):
        """비문 비교 테스트"""
        print(f"\n🔍 비문 비교 테스트:")
        print(f"   이미지1: {image1_path.name}")
        print(f"   이미지2: {image2_path.name}")
        
        try:
            with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
                files = {
                    'image1': f1,
                    'image2': f2
                }
                response = requests.post(f"{self.base_url}/compare_noses", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    similarity = data.get('similarity', 0)
                    is_same = data.get('is_same_dog', False)
                    confidence = data.get('confidence', 'unknown')
                    
                    print(f"   ✅ 성공!")
                    print(f"   📊 유사도: {similarity:.4f}")
                    print(f"   🐕 같은 개: {'예' if is_same else '아니오'}")
                    print(f"   🎯 신뢰도: {confidence}")
                    return True
                else:
                    print(f"   ❌ 실패: {data.get('error')}")
                    return False
            else:
                print(f"   ❌ HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 예외 발생: {e}")
            return False
    
    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🐕 강아지 비문 인식 AI 서비스 종합 테스트")
        print("=" * 50)
        
        # 1. 헬스 체크
        if not self.test_health():
            print("\n❌ 서비스가 실행되지 않았습니다. python app.py를 먼저 실행하세요!")
            return
        
        # 2. 테스트 이미지 확인
        images = self.get_test_images()
        if not images:
            print("\n❌ 테스트 이미지를 찾을 수 없습니다.")
            return
        
        print(f"\n📁 발견된 테스트 이미지: {len(images)}개")
        for i, img in enumerate(images[:5]):  # 최대 5개만 표시
            print(f"   {i}: {img.name}")
        
        # 3. 첫 번째 이미지로 코 크롭 테스트
        if images:
            self.test_crop_nose(images[0])
        
        # 4. 첫 번째 이미지로 특징 추출 테스트
        if images:
            self.test_extract_features(images[0])
        
        # 5. 두 이미지 비교 테스트 (같은 이미지)
        if len(images) >= 1:
            print(f"\n🔄 같은 이미지 비교 (유사도가 높아야 함)")
            self.test_compare_noses(images[0], images[0])
        
        # 6. 서로 다른 이미지 비교 테스트
        if len(images) >= 2:
            print(f"\n🔄 다른 이미지 비교")
            self.test_compare_noses(images[0], images[1])
        
        # 7. 추가 비교 테스트 (몇 개 더)
        if len(images) >= 3:
            print(f"\n🔄 추가 비교 테스트")
            for i in range(min(3, len(images)-1)):
                self.test_compare_noses(images[i], images[i+1])
                time.sleep(0.5)  # API 호출 간격
        
        print(f"\n🎉 테스트 완료!")

def main():
    tester = DogNoseAPITester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 