import nyckel
import requests

print("🐕 Google Drive 이미지로 Nyckel dog-color 테스트")

# Nyckel 계정 설정
credentials = nyckel.Credentials("iq34c1zbwx18d0939kd6aifur3mwfy75", "5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9")

# 원본 Google Drive 링크
original_link = "https://drive.google.com/file/d/16uuvfPmThFHa1_NoyVNv8n9ic6HK5C0C/view?usp=drive_link"
print(f"📁 원본 링크: {original_link}")

# Google Drive 파일 ID 추출
file_id = "16uuvfPmThFHa1_NoyVNv8n9ic6HK5C0C"
print(f"🆔 파일 ID: {file_id}")

# 직접 접근 가능한 URL들 생성
direct_urls = [
    f"https://drive.google.com/uc?id={file_id}",
    f"https://drive.google.com/uc?export=view&id={file_id}",
    f"https://drive.google.com/uc?export=download&id={file_id}",
    f"https://lh3.googleusercontent.com/d/{file_id}"
]

print(f"\n🔗 변환된 직접 URL들:")
for i, url in enumerate(direct_urls, 1):
    print(f"   {i}. {url}")

# 각 URL로 테스트
for i, url in enumerate(direct_urls, 1):
    print(f"\n{'='*60}")
    print(f"🌐 테스트 {i}: Google Drive URL 방식 {i}")
    print(f"URL: {url}")
    
    try:
        # 먼저 URL이 접근 가능한지 확인
        print("🔍 URL 접근성 확인 중...")
        response = requests.head(url, timeout=10)
        print(f"   HTTP 상태: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("✅ URL 접근 가능!")
            
            # Nyckel dog-color 분류 시도
            print("🤖 Nyckel dog-color 분류 시도...")
            result = nyckel.invoke("dog-color", url, credentials)
            print(f"🎉 분류 성공!")
            print(f"결과: {result}")
            
            # 성공하면 다른 사전 훈련된 분류기들도 테스트
            print(f"\n🔄 다른 분류기들도 테스트...")
            other_classifiers = ["dog-breed", "animal", "pet"]
            
            for classifier in other_classifiers:
                try:
                    result2 = nyckel.invoke(classifier, url, credentials)
                    print(f"✅ {classifier}: {result2}")
                except Exception as e:
                    print(f"❌ {classifier}: {e}")
            
            break  # 성공한 URL 발견하면 중단
            
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ URL 접근 실패: {e}")
    except Exception as e:
        print(f"❌ Nyckel 분류 실패: {e}")

print(f"\n{'='*60}")
print("💡 참고사항:")
print("- Google Drive 파일은 공개 설정이어야 직접 URL로 접근 가능합니다")
print("- '링크가 있는 모든 사용자가 볼 수 있음'으로 설정되어 있는지 확인하세요")
print("- 일부 URL 형식이 작동하지 않을 수 있습니다") 