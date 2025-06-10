#!/usr/bin/env python3
"""
테스트용 강아지 이미지 설정 스크립트
"""

import requests
from pathlib import Path
import shutil

def create_sample_readme():
    """test_images 폴더에 README 파일 생성"""
    test_images_dir = Path("test_images")
    readme_file = test_images_dir / "README.md"
    
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("""# 테스트 이미지 폴더

이 폴더에 강아지 사진들을 넣어주세요.

## 지원 형식
- JPG/JPEG
- PNG
- BMP
- TIFF
- WEBP

## 권장 사항
- 강아지의 얼굴이 선명하게 보이는 이미지
- 코 부분이 잘 보이는 정면 또는 측면 사진
- 해상도: 최소 200x200 픽셀 이상
- 파일 크기: 50MB 이하

## 테스트 파일 명명 규칙
- `dog1.jpg`, `dog2.jpg` 등으로 명명하면 테스트 결과에서 구분하기 쉽습니다.
- 같은 강아지의 다른 사진들은 `dog1_a.jpg`, `dog1_b.jpg` 등으로 명명하세요.

## 사용법
1. 이 폴더에 강아지 이미지들을 복사합니다.
2. `python batch_test_api.py` 명령어를 실행합니다.
3. `result` 폴더에서 테스트 결과를 확인합니다.
""")
    
    print(f"📄 README 파일 생성: {readme_file}")

def setup_test_environment():
    """테스트 환경 설정"""
    print("🔧 테스트 환경 설정 중...")
    
    # 필요한 폴더들 생성
    folders = ["test_images", "result"]
    for folder in folders:
        folder_path = Path(folder)
        folder_path.mkdir(exist_ok=True)
        print(f"📁 폴더 생성/확인: {folder}")
    
    # test_images 폴더에 README 생성
    create_sample_readme()
    
    print("\n✅ 테스트 환경 설정 완료!")
    print("\n📝 다음 단계:")
    print("1. test_images 폴더에 강아지 사진들을 넣어주세요")
    print("2. Docker 서비스를 실행하세요: docker-compose up -d --build")
    print("3. 배치 테스트를 실행하세요: python batch_test_api.py")
    print("4. result 폴더에서 결과를 확인하세요")

def create_test_curl_commands():
    """테스트용 curl 명령어 파일 생성"""
    commands_file = Path("test_commands.sh")
    
    with open(commands_file, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
# 강아지 비문 인식 API 테스트 명령어들

echo "🔍 서버 상태 확인"
curl -X GET http://localhost:5000/health | jq

echo -e "\n🔍 모델 목록 조회"
curl -X GET http://localhost:5000/models | jq

echo -e "\n🔍 모델 전환 테스트 (canny 모델로 변경)"
curl -X POST -H "Content-Type: application/json" -d '{"model_type": "canny"}' http://localhost:5000/switch_model | jq

# 이미지가 있는 경우의 테스트 명령어들 (주석 해제하여 사용)
# echo -e "\n🔍 코 크롭 테스트"
# curl -X POST -F "image=@test_images/dog1.jpg" http://localhost:5000/crop_nose | jq

# echo -e "\n🔍 특징 추출 테스트"
# curl -X POST -F "image=@test_images/dog1.jpg" -F "model_type=original" http://localhost:5000/extract_features | jq

# echo -e "\n🔍 전체 프로세스 테스트"
# curl -X POST -F "image=@test_images/dog1.jpg" -F "model_type=canny" http://localhost:5000/process_full | jq

# echo -e "\n🔍 비문 비교 테스트"
# curl -X POST -F "image1=@test_images/dog1.jpg" -F "image2=@test_images/dog2.jpg" -F "model_type=original" http://localhost:5000/compare_noses | jq
""")
    
    # 실행 권한 부여 (Unix 계열 시스템)
    try:
        commands_file.chmod(0o755)
    except:
        pass  # Windows에서는 무시
    
    print(f"📄 테스트 명령어 파일 생성: {commands_file}")

def main():
    """메인 함수"""
    print("🐕 강아지 비문 인식 API 테스트 환경 설정")
    print("=" * 50)
    
    setup_test_environment()
    create_test_curl_commands()
    
    print(f"\n🎯 테스트 실행 방법:")
    print(f"1. Python 스크립트: python batch_test_api.py")
    print(f"2. 개별 API 테스트: python test_api.py")
    print(f"3. curl 명령어: bash test_commands.sh (Linux/Mac)")

if __name__ == "__main__":
    main() 