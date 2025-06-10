import requests
import base64
import os

print("🌐 Nyckel API 직접 호출 테스트")

# 토큰 획득
print("1️⃣ API 토큰 획득 중...")
token_url = 'https://www.nyckel.com/connect/token'
data = {
    'grant_type': 'client_credentials', 
    'client_id': 'iq34c1zbwx18d0939kd6aifur3mwfy75', 
    'client_secret': '5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9'
}

token_response = requests.post(token_url, data=data)
print(f"토큰 응답 상태: {token_response.status_code}")

if token_response.status_code == 200:
    token = token_response.json()['access_token']
    print("✅ API 토큰 획득 성공")
    
    # 이미지 파일 경로들
    image_paths = [
        "dog_image.jpg",
        r"D:\USER FILE\Documents\VSCODE\LostPet\dog_nose_ai_service\test_images\n02088094_392.jpg"
    ]
    
    for image_path in image_paths:
        if os.path.exists(image_path):
            print(f"\n2️⃣ 이미지 파일 처리 중: {os.path.basename(image_path)}")
            
            try:
                # 이미지를 base64로 인코딩
                with open(image_path, 'rb') as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                print(f"✅ 이미지 base64 인코딩 완료 (크기: {len(image_data)} 문자)")
                
                # API 직접 호출
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                invoke_data = {
                    'data': f'data:image/jpeg;base64,{image_data}'
                }
                
                # 각 분류 함수별로 테스트
                functions = {
                    'dog-color': 'function_mihqjxivj8j6sven',
                    'dog-size': 'function_zqro27bkkoxnt6uz', 
                    'dog-hair-type': 'function_toug6vk7pyjo531f'
                }
                
                for func_name, func_id in functions.items():
                    print(f"\n3️⃣ {func_name} 분류 시도...")
                    
                    response = requests.post(
                        f'https://www.nyckel.com/v1/functions/{func_id}/invoke',
                        headers=headers,
                        json=invoke_data
                    )
                    
                    print(f"응답 상태: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ {func_name} 분류 결과: {result}")
                    else:
                        print(f"❌ {func_name} 분류 실패: {response.text}")
                
                break  # 첫 번째 성공한 파일로만 테스트
                
            except Exception as e:
                print(f"❌ 이미지 처리 오류: {e}")
        else:
            print(f"❌ 파일 없음: {image_path}")
else:
    print(f"❌ 토큰 획득 실패: {token_response.text}") 