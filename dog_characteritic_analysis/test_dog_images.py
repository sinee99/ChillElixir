import requests
import base64
import json
import os
from pathlib import Path
from datetime import datetime

class DogImageClassifier:
    def __init__(self):
        """강아지 이미지 분류 테스터"""
        # asd.py에서 가져온 인증 정보
        self.token_url = 'https://www.nyckel.com/connect/token'
        self.client_id = 'iq34c1zbwx18d0939kd6aifur3mwfy75'
        self.client_secret = '5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9'
        self.base_url = 'https://www.nyckel.com/v1'
        
        self.access_token = None
        
        # 생성된 함수 ID들 (이전에 확인된)
        self.functions = {
            'dog-size-classifier': 'function_zqro27bkkoxnt6uz',
            'dog-hair-type-classifier': 'function_toug6vk7pyjo531f', 
            'dog-ear-type-classifier': 'function_63mwhy5mw03ot1a0',
            'dog-snout-type-classifier': 'function_mt2dhgs36kz3nmeg',
            'dog-color-classifier': 'function_mihqjxivj8j6sven',
            'dog-general-classifier': 'function_nj1b1oxqajqwz1ya'
        }
    
    def get_access_token(self):
        """OAuth2 액세스 토큰을 획득합니다."""
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            if self.access_token:
                print("✅ Nyckel API 토큰 획득 성공")
                return True
            else:
                print("❌ 토큰 획득 실패: 응답에 access_token이 없습니다.")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 토큰 획득 중 오류 발생: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON 디코딩 오류: {e}")
            return False
    
    def classify_image(self, image_path, function_id):
        """이미지를 분류합니다."""
        if not self.access_token:
            return None, "토큰이 없습니다."
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # 이미지를 base64로 인코딩
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 이미지 형식 감지
            ext = Path(image_path).suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            else:
                mime_type = 'image/jpeg'  # 기본값
            
            # 분류 요청
            invoke_data = {
                'data': f'data:{mime_type};base64,{image_data}'
            }
            
            response = requests.post(
                f'{self.base_url}/functions/{function_id}/invoke',
                headers=headers,
                json=invoke_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result, None
            else:
                return None, f"분류 실패: {response.status_code} - {response.text}"
                
        except FileNotFoundError:
            return None, f"이미지 파일을 찾을 수 없습니다: {image_path}"
        except Exception as e:
            return None, f"분류 중 오류 발생: {e}"
    
    def test_single_image(self, image_path):
        """단일 이미지를 모든 분류기로 테스트합니다."""
        print(f"\n🖼️  이미지 분석 중: {Path(image_path).name}")
        print("-" * 60)
        
        results = {}
        
        for func_name, func_id in self.functions.items():
            print(f"🔍 {func_name} 분류 중...")
            
            result, error = self.classify_image(image_path, func_id)
            
            if result:
                # 결과 파싱
                if 'labelName' in result:
                    prediction = result['labelName']
                    confidence = result.get('confidence', 0)
                    print(f"   ✅ 결과: {prediction} (신뢰도: {confidence:.2f})")
                    results[func_name] = {
                        'prediction': prediction,
                        'confidence': confidence,
                        'success': True
                    }
                else:
                    print(f"   ⚠️  예상치 못한 응답 형식: {result}")
                    results[func_name] = {
                        'raw_result': result,
                        'success': False,
                        'error': 'Unexpected response format'
                    }
            else:
                print(f"   ❌ 오류: {error}")
                results[func_name] = {
                    'success': False,
                    'error': error
                }
        
        return results
    
    def test_all_images(self, images_dir):
        """모든 이미지를 테스트합니다."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        images_path = Path(images_dir)
        
        if not images_path.exists():
            print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {images_dir}")
            return
        
        # 이미지 파일들 찾기
        image_files = [f for f in images_path.iterdir() 
                      if f.is_file() and f.suffix.lower() in image_extensions]
        
        if not image_files:
            print(f"⚠️  '{images_dir}'에서 이미지 파일을 찾을 수 없습니다.")
            return
        
        print(f"📁 총 {len(image_files)}개의 이미지를 발견했습니다.")
        
        all_results = {}
        
        for image_file in image_files:
            results = self.test_single_image(str(image_file))
            all_results[image_file.name] = results
        
        # 결과 저장
        self.save_results(all_results)
        
        # 요약 출력
        self.print_summary(all_results)
    
    def save_results(self, results):
        """결과를 파일로 저장합니다."""
        # result 폴더 생성
        os.makedirs('result', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 결과 저장
        json_file = f"result/dog_classification_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 상세 결과가 '{json_file}'에 저장되었습니다.")
        
        # 요약 보고서 저장
        report_file = f"result/dog_classification_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🐕 강아지 특징 분류 테스트 결과\n\n")
            f.write(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for image_name, image_results in results.items():
                f.write(f"## 📸 {image_name}\n\n")
                
                for func_name, result in image_results.items():
                    f.write(f"### {func_name}\n")
                    if result.get('success'):
                        prediction = result.get('prediction', 'Unknown')
                        confidence = result.get('confidence', 0)
                        f.write(f"- **예측**: {prediction}\n")
                        f.write(f"- **신뢰도**: {confidence:.2f}\n")
                    else:
                        f.write(f"- **오류**: {result.get('error', 'Unknown error')}\n")
                    f.write("\n")
                
                f.write("---\n\n")
        
        print(f"📋 요약 보고서가 '{report_file}'에 저장되었습니다.")
    
    def print_summary(self, results):
        """결과 요약을 출력합니다."""
        print("\n" + "="*60)
        print("📊 강아지 특징 분류 테스트 요약")
        print("="*60)
        
        total_images = len(results)
        total_classifications = total_images * len(self.functions)
        successful_classifications = 0
        
        for image_results in results.values():
            for result in image_results.values():
                if result.get('success'):
                    successful_classifications += 1
        
        success_rate = (successful_classifications / total_classifications) * 100
        
        print(f"📁 테스트된 이미지 수: {total_images}개")
        print(f"🎯 총 분류 시도: {total_classifications}개")
        print(f"✅ 성공한 분류: {successful_classifications}개")
        print(f"📈 성공률: {success_rate:.1f}%")
        
        # 함수별 성공률
        print(f"\n🔍 함수별 성공률:")
        for func_name in self.functions.keys():
            func_success = sum(1 for img_results in results.values() 
                             if img_results.get(func_name, {}).get('success', False))
            func_rate = (func_success / total_images) * 100
            print(f"   {func_name}: {func_rate:.1f}% ({func_success}/{total_images})")
    
    def run(self):
        """전체 테스트를 실행합니다."""
        print("🐕 강아지 특징 분류 테스트 시작")
        print("="*50)
        
        # 1. 토큰 획득
        if not self.get_access_token():
            print("❌ 토큰 획득에 실패했습니다. 프로그램을 종료합니다.")
            return
        
        # 2. test_images 디렉토리 확인
        test_images_path = "../dog_nose_ai_service/test_images"
        
        if not Path(test_images_path).exists():
            # 현재 디렉토리의 test_images도 확인
            test_images_path = "test_images"
            if not Path(test_images_path).exists():
                print("❌ test_images 폴더를 찾을 수 없습니다.")
                print("💡 다음 경로들을 확인했습니다:")
                print("   - ../dog_nose_ai_service/test_images")
                print("   - ./test_images")
                return
        
        # 3. 이미지 분류 테스트
        print(f"📁 이미지 폴더: {test_images_path}")
        self.test_all_images(test_images_path)
        
        print("\n🎉 모든 테스트가 완료되었습니다!")

def main():
    """메인 함수"""
    classifier = DogImageClassifier()
    classifier.run()

if __name__ == "__main__":
    main() 