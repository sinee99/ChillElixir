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

def upload_image_sample_v2(token, function_id, image_path, label):
    """수정된 형식으로 이미지 샘플을 업로드합니다."""
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
        
        # 다양한 annotation 형식 시도
        annotation_formats = [
            label,  # 문자열
            {"labelName": label},  # 객체 형식 1
            {"label": label},  # 객체 형식 2
            {"name": label},  # 객체 형식 3
        ]
        
        for i, annotation in enumerate(annotation_formats):
            sample_data = {
                'data': f'data:{mime_type};base64,{image_data}',
                'annotation': annotation
            }
            
            print(f"      시도 {i+1}: annotation = {annotation}")
            
            response = requests.post(
                f'https://www.nyckel.com/v1/functions/{function_id}/samples',
                headers=headers,
                json=sample_data
            )
            
            if response.status_code in [200, 201]:
                return True, f"샘플 업로드 성공: {label} (형식 {i+1})"
            else:
                print(f"      실패 {i+1}: {response.status_code} - {response.text[:100]}...")
        
        return False, "모든 annotation 형식 시도 실패"
            
    except Exception as e:
        return False, f"오류 발생: {e}"

def try_simple_approach(token, function_id):
    """간단한 텍스트 라벨 생성을 시도합니다."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 간단한 더미 이미지 (1x1 픽셀)
    dummy_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x7f\x18\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    image_data = base64.b64encode(dummy_png).decode('utf-8')
    
    # 간단한 텍스트 라벨들 시도
    labels = ["label1", "label2"]
    
    for label in labels:
        print(f"   간단한 라벨 '{label}' 시도 중...")
        
        sample_data = {
            'data': f'data:image/png;base64,{image_data}',
            'annotation': label
        }
        
        response = requests.post(
            f'https://www.nyckel.com/v1/functions/{function_id}/samples',
            headers=headers,
            json=sample_data
        )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ 성공: {label}")
            return True
        else:
            print(f"   ❌ 실패: {response.status_code} - {response.text[:100]}...")
    
    return False

def main():
    """메인 함수"""
    print("🐕 수정된 방식으로 샘플 업로드 시도")
    print("="*50)
    
    # 토큰 획득
    token = get_access_token()
    if not token:
        return
    
    # 테스트할 함수 (하나만)
    function_id = 'function_zqro27bkkoxnt6uz'  # dog-size-classifier
    function_name = 'dog-size-classifier'
    
    print(f"\n🏷️  '{function_name}' 함수에 간단한 라벨 생성 시도...")
    
    # 먼저 간단한 방법 시도
    if try_simple_approach(token, function_id):
        print("✅ 간단한 라벨 생성 성공!")
    else:
        print("❌ 간단한 라벨 생성도 실패")
        
        # 실제 이미지로 시도
        test_images_path = Path("../dog_nose_ai_service/test_images")
        if not test_images_path.exists():
            test_images_path = Path("test_images")
        
        if test_images_path.exists():
            image_files = [f for f in test_images_path.iterdir() 
                          if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
            
            if image_files:
                print(f"\n실제 강아지 이미지로 재시도: {image_files[0].name}")
                success, message = upload_image_sample_v2(token, function_id, str(image_files[0]), "test_label")
                print(f"결과: {message}")
    
    print("\n💡 Nyckel 계정의 제한이나 설정 문제일 수 있습니다.")
    print("   웹사이트에서 직접 라벨을 추가해보세요: https://www.nyckel.com")

if __name__ == "__main__":
    main() 