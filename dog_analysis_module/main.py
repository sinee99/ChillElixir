#!/usr/bin/env python3
"""
강아지 특성 분석 모듈 메인 실행 파일
"""

import sys
import os
import logging
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from dog_analyzer import DogAnalyzer
from firebase_manager import FirebaseManager
from config import Config

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('dog_analysis.log'),
            logging.StreamHandler()
        ]
    )

def analyze_single_image(image_path: str):
    """
    단일 이미지 분석 함수
    
    Args:
        image_path (str): 분석할 이미지 경로
    """
    try:
        # 객체 초기화
        analyzer = DogAnalyzer()
        firebase_mgr = FirebaseManager()
        
        # 이미지 파일 검증
        if not analyzer.validate_image_file(image_path):
            logging.error(f"유효하지 않은 이미지 파일: {image_path}")
            return
        
        # 이미지 분석
        logging.info(f"이미지 분석 시작: {image_path}")
        predictions, confidence_scores, raw_results = analyzer.analyze_dog_image(image_path)
        
        if not predictions:
            logging.warning(f"강아지를 감지하지 못했습니다: {image_path}")
            return
        
        # 결과 출력
        best_class_id = max(confidence_scores.keys(), key=lambda x: confidence_scores[x])
        best_prediction = predictions[best_class_id]
        best_confidence = confidence_scores[best_class_id]
        
        print(f"\n=== 분석 결과 ===")
        print(f"이미지: {os.path.basename(image_path)}")
        print(f"예측 품종: {best_prediction}")
        print(f"신뢰도: {best_confidence:.3f}")
        print(f"모든 예측:")
        for class_id, class_name in predictions.items():
            confidence = confidence_scores[class_id]
            print(f"  - {class_name}: {confidence:.3f}")
        
        # Firebase에 저장
        doc_id = firebase_mgr.save_analysis_result(
            os.path.basename(image_path),
            predictions,
            confidence_scores
        )
        print(f"Firebase 저장 완료 - Document ID: {doc_id}")
        
    except Exception as e:
        logging.error(f"이미지 분석 중 오류 발생: {str(e)}")

def start_api_server():
    """API 서버 시작"""
    try:
        import uvicorn
        from api import app
        
        logging.info("API 서버를 시작합니다...")
        logging.info(f"서버 주소: http://{Config.API_HOST}:{Config.API_PORT}")
        logging.info("종료하려면 Ctrl+C를 누르세요.")
        
        uvicorn.run(
            app,
            host=Config.API_HOST,
            port=Config.API_PORT,
            reload=False
        )
        
    except KeyboardInterrupt:
        logging.info("API 서버가 종료되었습니다.")
    except Exception as e:
        logging.error(f"API 서버 실행 중 오류: {str(e)}")

def show_help():
    """도움말 출력"""
    print("""
강아지 특성 분석 모듈 사용법:

1. API 서버 실행:
   python main.py server

2. 단일 이미지 분석:
   python main.py analyze <image_path>

3. 모델 정보 확인:
   python main.py info

4. 도움말:
   python main.py help

예시:
   python main.py server
   python main.py analyze ./test_dog.jpg
""")

def show_model_info():
    """모델 정보 출력"""
    try:
        analyzer = DogAnalyzer()
        info = analyzer.get_model_info()
        
        print(f"\n=== 모델 정보 ===")
        print(f"모델 경로: {info['model_path']}")
        print(f"모델 타입: {info['model_type']}")
        print(f"신뢰도 임계값: {info['confidence_threshold']}")
        print(f"지원 클래스:")
        for class_id, class_name in info['supported_classes'].items():
            print(f"  {class_id}: {class_name}")
            
    except Exception as e:
        logging.error(f"모델 정보 조회 중 오류: {str(e)}")

def main():
    """메인 함수"""
    setup_logging()
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "server":
        start_api_server()
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("오류: 이미지 경로가 필요합니다.")
            print("사용법: python main.py analyze <image_path>")
            return
        image_path = sys.argv[2]
        analyze_single_image(image_path)
    elif command == "info":
        show_model_info()
    elif command == "help":
        show_help()
    else:
        print(f"알 수 없는 명령어: {command}")
        show_help()

if __name__ == "__main__":
    main() 