import nyckel
import requests
import base64
import os

print("🐕 Nyckel 사전 훈련된 분류기 테스트")

# Nyckel 계정 설정
credentials = nyckel.Credentials("iq34c1zbwx18d0939kd6aifur3mwfy75", "5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9")

print("\n방법 1: 공개 웹 URL 사용")
# 개 이미지 공개 URL들
test_urls = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/1024px-Collage_of_Nine_Dogs.jpg",
    "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500",
    "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=500"
]

for i, url in enumerate(test_urls, 1):
    try:
        print(f"\n🌐 테스트 {i}: {url[:50]}...")
        result = nyckel.invoke("dog-color", url, credentials)
        print(f"✅ 결과: {result}")
        break  # 성공하면 중단
    except Exception as e:
        print(f"❌ 실패: {e}")

print("\n" + "="*60)
print("방법 2: 로컬 이미지를 Data URI로 변환")

# 로컬 이미지 파일들
local_files = [
    "../dog_nose_ai_service/test_images/n02088094_392.jpg",
    "dog_image.jpg"
]

for file_path in local_files:
    if os.path.exists(file_path):
        print(f"\n📁 파일: {file_path}")
        try:
            # 이미지를 base64로 인코딩
            with open(file_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Data URI 생성
            data_uri = f"data:image/jpeg;base64,{encoded_string}"
            print(f"🔗 Data URI 길이: {len(data_uri)} 문자")
            
            # 분류 시도
            result = nyckel.invoke("dog-color", data_uri, credentials)
            print(f"✅ 결과: {result}")
            break
            
        except Exception as e:
            print(f"❌ 실패: {e}")
    else:
        print(f"❌ 파일 없음: {file_path}")

print("\n" + "="*60)
print("방법 3: 사용 가능한 사전 훈련된 분류기 확인")

# 다른 사전 훈련된 분류기들도 테스트
pretrained_classifiers = [
    "dog-color",
    "dog-breed", 
    "animal",
    "pet",
    "image-classification"
]

test_url = "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500"
print(f"🎯 테스트 URL: {test_url}")

for classifier in pretrained_classifiers:
    try:
        print(f"\n🤖 {classifier} 분류기 테스트...")
        result = nyckel.invoke(classifier, test_url, credentials)
        print(f"✅ {classifier}: {result}")
    except Exception as e:
        print(f"❌ {classifier}: {e}") 