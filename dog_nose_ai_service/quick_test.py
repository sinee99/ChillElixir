#!/usr/bin/env python3
"""
간단한 API 테스트 스크립트
"""

import requests
import json

def test_health():
    """헬스 체크 테스트"""
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"🔍 헬스 체크 결과:")
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 서비스 상태: {data.get('status')}")
            print(f"   YOLO 모델: {data.get('yolo_loaded')}")
            print(f"   Siamese 모델: {data.get('siamese_loaded')}")
            print(f"   디바이스: {data.get('device')}")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("Flask 서버가 실행 중인지 확인하세요!")

def test_models():
    """모델 정보 확인"""
    try:
        response = requests.get("http://localhost:5000/models")
        print(f"\n🤖 모델 정보:")
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   YOLO 사용 가능: {data.get('yolo_available')}")
            siamese_info = data.get('siamese_models', {})
            print(f"   사용 가능한 Siamese 모델: {siamese_info.get('available')}")
            print(f"   현재 Siamese 모델: {siamese_info.get('current')}")
            print(f"   총 모델 수: {data.get('total_models')}")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    print("🐕 강아지 비문 인식 AI 서비스 테스트")
    print("=" * 40)
    
    test_health()
    test_models()
    
    print("\n📋 다음 단계:")
    print("1. 강아지 이미지 준비")
    print("2. 테스트 이미지로 API 호출")
    print("3. http://localhost:5000/health 브라우저에서 확인") 