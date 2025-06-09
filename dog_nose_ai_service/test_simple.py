#!/usr/bin/env python3
"""
간단한 테스트 서버 확인용 스크립트
"""

import requests
import json

def test_simple_server():
    """간단한 서버 테스트"""
    base_url = "http://localhost:5001"
    
    print("🐕 간단한 테스트 서버 확인")
    print("=" * 40)
    
    # 1. 헬스 체크
    print("\n🔍 헬스 체크...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 상태: {data.get('status')}")
            print(f"   💬 메시지: {data.get('message')}")
            print(f"   💻 디바이스: {data.get('device')}")
            print(f"   📁 발견된 모델들:")
            for model, exists in data.get('models_found', {}).items():
                status = "✅" if exists else "❌"
                print(f"      {status} {model}")
        else:
            print(f"   ❌ 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 2. 모델 목록 확인
    print("\n📁 모델 파일 목록...")
    try:
        response = requests.get(f"{base_url}/models")
        if response.status_code == 200:
            data = response.json()
            print(f"   📂 모델 디렉토리: {data.get('models_directory')}")
            print(f"   📊 총 파일 수: {data.get('total_files')}")
            print(f"   📄 모델 파일들:")
            for model_file in data.get('model_files', []):
                print(f"      📄 {model_file}")
        else:
            print(f"   ❌ 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 3. 테스트 엔드포인트
    print("\n🧪 테스트 엔드포인트...")
    try:
        response = requests.get(f"{base_url}/test")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data.get('message')}")
            print(f"   📋 사용 가능한 엔드포인트:")
            for endpoint in data.get('endpoints', []):
                print(f"      - {endpoint}")
        else:
            print(f"   ❌ 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    print(f"\n🎉 테스트 완료!")
    print(f"💡 실제 AI 기능을 사용하려면 'python app.py'를 실행하세요.")

if __name__ == "__main__":
    test_simple_server() 