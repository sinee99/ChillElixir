#!/usr/bin/env python3
"""
간단한 강아지 비문 인식 API 서버 (빠른 테스트용)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 API"""
    try:
        # 모델 파일 존재 확인
        yolo_exists = os.path.exists('./models/yolo_best.pt')
        siamese_exists = os.path.exists('./models/siamese_original.h5')
        
        return jsonify({
            'status': 'healthy',
            'yolo_loaded': yolo_exists,
            'siamese_loaded': siamese_exists,
            'device': 'cpu',
            'message': '간단 테스트 서버',
            'models_found': {
                'yolo_best.pt': yolo_exists,
                'siamese_original.h5': siamese_exists,
                'siamese_canny.h5': os.path.exists('./models/siamese_canny.h5'),
                'siamese_laplacian.h5': os.path.exists('./models/siamese_laplacian.h5'),
                'siamese_sobel.h5': os.path.exists('./models/siamese_sobel.h5'),
            }
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def list_models():
    """모델 목록 확인 API"""
    try:
        models_dir = './models'
        if not os.path.exists(models_dir):
            return jsonify({'error': 'Models directory not found'}), 404
        
        files = os.listdir(models_dir)
        model_files = [f for f in files if f.endswith(('.pt', '.h5'))]
        
        return jsonify({
            'models_directory': models_dir,
            'model_files': model_files,
            'total_files': len(model_files),
            'note': '이것은 간단 테스트 서버입니다. 실제 AI 기능은 app.py를 사용하세요.'
        })
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """테스트 엔드포인트"""
    return jsonify({
        'message': '🐕 간단 테스트 서버가 정상 작동 중입니다!',
        'status': 'ok',
        'endpoints': [
            'GET /health - 헬스 체크',
            'GET /models - 모델 파일 목록',
            'GET /test - 이 테스트 엔드포인트'
        ]
    })

if __name__ == '__main__':
    print("🐕 강아지 비문 인식 AI - 간단 테스트 서버")
    print("=" * 50)
    print("포트: 5001")
    print("헬스 체크: http://localhost:5001/health")
    print("모델 확인: http://localhost:5001/models")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=False) 