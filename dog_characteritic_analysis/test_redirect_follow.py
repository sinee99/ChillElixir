import nyckel
import requests

print("🐕 Google Drive 리다이렉트 추적하여 Nyckel 테스트")

# Nyckel 계정 설정
credentials = nyckel.Credentials("iq34c1zbwx18d0939kd6aifur3mwfy75", "5zxo5xdzbs581opp4sl3zeqza8d8f2vypv2d2kxc6evid7s2ewsnc36r9xdxj4k9")

file_id = "16uuvfPmThFHa1_NoyVNv8n9ic6HK5C0C"

# 다양한 URL 형식 시도
urls_to_try = [
    f"https://drive.google.com/uc?id={file_id}",
    f"https://drive.google.com/uc?export=download&id={file_id}",
    f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000",
    f"https://lh3.googleusercontent.com/d/{file_id}=w1000"
]

print("🌐 리다이렉트를 허용하여 실제 이미지 URL 찾기...")

for i, url in enumerate(urls_to_try, 1):
    print(f"\n{'='*50}")
    print(f"🔗 시도 {i}: {url}")
    
    try:
        # 리다이렉트를 따라가면서 최종 URL 찾기
        session = requests.Session()
        response = session.get(url, allow_redirects=True, timeout=15)
        
        print(f"📊 최종 상태: {response.status_code}")
        print(f"📍 최종 URL: {response.url}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"📏 Content-Length: {response.headers.get('content-length', 'Unknown')}")
        
        # 이미지인지 확인
        content_type = response.headers.get('content-type', '').lower()
        if response.status_code == 200 and ('image' in content_type):
            print(f"✅ 이미지 파일 발견!")
            
            # Nyckel로 분류 시도
            print(f"🤖 Nyckel dog-color 분류 시도...")
            final_url = response.url
            
            try:
                result = nyckel.invoke("dog-color", final_url, credentials)
                print(f"🎉 성공! 분류 결과: {result}")
                
                # 다른 분류기들도 시도
                print(f"\n🔄 다른 분류기들 시도...")
                other_classifiers = ["dog-breed", "animal", "pet"]
                
                for classifier in other_classifiers:
                    try:
                        result2 = nyckel.invoke(classifier, final_url, credentials)
                        print(f"✅ {classifier}: {result2}")
                    except Exception as e:
                        print(f"❌ {classifier}: {e}")
                
                break  # 성공하면 중단
                
            except Exception as e:
                print(f"❌ Nyckel 분류 실패: {e}")
                
        elif response.status_code == 200:
            print(f"⚠️ 파일을 찾았지만 이미지가 아님")
            # 응답 내용의 일부 출력 (HTML인지 확인)
            content_preview = response.text[:200] if hasattr(response, 'text') else str(response.content[:200])
            print(f"내용 미리보기: {content_preview}...")
            
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

print(f"\n{'='*60}")
print("💡 대안 방법:")
print("1. Google Drive 파일을 '링크가 있는 모든 사용자가 볼 수 있음'으로 설정")
print("2. 다른 이미지 호스팅 서비스 사용 (Imgur, ImageBB 등)")
print("3. 공개 웹사이트에 이미지 업로드")

# 대안으로 공개 개 이미지로 테스트
print(f"\n🔄 대안: 공개 개 이미지로 테스트")
public_dog_urls = [
    "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500",
    "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=500"
]

for test_url in public_dog_urls:
    try:
        print(f"\n🌐 테스트 URL: {test_url}")
        result = nyckel.invoke("dog-color", test_url, credentials)
        print(f"✅ dog-color 결과: {result}")
        break
    except Exception as e:
        print(f"❌ 실패: {e}") 