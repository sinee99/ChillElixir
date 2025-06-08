#!/usr/bin/env python3
"""
강아지 분석 API 테스트 스크립트
"""

import requests
import json
import os
import time
from pathlib import Path

class DogAnalysisAPITester:
    def __init__(self, api_base_url="http://localhost:8000"):
        """
        API 테스터 초기화
        
        Args:
            api_base_url (str): API 서버 주소
        """
        self.api_base_url = api_base_url
        self.test_images_dir = Path("test_images")
        
    def test_health_check(self):
        """헬스 체크 테스트"""
        print("=" * 50)
        print("🔍 헬스 체크 테스트")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.api_base_url}/health")
            if response.status_code == 200:
                print("✅ 서버 상태: 정상")
                print(f"📄 응답: {response.json()}")
            else:
                print(f"❌ 서버 상태 확인 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {str(e)}")
            return False
        
        return True
    
    def test_model_info(self):
        """모델 정보 조회 테스트"""
        print("\n" + "=" * 50)
        print("🤖 모델 정보 조회 테스트")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.api_base_url}/model-info")
            if response.status_code == 200:
                model_info = response.json()
                print("✅ 모델 정보 조회 성공")
                print(f"📍 모델 경로: {model_info.get('model_path', 'N/A')}")
                print(f"🔧 모델 타입: {model_info.get('model_type', 'N/A')}")
                print(f"📊 신뢰도 임계값: {model_info.get('confidence_threshold', 'N/A')}")
                print(f"🐕 지원 클래스 수: {len(model_info.get('supported_classes', {}))}")
                
                # 지원 클래스 출력
                print("\n📋 지원하는 강아지 품종:")
                for class_id, class_name in model_info.get('supported_classes', {}).items():
                    print(f"  {class_id}: {class_name}")
                    
            else:
                print(f"❌ 모델 정보 조회 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 모델 정보 조회 중 오류: {str(e)}")
            return False
            
        return True
    
    def test_image_analysis(self, image_path):
        """
        이미지 분석 테스트
        
        Args:
            image_path (str): 테스트할 이미지 경로
        """
        print(f"\n" + "=" * 50)
        print(f"📸 이미지 분석 테스트: {os.path.basename(image_path)}")
        print("=" * 50)
        
        if not os.path.exists(image_path):
            print(f"❌ 이미지 파일이 존재하지 않습니다: {image_path}")
            return False
        
        try:
            # 이미지 파일 열기
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': (os.path.basename(image_path), image_file, 'image/jpeg')
                }
                
                print("🚀 이미지 업로드 중...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.api_base_url}/analyze",
                    files=files
                )
                
                analysis_time = time.time() - start_time
                print(f"⏱️ 분석 시간: {analysis_time:.2f}초")
                
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    print("✅ 이미지 분석 성공!")
                    print(f"📁 파일명: {result.get('filename')}")
                    print(f"🐕 예측 품종: {result.get('predicted_breed')}")
                    print(f"📊 신뢰도: {result.get('confidence_score')}")
                    print(f"🕐 분석 시각: {result.get('timestamp')}")
                    
                    # 모든 예측 결과 출력
                    print("\n📋 모든 예측 결과:")
                    all_predictions = result.get('all_predictions', {})
                    all_confidence = result.get('all_confidence_scores', {})
                    
                    for class_id in all_predictions:
                        breed = all_predictions[class_id]
                        confidence = all_confidence.get(class_id, 0)
                        print(f"  {breed}: {confidence:.3f}")
                        
                else:
                    print(f"⚠️ 분석 실패: {result.get('message', '알 수 없는 오류')}")
                    
            else:
                print(f"❌ API 요청 실패: {response.status_code}")
                print(f"📄 에러 메시지: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 이미지 분석 중 오류: {str(e)}")
            return False
            
        return True
    
    def test_recent_analyses(self):
        """최근 분석 결과 조회 테스트"""
        print(f"\n" + "=" * 50)
        print("📊 최근 분석 결과 조회 테스트")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.api_base_url}/recent-analyses?limit=5")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    analyses = result.get('analyses', [])
                    count = result.get('count', 0)
                    
                    print(f"✅ 최근 분석 결과 조회 성공 (총 {count}개)")
                    
                    if count > 0:
                        print("\n📋 최근 분석 결과:")
                        for i, analysis in enumerate(analyses, 1):
                            print(f"\n  {i}. 파일: {analysis.get('image_filename', 'N/A')}")
                            print(f"     품종: {analysis.get('predicted_breed', 'N/A')}")
                            print(f"     신뢰도: {analysis.get('confidence_score', 'N/A')}")
                            print(f"     분석시각: {analysis.get('analysis_timestamp', 'N/A')}")
                    else:
                        print("📭 저장된 분석 결과가 없습니다.")
                else:
                    print("❌ 분석 결과 조회 실패")
                    
            else:
                print(f"❌ API 요청 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 분석 결과 조회 중 오류: {str(e)}")
            return False
            
        return True
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 강아지 분석 API 테스트 시작")
        print("=" * 70)
        
        # 1. 헬스 체크
        if not self.test_health_check():
            print("❌ 헬스 체크 실패. 테스트를 중단합니다.")
            return
        
        # 2. 모델 정보 조회
        if not self.test_model_info():
            print("⚠️ 모델 정보 조회 실패. 계속 진행합니다.")
        
        # 3. 이미지 분석 테스트
        print(f"\n🔍 테스트 이미지 디렉토리: {self.test_images_dir}")
        
        if self.test_images_dir.exists():
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                image_files.extend(self.test_images_dir.glob(ext))
            
            if image_files:
                print(f"📁 발견된 이미지 파일: {len(image_files)}개")
                
                for image_path in image_files:
                    success = self.test_image_analysis(str(image_path))
                    if success:
                        time.sleep(1)  # API 호출 간격
                    
            else:
                print("❌ 테스트할 이미지 파일을 찾을 수 없습니다.")
        else:
            print(f"❌ 테스트 이미지 디렉토리가 존재하지 않습니다: {self.test_images_dir}")
        
        # 4. 최근 분석 결과 조회
        self.test_recent_analyses()
        
        print(f"\n" + "=" * 70)
        print("🎉 모든 테스트 완료!")
        print("=" * 70)

def main():
    """메인 함수"""
    import sys
    
    # API 서버 주소 설정
    api_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    print(f"🎯 테스트 대상 API: {api_url}")
    
    # 테스터 생성 및 실행
    tester = DogAnalysisAPITester(api_url)
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 