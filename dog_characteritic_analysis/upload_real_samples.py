import requests
import base64
import json
from pathlib import Path

def get_access_token():
    """OAuth2 액세스 토큰을 획득합니다."""
    token_url = 'https://www.nyckel.com/connect/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': 'iq34c1zbwx18d0939kd6aifur3mwfy75',
        'client_secret': '5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9'
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token = response.json()['access_token']
        print("✅ 토큰 획득 성공")
        return token
    except Exception as e:
        print(f"❌ 토큰 획득 실패: {e}")
        return None

def upload_image_sample(token, function_id, image_path, label):
    """이미지 샘플을 함수에 업로드합니다."""
    headers = {
        'Authorization': f'Bearer {token}',
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
            mime_type = 'image/jpeg'
        
        # 샘플 데이터
        sample_data = {
            'data': f'data:{mime_type};base64,{image_data}',
            'annotation': label
        }
        
        response = requests.post(
            f'https://www.nyckel.com/v1/functions/{function_id}/samples',
            headers=headers,
            json=sample_data
        )
        
        if response.status_code in [200, 201]:
            return True, f"샘플 업로드 성공: {label}"
        else:
            return False, f"업로드 실패: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"오류 발생: {e}"

def main():
    """메인 함수"""
    print("🐕 실제 강아지 이미지로 샘플 업로드 시작")
    print("="*50)
    
    # 토큰 획득
    token = get_access_token()
    if not token:
        return
    
    # 생성된 함수들
    functions = {
        'dog-size-classifier': 'function_zqro27bkkoxnt6uz',
        'dog-ear-type-classifier': 'function_63mwhy5mw03ot1a0',
    }
    
    # test_images 경로 확인
    test_images_path = Path("../dog_nose_ai_service/test_images")
    if not test_images_path.exists():
        test_images_path = Path("test_images")
        if not test_images_path.exists():
            print("❌ test_images 폴더를 찾을 수 없습니다.")
            return
    
    # 이미지 파일들 찾기
    image_files = [f for f in test_images_path.iterdir() 
                   if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
    
    if not image_files:
        print("❌ 이미지 파일을 찾을 수 없습니다.")
        return
    
    print(f"📁 발견된 이미지: {len(image_files)}개")
    
    # 각 함수에 샘플 업로드
    for func_name, func_id in functions.items():
        print(f"\n🏷️  '{func_name}' 함수에 샘플 업로드 중...")
        
        if func_name == 'dog-size-classifier':
            # 첫 번째 이미지는 중형견, 두 번째는 대형견으로 라벨링
            labels = ['중형견', '대형견']
        elif func_name == 'dog-ear-type-classifier':
            # 첫 번째는 서있는귀, 두 번째는 늘어진귀로 라벨링
            labels = ['서있는귀', '늘어진귀']
        else:
            labels = ['라벨1', '라벨2']  # 기본 라벨
        
        for i, image_file in enumerate(image_files[:2]):  # 최대 2개 이미지만
            if i < len(labels):
                label = labels[i]
                print(f"   📤 {image_file.name} -> '{label}' 업로드 중...")
                
                success, message = upload_image_sample(token, func_id, str(image_file), label)
                
                if success:
                    print(f"      ✅ {message}")
                else:
                    print(f"      ❌ {message}")
    
    print("\n🎉 샘플 업로드 완료!")
    print("\n💡 이제 다시 분류 테스트를 실행해보세요:")
    print("   python test_dog_images.py")

if __name__ == "__main__":
    main() 