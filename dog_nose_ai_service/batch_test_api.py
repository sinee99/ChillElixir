#!/usr/bin/env python3
"""
강아지 비문 인식 API 배치 테스트 스크립트
test_images 폴더의 모든 이미지를 처리하고 결과를 result 폴더에 저장
"""

import requests
import json
import base64
import io
import os
import time
from pathlib import Path
from datetime import datetime
import itertools

# API 서버 설정
API_BASE_URL = "http://localhost:5000"

# 지원되는 이미지 확장자
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

# 사용할 Siamese 모델들
SIAMESE_MODELS = ['original', 'canny', 'laplacian', 'sobel']

class DogNoseAPITester:
    def __init__(self, api_url=API_BASE_URL):
        self.api_url = api_url
        self.test_results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 결과 저장 디렉토리 설정
        self.result_dir = Path("result")
        self.result_dir.mkdir(exist_ok=True)
        
        self.batch_result_dir = self.result_dir / f"batch_test_{self.timestamp}"
        self.batch_result_dir.mkdir(exist_ok=True)
        
        # 하위 디렉토리 생성
        (self.batch_result_dir / "cropped_images").mkdir(exist_ok=True)
        (self.batch_result_dir / "processed_images").mkdir(exist_ok=True)
        (self.batch_result_dir / "comparison_results").mkdir(exist_ok=True)
        (self.batch_result_dir / "logs").mkdir(exist_ok=True)
        
        print(f"📁 결과 저장 디렉토리: {self.batch_result_dir}")

    def check_server_health(self):
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ 서버 상태 확인 완료!")
                print(f"   - YOLO 모델: {'로드됨' if health_data['yolo_loaded'] else '로드 안됨'}")
                print(f"   - Siamese 모델: {'로드됨' if health_data['siamese_loaded'] else '로드 안됨'}")
                print(f"   - 디바이스: {health_data['device']}")
                print(f"   - 사용 가능한 모델: {health_data['available_siamese_models']}")
                return True
            else:
                print(f"❌ 서버 응답 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {str(e)}")
            return False

    def get_test_images(self):
        """test_images 폴더에서 이미지 파일들 찾기"""
        test_images_dir = Path("test_images")
        if not test_images_dir.exists():
            print("❌ test_images 폴더가 존재하지 않습니다.")
            return []
        
        image_files = []
        for file_path in test_images_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                image_files.append(file_path)
        
        if not image_files:
            print("❌ test_images 폴더에 이미지 파일이 없습니다.")
            print(f"   지원 형식: {', '.join(SUPPORTED_EXTENSIONS)}")
        else:
            print(f"📸 발견된 테스트 이미지: {len(image_files)}개")
            for img in image_files:
                print(f"   - {img.name}")
        
        return sorted(image_files)

    def crop_nose_test(self, image_path):
        """코 크롭 테스트"""
        print(f"🔍 코 크롭 테스트: {image_path.name}")
        
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(f"{self.api_url}/crop_nose", files=files, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # 크롭된 이미지 저장
                cropped_image_data = base64.b64decode(data['cropped_nose'])
                output_path = self.batch_result_dir / "cropped_images" / f"cropped_{image_path.stem}.jpg"
                
                with open(output_path, 'wb') as f:
                    f.write(cropped_image_data)
                
                result = {
                    'success': True,
                    'image_size': data['size'],
                    'cropped_image_path': str(output_path),
                    'processing_time': None
                }
                
                print(f"   ✅ 성공! 크롭 이미지 크기: {data['size']}")
                return result
            else:
                error_msg = response.text
                print(f"   ❌ 실패: {response.status_code} - {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ 오류: {error_msg}")
            return {'success': False, 'error': error_msg}

    def extract_features_test(self, image_path, model_type='original'):
        """특징 추출 테스트"""
        print(f"🔍 특징 추출 테스트: {image_path.name} (모델: {model_type})")
        
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'model_type': model_type}
                response = requests.post(f"{self.api_url}/extract_features", files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result_data = response.json()
                
                result = {
                    'success': True,
                    'model_type': model_type,
                    'feature_size': result_data['feature_size'],
                    'features': result_data['features'][:10],  # 처음 10개만 저장
                    'full_features_length': len(result_data['features'])
                }
                
                print(f"   ✅ 성공! 특징 벡터 크기: {result_data['feature_size']}")
                return result
            else:
                error_msg = response.text
                print(f"   ❌ 실패: {response.status_code} - {error_msg}")
                return {'success': False, 'error': error_msg, 'model_type': model_type}
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ 오류: {error_msg}")
            return {'success': False, 'error': error_msg, 'model_type': model_type}

    def process_full_test(self, image_path, model_type='original'):
        """전체 프로세스 테스트"""
        print(f"🔍 전체 프로세스 테스트: {image_path.name} (모델: {model_type})")
        
        try:
            start_time = time.time()
            
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'model_type': model_type}
                response = requests.post(f"{self.api_url}/process_full", files=files, data=data, timeout=60)
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                # 처리된 이미지 저장
                processed_image_data = base64.b64decode(result_data['cropped_nose'])
                output_path = self.batch_result_dir / "processed_images" / f"processed_{image_path.stem}_{model_type}.jpg"
                
                with open(output_path, 'wb') as f:
                    f.write(processed_image_data)
                
                result = {
                    'success': True,
                    'model_type': model_type,
                    'crop_size': result_data['crop_size'],
                    'feature_size': result_data['feature_size'],
                    'features_sample': result_data['features'][:10],  # 처음 10개만 저장
                    'processed_image_path': str(output_path),
                    'processing_time': round(processing_time, 2)
                }
                
                print(f"   ✅ 성공! 처리 시간: {processing_time:.2f}초")
                return result
            else:
                error_msg = response.text
                print(f"   ❌ 실패: {response.status_code} - {error_msg}")
                return {'success': False, 'error': error_msg, 'model_type': model_type}
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ 오류: {error_msg}")
            return {'success': False, 'error': error_msg, 'model_type': model_type}

    def compare_noses_test(self, image1_path, image2_path, model_type='original'):
        """두 비문 비교 테스트"""
        print(f"🔍 비문 비교 테스트: {image1_path.name} vs {image2_path.name} (모델: {model_type})")
        
        try:
            start_time = time.time()
            
            with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
                files = {'image1': f1, 'image2': f2}
                data = {'model_type': model_type}
                response = requests.post(f"{self.api_url}/compare_noses", files=files, data=data, timeout=60)
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                result = {
                    'success': True,
                    'image1': image1_path.name,
                    'image2': image2_path.name,
                    'model_type': model_type,
                    'similarity': result_data['similarity'],
                    'is_same_dog': result_data['is_same_dog'],
                    'confidence': result_data['confidence'],
                    'processing_time': round(processing_time, 2)
                }
                
                same_status = "같은 개체" if result_data['is_same_dog'] else "다른 개체"
                print(f"   ✅ 성공! 유사도: {result_data['similarity']:.4f}, 판정: {same_status}")
                return result
            else:
                error_msg = response.text
                print(f"   ❌ 실패: {response.status_code} - {error_msg}")
                return {'success': False, 'error': error_msg, 'model_type': model_type}
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ 오류: {error_msg}")
            return {'success': False, 'error': error_msg, 'model_type': model_type}

    def run_batch_tests(self):
        """배치 테스트 실행"""
        print("🐕 강아지 비문 인식 API 배치 테스트 시작")
        print("=" * 60)
        
        # 서버 상태 확인
        if not self.check_server_health():
            return
        
        # 테스트 이미지 수집
        test_images = self.get_test_images()
        if not test_images:
            return
        
        print(f"\n📊 테스트 계획:")
        print(f"   - 테스트 이미지: {len(test_images)}개")
        print(f"   - Siamese 모델: {len(SIAMESE_MODELS)}개")
        print(f"   - 비교 테스트: {len(test_images) * (len(test_images) - 1) // 2}개 조합")
        
        # 각 이미지별 테스트 실행
        for i, image_path in enumerate(test_images, 1):
            print(f"\n🖼️  이미지 {i}/{len(test_images)}: {image_path.name}")
            print("-" * 50)
            
            image_results = {}
            
            # 1. 코 크롭 테스트
            crop_result = self.crop_nose_test(image_path)
            image_results['crop'] = crop_result
            
            # 2. 각 모델별 특징 추출 테스트
            image_results['features'] = {}
            for model in SIAMESE_MODELS:
                feature_result = self.extract_features_test(image_path, model)
                image_results['features'][model] = feature_result
            
            # 3. 각 모델별 전체 프로세스 테스트
            image_results['full_process'] = {}
            for model in SIAMESE_MODELS:
                process_result = self.process_full_test(image_path, model)
                image_results['full_process'][model] = process_result
            
            self.test_results[image_path.name] = image_results
        
        # 이미지간 비교 테스트
        if len(test_images) >= 2:
            print(f"\n🔄 비문 비교 테스트 시작")
            print("-" * 50)
            
            comparison_results = {}
            
            # 모든 이미지 조합에 대해 비교 테스트
            for img1, img2 in itertools.combinations(test_images, 2):
                comparison_key = f"{img1.name}_vs_{img2.name}"
                comparison_results[comparison_key] = {}
                
                for model in SIAMESE_MODELS:
                    compare_result = self.compare_noses_test(img1, img2, model)
                    comparison_results[comparison_key][model] = compare_result
            
            self.test_results['comparisons'] = comparison_results
        
        # 결과 저장
        self.save_results()
        self.generate_report()
        
        print(f"\n🎉 배치 테스트 완료!")
        print(f"📁 결과 저장 위치: {self.batch_result_dir}")

    def save_results(self):
        """테스트 결과를 JSON 파일로 저장"""
        results_file = self.batch_result_dir / "test_results.json"
        
        # 결과 데이터 정리
        summary = {
            'timestamp': self.timestamp,
            'test_info': {
                'total_images': len([k for k in self.test_results.keys() if k != 'comparisons']),
                'models_tested': SIAMESE_MODELS,
                'api_url': self.api_url
            },
            'results': self.test_results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"💾 결과 저장: {results_file}")

    def generate_report(self):
        """테스트 결과 리포트 생성"""
        report_file = self.batch_result_dir / "test_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 강아지 비문 인식 API 테스트 리포트\n\n")
            f.write(f"**테스트 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 테스트 개요
            total_images = len([k for k in self.test_results.keys() if k != 'comparisons'])
            f.write(f"## 📊 테스트 개요\n\n")
            f.write(f"- **총 테스트 이미지**: {total_images}개\n")
            f.write(f"- **테스트 모델**: {', '.join(SIAMESE_MODELS)}\n")
            f.write(f"- **API 서버**: {self.api_url}\n\n")
            
            # 개별 이미지 결과
            f.write(f"## 🖼️ 개별 이미지 테스트 결과\n\n")
            
            for image_name, results in self.test_results.items():
                if image_name == 'comparisons':
                    continue
                    
                f.write(f"### {image_name}\n\n")
                
                # 코 크롭 결과
                crop_result = results.get('crop', {})
                if crop_result.get('success'):
                    f.write(f"- **코 크롭**: ✅ 성공 (크기: {crop_result['image_size']})\n")
                else:
                    f.write(f"- **코 크롭**: ❌ 실패 ({crop_result.get('error', 'Unknown error')})\n")
                
                # 모델별 결과
                f.write(f"- **모델별 특징 추출 결과**:\n")
                for model in SIAMESE_MODELS:
                    feature_result = results.get('features', {}).get(model, {})
                    if feature_result.get('success'):
                        f.write(f"  - {model}: ✅ 성공 (특징 크기: {feature_result['feature_size']})\n")
                    else:
                        f.write(f"  - {model}: ❌ 실패\n")
                
                f.write(f"- **모델별 전체 프로세스 결과**:\n")
                for model in SIAMESE_MODELS:
                    process_result = results.get('full_process', {}).get(model, {})
                    if process_result.get('success'):
                        processing_time = process_result.get('processing_time', 'N/A')
                        f.write(f"  - {model}: ✅ 성공 (처리 시간: {processing_time}초)\n")
                    else:
                        f.write(f"  - {model}: ❌ 실패\n")
                
                f.write(f"\n")
            
            # 비교 테스트 결과
            if 'comparisons' in self.test_results:
                f.write(f"## 🔄 비문 비교 테스트 결과\n\n")
                
                for comparison_key, comparison_results in self.test_results['comparisons'].items():
                    f.write(f"### {comparison_key.replace('_vs_', ' vs ')}\n\n")
                    
                    for model, result in comparison_results.items():
                        if result.get('success'):
                            similarity = result['similarity']
                            is_same = result['is_same_dog']
                            confidence = result['confidence']
                            same_status = "같은 개체" if is_same else "다른 개체"
                            f.write(f"- **{model}**: 유사도 {similarity:.4f} → {same_status} (신뢰도: {confidence})\n")
                        else:
                            f.write(f"- **{model}**: ❌ 실패\n")
                    
                    f.write(f"\n")
        
        print(f"📄 리포트 생성: {report_file}")

def main():
    """메인 실행 함수"""
    tester = DogNoseAPITester()
    tester.run_batch_tests()

if __name__ == "__main__":
    main() 