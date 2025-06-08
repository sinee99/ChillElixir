#!/usr/bin/env python3
"""
Dog Nose AI Service API 테스트 스크립트
"""

import requests
import base64
import json
import sys
from pathlib import Path
import argparse

class DogNoseAPITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self):
        """헬스 체크 테스트"""
        print("🔍 Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed!")
                print(f"   Status: {data.get('status')}")
                print(f"   YOLOv5 loaded: {data.get('yolo_loaded')}")
                print(f"   Siamese loaded: {data.get('siamese_loaded')}")
                print(f"   Device: {data.get('device')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def load_test_image(self, image_path):
        """테스트 이미지 로드"""
        try:
            with open(image_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Failed to load image {image_path}: {str(e)}")
            return None
    
    def test_crop_nose(self, image_path):
        """코 크롭 테스트"""
        print("\n🐕 Testing nose cropping...")
        
        image_data = self.load_test_image(image_path)
        if image_data is None:
            return False
        
        try:
            files = {'image': ('test.jpg', image_data, 'image/jpeg')}
            response = self.session.post(f"{self.base_url}/crop_nose", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Nose cropping successful!")
                    print(f"   Cropped size: {data.get('size')}")
                    
                    # 크롭된 이미지 저장 (선택사항)
                    if 'cropped_nose' in data:
                        cropped_data = base64.b64decode(data['cropped_nose'])
                        with open('test_cropped_nose.jpg', 'wb') as f:
                            f.write(cropped_data)
                        print("   Cropped image saved as: test_cropped_nose.jpg")
                    
                    return True
                else:
                    print(f"❌ Nose cropping failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Nose cropping request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Nose cropping error: {str(e)}")
            return False
    
    def test_extract_features(self, image_path):
        """특징 추출 테스트"""
        print("\n🧠 Testing feature extraction...")
        
        image_data = self.load_test_image(image_path)
        if image_data is None:
            return False
        
        try:
            files = {'image': ('test.jpg', image_data, 'image/jpeg')}
            response = self.session.post(f"{self.base_url}/extract_features", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Feature extraction successful!")
                    print(f"   Feature vector size: {data.get('feature_size')}")
                    return True
                else:
                    print(f"❌ Feature extraction failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Feature extraction request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Feature extraction error: {str(e)}")
            return False
    
    def test_compare_noses(self, image1_path, image2_path):
        """비문 비교 테스트"""
        print("\n🔍 Testing nose comparison...")
        
        image1_data = self.load_test_image(image1_path)
        image2_data = self.load_test_image(image2_path)
        
        if image1_data is None or image2_data is None:
            return False
        
        try:
            files = {
                'image1': ('test1.jpg', image1_data, 'image/jpeg'),
                'image2': ('test2.jpg', image2_data, 'image/jpeg')
            }
            response = self.session.post(f"{self.base_url}/compare_noses", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Nose comparison successful!")
                    print(f"   Similarity: {data.get('similarity'):.4f}")
                    print(f"   Same dog: {data.get('is_same_dog')}")
                    print(f"   Confidence: {data.get('confidence')}")
                    return True
                else:
                    print(f"❌ Nose comparison failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Nose comparison request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Nose comparison error: {str(e)}")
            return False
    
    def test_process_full(self, image_path):
        """전체 프로세스 테스트"""
        print("\n🚀 Testing full process...")
        
        image_data = self.load_test_image(image_path)
        if image_data is None:
            return False
        
        try:
            files = {'image': ('test.jpg', image_data, 'image/jpeg')}
            response = self.session.post(f"{self.base_url}/process_full", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Full process successful!")
                    print(f"   Crop size: {data.get('crop_size')}")
                    print(f"   Feature size: {data.get('feature_size')}")
                    return True
                else:
                    print(f"❌ Full process failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Full process request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Full process error: {str(e)}")
            return False
    
    def test_models_api(self):
        """모델 목록 API 테스트"""
        print("\n🔧 Testing models API...")
        try:
            response = self.session.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                print("✅ Models API successful!")
                print(f"   YOLOv5 available: {data.get('yolo_available')}")
                print(f"   Available Siamese models: {data.get('siamese_models', {}).get('available', [])}")
                print(f"   Current Siamese model: {data.get('siamese_models', {}).get('current')}")
                print(f"   Total models: {data.get('total_models')}")
                return True
            else:
                print(f"❌ Models API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Models API error: {str(e)}")
            return False

    def test_model_switching(self):
        """모델 전환 테스트"""
        print("\n🔄 Testing model switching...")
        try:
            # 먼저 사용 가능한 모델 확인
            models_response = self.session.get(f"{self.base_url}/models")
            if models_response.status_code != 200:
                print("❌ Cannot get available models")
                return False
            
            models_data = models_response.json()
            available_models = models_data.get('siamese_models', {}).get('available', [])
            
            if len(available_models) < 2:
                print("⚠️ Not enough models to test switching")
                return True  # 테스트는 통과로 처리
            
            # 다른 모델로 전환 시도
            current_model = models_data.get('siamese_models', {}).get('current')
            test_model = None
            for model in available_models:
                if model != current_model:
                    test_model = model
                    break
            
            if not test_model:
                print("⚠️ No alternative model found")
                return True
            
            # 모델 전환 요청
            switch_data = {'model_type': test_model}
            response = self.session.post(f"{self.base_url}/switch_model", 
                                       json=switch_data,
                                       headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('current_model') == test_model:
                    print(f"✅ Model switching successful! Switched to: {test_model}")
                    
                    # 원래 모델로 되돌리기
                    if current_model:
                        restore_data = {'model_type': current_model}
                        self.session.post(f"{self.base_url}/switch_model", 
                                        json=restore_data,
                                        headers={'Content-Type': 'application/json'})
                    
                    return True
                else:
                    print(f"❌ Model switching failed: {data}")
                    return False
            else:
                print(f"❌ Model switching request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Model switching error: {str(e)}")
            return False

    def run_all_tests(self, image_path, image2_path=None):
        """모든 테스트 실행"""
        print("🐕 Starting Dog Nose AI Service API Tests")
        print("=" * 50)
        
        results = {}
        
        # 헬스 체크
        results['health'] = self.test_health()
        
        if not results['health']:
            print("\n❌ Service is not healthy. Stopping tests.")
            return results
        
        # 이미지 파일 존재 확인
        if not Path(image_path).exists():
            print(f"\n❌ Test image not found: {image_path}")
            return results
        
        # 모델 관련 테스트
        results['models_api'] = self.test_models_api()
        results['model_switching'] = self.test_model_switching()
        
        # 개별 테스트 실행
        results['crop'] = self.test_crop_nose(image_path)
        results['features'] = self.test_extract_features(image_path)
        results['full_process'] = self.test_process_full(image_path)
        
        # 비교 테스트 (두 번째 이미지가 있는 경우)
        if image2_path and Path(image2_path).exists():
            results['compare'] = self.test_compare_noses(image_path, image2_path)
        else:
            print("\n⚠️ Second image not provided, skipping comparison test")
            results['compare'] = None
        
        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")
        print(f"   Health Check: {'✅' if results['health'] else '❌'}")
        print(f"   Models API: {'✅' if results['models_api'] else '❌'}")
        print(f"   Model Switching: {'✅' if results['model_switching'] else '❌'}")
        print(f"   Nose Cropping: {'✅' if results['crop'] else '❌'}")
        print(f"   Feature Extraction: {'✅' if results['features'] else '❌'}")
        print(f"   Full Process: {'✅' if results['full_process'] else '❌'}")
        
        if results['compare'] is not None:
            print(f"   Nose Comparison: {'✅' if results['compare'] else '❌'}")
        
        # 전체 성공 여부
        success_count = sum(1 for v in results.values() if v is True)
        total_tests = sum(1 for v in results.values() if v is not None)
        
        print(f"\n🎯 Overall Success Rate: {success_count}/{total_tests} tests passed")
        
        if success_count == total_tests:
            print("🎉 All tests passed! Service is working correctly.")
        else:
            print("⚠️ Some tests failed. Please check the service.")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Test Dog Nose AI Service API')
    parser.add_argument('--url', default='http://localhost:5000',
                       help='API base URL (default: http://localhost:5000)')
    parser.add_argument('--image', required=True,
                       help='Path to test image file')
    parser.add_argument('--image2', 
                       help='Path to second test image for comparison')
    
    args = parser.parse_args()
    
    tester = DogNoseAPITester(args.url)
    results = tester.run_all_tests(args.image, args.image2)
    
    # 종료 코드 설정
    success_count = sum(1 for v in results.values() if v is True)
    total_tests = sum(1 for v in results.values() if v is not None)
    
    return 0 if success_count == total_tests else 1

if __name__ == "__main__":
    exit(main()) 