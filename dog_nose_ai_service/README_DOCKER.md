# 🐕 강아지 비문 인식 AI 서비스 (Docker 버전)

Docker와 docker-compose를 사용하여 강아지 비문 인식 AI 서비스를 쉽게 배포하고 관리할 수 있습니다.

## 📁 프로젝트 구조

```
dog_nose_ai_service/
├── app.py                      # Flask API 서버
├── model_converter.py          # 모델 변환 유틸리티
├── requirements.txt            # Python 패키지 의존성
├── Dockerfile                  # Docker 이미지 빌드 설정
├── docker-compose.yml          # Docker Compose 메인 설정
├── docker-compose.override.yml # 개발 환경 설정
├── nginx.conf                  # Nginx 리버스 프록시 설정
├── test_api.py                 # API 테스트 스크립트
├── models/                     # AI 모델 파일들
│   ├── yolo_best.pt           # YOLOv5 강아지 코 탐지 모델
│   ├── siamese_original.h5    # Siamese 원본 모델
│   ├── siamese_canny.h5       # Canny 에지 검출 모델
│   ├── siamese_laplacian.h5   # Laplacian 에지 검출 모델
│   ├── siamese_sobel.h5       # Sobel 에지 검출 모델
│   └── model_info.txt         # 모델 정보
├── logs/                      # 로그 파일 저장소
└── README_DOCKER.md           # Docker 사용 가이드
```

## 🚀 빠른 시작

### 1단계: 필수 요구사항 확인
- **Docker**: 20.10 이상
- **Docker Compose**: 1.29 이상
- **RAM**: 8GB 이상 (16GB 권장)
- **디스크 공간**: 10GB 이상 여유 공간

### 2단계: 서비스 실행

#### 기본 실행 (CPU 버전)
```bash
# 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f dog-nose-ai

# 서비스 중지
docker-compose down
```

#### GPU 사용 (NVIDIA GPU가 있는 경우)
```bash
# GPU 서비스 활성화 (docker-compose.yml에서 주석 해제 후)
docker-compose up --build dog-nose-ai-gpu

# 또는 개발 환경에서 GPU 사용
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build dog-nose-ai-gpu-dev
```

### 3단계: 서비스 확인
```bash
# 헬스 체크
curl http://localhost:5000/health

# 또는 브라우저에서
http://localhost:5000/health

# Nginx를 통한 접근 (포트 80)
http://localhost/health
```

## 🔧 설정 옵션

### 환경 변수 설정

`docker-compose.yml` 파일에서 다음 환경 변수들을 조정할 수 있습니다:

```yaml
environment:
  - FLASK_ENV=production          # 실행 환경 (production/development)
  - FLASK_DEBUG=0                 # 디버그 모드 (0/1)
  - PYTHONUNBUFFERED=1           # Python 버퍼링 비활성화
  - CUDA_VISIBLE_DEVICES=""      # GPU 사용 설정 (빈 문자열은 CPU만 사용)
```

### 포트 설정

기본 포트 설정:
- **Flask API**: 5000번 포트
- **Nginx**: 80번 포트 (HTTP), 443번 포트 (HTTPS)
- **GPU 버전**: 5001번 포트

다른 포트 사용시 `docker-compose.yml`에서 수정:
```yaml
ports:
  - "8080:5000"  # 호스트의 8080 포트를 컨테이너의 5000 포트로 연결
```

### 볼륨 마운트

- **모델 파일**: `./models:/app/models:ro` (읽기 전용)
- **로그 파일**: `./logs:/app/logs`
- **개발 환경**: 코드 실시간 반영을 위한 볼륨 추가

## 🧪 API 테스트

### 자동 테스트 스크립트 실행
```bash
# 테스트 스크립트 실행
python test_api.py

# 또는 Docker 내에서 실행
docker-compose exec dog-nose-ai python test_api.py
```

### 수동 API 테스트

#### 1. 헬스 체크
```bash
curl http://localhost:5000/health
```

#### 2. 모델 목록 조회
```bash
curl http://localhost:5000/models
```

#### 3. 이미지 업로드 및 코 크롭
```bash
curl -X POST -F "image=@test_dog.jpg" http://localhost:5000/crop_nose
```

#### 4. 특징 추출
```bash
curl -X POST -F "image=@test_dog.jpg" http://localhost:5000/extract_features
```

#### 5. 비문 비교
```bash
curl -X POST \
  -F "image1=@dog1.jpg" \
  -F "image2=@dog2.jpg" \
  -F "model_type=canny" \
  http://localhost:5000/compare_noses
```

## 🐛 문제 해결

### 일반적인 문제들

#### 1. 컨테이너가 시작되지 않는 경우
```bash
# 로그 확인
docker-compose logs dog-nose-ai

# 컨테이너 상태 확인
docker ps -a

# 이미지 재빌드
docker-compose build --no-cache
```

#### 2. 모델 로딩 실패
```bash
# 모델 파일 확인
ls -la models/

# 모델 권한 확인
chmod 644 models/*.pt models/*.h5
```

#### 3. 메모리 부족
```bash
# Docker 메모리 제한 확인
docker stats

# 메모리 제한 설정 (docker-compose.yml에 추가)
deploy:
  resources:
    limits:
      memory: 8G
```

#### 4. GPU 관련 문제
```bash
# NVIDIA Docker 설치 확인
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# GPU 사용 가능 확인
docker-compose exec dog-nose-ai-gpu nvidia-smi
```

### 로그 확인 방법

```bash
# 실시간 로그 확인
docker-compose logs -f dog-nose-ai

# 특정 시간 이후 로그 확인
docker-compose logs --since="2h" dog-nose-ai

# 로그 파일 직접 확인
tail -f logs/app.log
```

## 🔒 보안 설정

### 1. Nginx HTTPS 설정
```bash
# SSL 인증서 디렉토리 생성
mkdir -p ssl

# 자체 서명 인증서 생성 (테스트용)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# nginx.conf에서 HTTPS 섹션 주석 해제
```

### 2. API 키 인증 (선택사항)
Flask 앱에 API 키 인증을 추가하려면 `app.py`를 수정하세요:

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-api-key':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/crop_nose', methods=['POST'])
@require_api_key
def crop_nose():
    # ... 기존 코드
```

## 📊 모니터링

### Docker 컨테이너 모니터링
```bash
# 리소스 사용량 확인
docker stats dog-nose-ai-service

# 컨테이너 상태 확인
docker-compose ps

# 헬스체크 상태 확인
docker inspect dog-nose-ai-service | grep Health -A 10
```

### 애플리케이션 모니터링
```bash
# API 응답 시간 테스트
time curl http://localhost:5000/health

# 로그 레벨 조정 (app.py에서)
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 프로덕션 배포

### 1. 환경 설정
```bash
# 프로덕션 환경 변수 설정
export FLASK_ENV=production
export FLASK_DEBUG=0

# 보안 설정
export SECRET_KEY="your-super-secret-key"
```

### 2. 리소스 제한 설정
```yaml
# docker-compose.yml에 추가
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 8G
    reservations:
      cpus: '1'
      memory: 4G
```

### 3. 백업 및 복구
```bash
# 모델 파일 백업
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# 로그 파일 백업
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요. 