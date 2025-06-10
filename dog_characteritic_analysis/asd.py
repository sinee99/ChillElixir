import requests
"""
token_url = 'https://www.nyckel.com/connect/token'
data = {'grant_type': 'client_credentials', 'client_id': 'iq34c1zbwx18d0939kd6aifur3mwfy75', 'client_secret': '5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9'}

result = requests.post(token_url, data = data)
print(result.text)
"""
import nyckel
import os

# Nyckel 계정에서 발급받은 API 키 입력
credentials = nyckel.Credentials("iq34c1zbwx18d0939kd6aifur3mwfy75", "5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9")

# 여러 경로 시도
possible_paths = [
    "../dog_nose_ai_service/test_images/n02088094_392.jpg",
    "test_images/n02088094_392.jpg",
    "../dog_nose_ai_service/test_images/n02088094_649.jpg",
    "test_images/n02088094_649.jpg"
]

print("🔍 파일 경로 확인 중...")
for path in possible_paths:
    print(f"   {path}: {'✅ 존재' if os.path.exists(path) else '❌ 없음'}")

# 존재하는 첫 번째 파일 찾기
found_file = None
for path in possible_paths:
    if os.path.exists(path):
        found_file = path
        break

if found_file:
    # 절대경로로 변환
    absolute_path = os.path.abspath(found_file)
    print(f"\n📁 사용할 파일:")
    print(f"   상대경로: {found_file}")
    print(f"   절대경로: {absolute_path}")
    
    try:
        # 절대경로로 시도
        print(f"\n🤖 절대경로로 분류 시도...")
        result = nyckel.invoke("dog-color", absolute_path, credentials)
        print("분류 결과 (절대경로):")
        print(result)
    except Exception as e:
        print(f"❌ 절대경로 실패: {e}")
        
        # 상대경로로 재시도
        try:
            print(f"\n🤖 상대경로로 분류 재시도...")
            result = nyckel.invoke("dog-color", found_file, credentials)
            print("분류 결과 (상대경로):")
            print(result)
        except Exception as e2:
            print(f"❌ 상대경로도 실패: {e2}")
            
            # URL 형식으로 시도
            print(f"\n🤖 file:// URL 형식으로 시도...")
            file_url = f"file:///{absolute_path.replace(os.sep, '/')}"
            print(f"   URL: {file_url}")
            result = nyckel.invoke("dog-color", file_url, credentials)
            print("분류 결과 (URL):")
            print(result)
else:
    print("❌ 이미지 파일을 찾을 수 없습니다.")
    
    # 현재 디렉토리 확인
    print("\n📁 현재 디렉토리 내용:")
    for item in os.listdir("."):
        item_path = os.path.join(".", item)
        if os.path.isfile(item_path):
            print(f"   📄 {item}")
        elif os.path.isdir(item_path):
            print(f"   📁 {item}/")
            # test_images 폴더가 있다면 내용도 확인
            if item == "test_images":
                try:
                    test_files = os.listdir(item_path)
                    for test_file in test_files:
                        print(f"      📄 {test_file}")
                except:
                    pass
