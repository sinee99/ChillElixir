# 🐕 강아지 비문 인식 AI 서비스 (Docker)

YOLOv5와 Siamese Neural Network를 활용한 강아지 비문(코 주름) 인식 API 서비스입니다.

## 🚀 주요 기능

- **강아지 코 탐지 및 크롭**: YOLOv5 모델로 강아지 얼굴에서 코 영역만 정확히 추출
- **비문 특징 추출**: Siamese Neural Network로 고유한 비문 패턴 분석
- **개체 식별**: 두 비문 이미지 비교를 통한 동일 개체 판별
- **REST API**: 간단한 HTTP 요청으로 모든 기능 사용 가능

## 📋 시스템 요구사항

### 하드웨어
- **CPU**: Intel i5 이상 또는 AMD Ryzen 5 이상
- **RAM**: 8GB 이상 (GPU 사용시 16GB 권장)
- **GPU**: NVIDIA GPU (CUDA 지원, 선택사항)
- **Storage**: 10GB 이상 여유 공간

### 소프트웨어
- **Docker**: 20.10 이상
- **Docker Compose**: 1.29 이상
- **NVIDIA Docker** (GPU 사용시): nvidia-docker2

## 🛠️ 설치 및 실행

### 1단계: 모델 준비
먼저 기존 프로젝트에서 학습된 모델을 준비합니다:

```bash
# 모델 변환 스크립트 실행
python model_converter.py --source "dognose_recognition_management_service-main" --target "./models"
```

### 2단계: Docker 빌드 및 실행

#### 옵션 A: Docker Compose 사용 (권장)
```bash
# 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build

# 서비스 중지
docker-compose down
```

#### 옵션 B: Docker 직접 사용
```bash
# 이미지 빌드
docker build -t dog-nose-ai .

# 컨테이너 실행 (CPU 모드)
docker run -p 5000:5000 -v $(pwd)/models:/app/models:ro dog-nose-ai

# 컨테이너 실행 (GPU 모드)
docker run --gpus all -p 5000:5000 -v $(pwd)/models:/app/models:ro dog-nose-ai
```

### 3단계: 서비스 확인
```bash
# 헬스 체크
curl http://localhost:5000/health

# 또는 웹 브라우저에서
http://localhost:5000/health
```

## 📡 API 사용법

### 1. 헬스 체크
```bash
GET /health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "yolo_loaded": true,
  "siamese_loaded": true,
  "device": "cuda:0",
  "available_siamese_models": ["original", "canny", "laplacian", "sobel"],
  "current_siamese_model": "original",
  "total_models_loaded": 5
}
```

### 2. 모델 정보 조회
```bash
GET /models
```

**응답 예시:**
```json
{
  "yolo_available": true,
  "siamese_models": {
    "available": ["original", "canny", "laplacian", "sobel"],
    "current": "original",
    "descriptions": {
      "original": "Original preprocessing (no edge detection)",
      "canny": "Canny edge detection preprocessing",
      "laplacian": "Laplacian edge detection preprocessing",
      "sobel": "Sobel edge detection preprocessing"
    }
  },
  "total_models": 5
}
```

### 3. Siamese 모델 전환
```bash
POST /switch_model
Content-Type: application/json

# 파라미터: {"model_type": "canny"}
```

**Python 예시:**
```python
import requests

data = {"model_type": "canny"}
response = requests.post('http://localhost:5000/switch_model', json=data)
result = response.json()
```

### 4. 강아지 코 크롭
```bash
POST /crop_nose
Content-Type: multipart/form-data

# 파라미터: image (파일)
```

**Python 예시:**
```python
import requests

with open('dog_image.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/crop_nose', files=files)
    result = response.json()
```

### 5. 비문 특징 추출
```bash
POST /extract_features
Content-Type: multipart/form-data

# 파라미터: image (파일), model_type (선택사항: original/canny/laplacian/sobel)
```

### 6. 두 비문 비교
```bash
POST /compare_noses
Content-Type: multipart/form-data

# 파라미터: image1 (파일), image2 (파일), model_type (선택사항)
```

**응답 예시:**
```json
{
  "success": true,
  "similarity": 0.8234,
  "is_same_dog": true,
  "confidence": "high",
  "model_used": "canny"
}
```

### 7. 전체 프로세스 (크롭 + 특징 추출)
```bash
POST /process_full
Content-Type: multipart/form-data

# 파라미터: image (파일), model_type (선택사항)
```

**응답 예시:**
```json
{
  "success": true,
  "cropped_nose": "base64_encoded_image",
  "features": [0.1, 0.2, 0.3, ...],
  "crop_size": [224, 224, 3],
  "feature_size": 128,
  "model_used": "original"
}
```

## 🧪 테스트

API 테스트 스크립트를 사용하여 서비스 기능을 확인할 수 있습니다:

```bash
# 기본 테스트
python test_api.py --image test_dog.jpg

# 비교 테스트 포함
python test_api.py --image test_dog1.jpg --image2 test_dog2.jpg

# 다른 서버 테스트
python test_api.py --url http://your-server:5000 --image test_dog.jpg
```

## 📁 프로젝트 구조

```
dog_nose_ai_service/
├── app.py                 # Flask API 서버
├── Dockerfile            # Docker 이미지 빌드 파일
├── docker-compose.yml    # Docker Compose 설정
├── requirements.txt      # Python 패키지 목록
├── model_converter.py    # 모델 변환 스크립트
├── test_api.py          # API 테스트 스크립트
├── README.md            # 사용 가이드 (이 파일)
└── models/              # AI 모델 파일들
    ├── yolo_best.pt     # YOLOv5 모델
    ├── siamese_original.h5  # Siamese 모델
    └── model_info.txt   # 모델 정보
```

## 🔧 설정 및 커스터마이징

### 환경 변수
- `CUDA_VISIBLE_DEVICES`: 사용할 GPU 번호 (기본값: 0)
- `FLASK_ENV`: Flask 환경 (production/development)

### 모델 교체
다른 학습된 모델을 사용하려면:
1. `models/` 디렉토리에 새 모델 파일 복사
2. `app.py`에서 모델 경로 수정
3. 컨테이너 재시작

### 성능 튜닝
- **배치 크기**: 메모리에 따라 조정
- **신뢰도 임계값**: YOLOv5 탐지 정확도 조정
- **유사도 임계값**: 비문 비교 민감도 조정

## 🐛 문제 해결

### 일반적인 문제들

#### 1. GPU 인식 안됨
```bash
# NVIDIA Docker 설치 확인
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# CUDA 버전 확인
nvidia-smi
```

#### 2. 모델 로드 실패
```bash
# 모델 파일 존재 확인
ls -la models/

# 모델 유효성 검사
python model_converter.py --source [프로젝트_경로] --target ./models
```

#### 3. 메모리 부족
```bash
# Docker 메모리 제한 증가
docker run -m 8g -p 5000:5000 dog-nose-ai

# 또는 docker-compose.yml에서 설정
```

#### 4. API 응답 느림
- GPU 사용 확인
- 이미지 크기 조정 (최대 1920x1080 권장)
- 배치 처리 고려

### 로그 확인
```bash
# 실시간 로그 보기
docker-compose logs -f

# 컨테이너 로그 보기
docker logs dog-nose-ai-service
```

## 📊 성능 벤치마크

| 작업 | CPU (i7-9700K) | GPU (RTX 3080) |
|------|----------------|----------------|
| 코 크롭 | ~2.5초 | ~0.8초 |
| 특징 추출 | ~1.8초 | ~0.5초 |
| 비문 비교 | ~3.2초 | ~1.0초 |

*이미지 크기: 1024x768 기준

## 🤝 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면:
- Issue 등록
- 이메일 문의

---

**Made with ❤️ for 🐕 lovers** 