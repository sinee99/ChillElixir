import nyckel
import os

print("🔍 현재 디렉토리 파일들:")
for file in os.listdir("."):
    if file.endswith(('.jpg', '.jpeg', '.png')):
        print(f"   📸 {file}")

# Nyckel 계정 설정
credentials = nyckel.Credentials("iq34c1zbwx18d0939kd6aifur3mwfy75", "5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9")

# 간단한 파일명으로 시도
if os.path.exists("dog_image.jpg"):
    print(f"\n🤖 간단한 파일명으로 분류 시도: dog_image.jpg")
    try:
        result = nyckel.invoke("dog-color", "dog_image.jpg", credentials)
        print("✅ 분류 결과:")
        print(result)
    except Exception as e:
        print(f"❌ 오류: {e}")
else:
    print("❌ dog_image.jpg 파일이 없습니다.")
    
    # 원본 파일로 다시 시도 (절대경로)
    original_path = r"D:\USER FILE\Documents\VSCODE\LostPet\dog_nose_ai_service\test_images\n02088094_392.jpg"
    if os.path.exists(original_path):
        print(f"\n🤖 원본 파일로 시도...")
        try:
            # 문제가 있을 수 있는 함수명 대신 다른 함수로 시도
            result = nyckel.invoke("function_mihqjxivj8j6sven", original_path, credentials)
            print("✅ 분류 결과 (함수 ID 사용):")
            print(result)
        except Exception as e:
            print(f"❌ 함수 ID 사용 실패: {e}")
            
            # HTTP URL 방식 시도
            print(f"\n💡 nyckel 라이브러리 대신 직접 API 호출 시도...")
            import requests
            import base64
            
            # 토큰 획득
            token_url = 'https://www.nyckel.com/connect/token'
            data = {'grant_type': 'client_credentials', 'client_id': 'iq34c1zbwx18d0939kd6aifur3mwfy75', 'client_secret': '5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9'}
            
            token_response = requests.post(token_url, data=data)
            if token_response.status_code == 200:
                token = token_response.json()['access_token']
                print("✅ API 토큰 획득 성공")
                
                # 이미지를 base64로 인코딩
                with open(original_path, 'rb') as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
                # API 직접 호출
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                invoke_data = {
                    'data': f'data:image/jpeg;base64,{image_data}'
                }
                
                # dog-color-classifier 함수 ID로 호출
                function_id = 'function_mihqjxivj8j6sven'
                response = requests.post(
                    f'https://www.nyckel.com/v1/functions/{function_id}/invoke',
                    headers=headers,
                    json=invoke_data
                )
                
                print(f"API 응답 상태: {response.status_code}")
                print(f"API 응답 내용: {response.text}")
            else:
                print(f"❌ 토큰 획득 실패: {token_response.text}")
    else:
        print("❌ 원본 파일도 찾을 수 없습니다.") 