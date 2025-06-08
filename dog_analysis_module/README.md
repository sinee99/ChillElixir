# 강아지 특성 분석 모듈

YOLOv8 모델을 사용하여 강아지 사진을 분석하고 품종을 예측한 후 Firebase에 결과를 저장하는 독립적인 모듈입니다.

## 주요 기능

- YOLOv8 기반 강아지 품종 분류
- FastAPI를 통한 REST API 제공
- Firebase Firestore에 분석 결과 저장
- Docker 컨테이너화 지원
- 실시간 이미지 업로드 및 분석

## 파일 구조

```
dog_analysis_module/
├── main.py                 # 메인 실행 파일
├── api.py                  # FastAPI 서버
├── dog_analyzer.py         # 강아지 분석 모듈
├── firebase_manager.py     # Firebase 연동 모듈
├── config.py              # 설정 관리
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 이미지 빌드
├── docker-compose.yml    # Docker Compose 설정
├── .env.example         # 환경 변수 예시
└── README.md           # 이 파일
```

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 실제 값으로 수정:

```bash
cp .env.example .env
```

### 3. Firebase 설정

1. Firebase 프로젝트에서 서비스 계정 키 생성
2. `firebase-credentials.json` 파일을 모듈 디렉토리에 저장
3. `.env` 파일에서 Firebase 설정 업데이트

### 4. 모델 파일 확인

`config.py`에서 모델 경로가 올바른지 확인:
```python
MODEL_PATH = "../model_training/DogCharacteristic/runs/detect/train/weights/best.pt"
```

## 사용법

### 1. API 서버 실행

```bash
python main.py server
```

서버가 시작되면 `http://localhost:8000`에서 접근 가능합니다.

### 2. 단일 이미지 분석

```bash
python main.py analyze path/to/dog_image.jpg
```

### 3. 모델 정보 확인

```bash
python main.py info
```

## API 엔드포인트

### POST /analyze
강아지 이미지를 업로드하여 분석합니다.

**요청:**
- `file`: 이미지 파일 (multipart/form-data)

**응답:**
```json
{
  "success": true,
  "filename": "dog.jpg",
  "predicted_breed": "골든 리트리버",
  "confidence_score": 0.892,
  "all_predictions": {
    "0": "골든 리트리버",
    "1": "래브라도"
  },
  "all_confidence_scores": {
    "0": 0.892,
    "1": 0.234
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### GET /model-info
모델 정보를 조회합니다.

### GET /recent-analyses?limit=10
최근 분석 결과를 조회합니다.

### GET /analysis/{doc_id}
특정 분석 결과를 조회합니다.

### GET /health
서비스 상태를 확인합니다.

## Docker 사용법

### 1. Docker 이미지 빌드

```bash
docker build -t dog-analyzer .
```

### 2. Docker Compose로 실행

```bash
docker-compose up -d
```

### 3. 로그 확인

```bash
docker-compose logs -f
```

## 설정 옵션

`config.py`에서 다음 설정을 수정할 수 있습니다:

- `MODEL_PATH`: YOLOv8 모델 파일 경로
- `CONFIDENCE_THRESHOLD`: 신뢰도 임계값 (기본값: 0.5)
- `DOG_CLASSES`: 지원하는 강아지 품종 클래스
- `MAX_FILE_SIZE`: 최대 파일 크기 (기본값: 10MB)
- `ALLOWED_EXTENSIONS`: 지원하는 파일 형식

## Firebase 데이터 구조

분석 결과는 다음과 같은 구조로 Firestore에 저장됩니다:

```json
{
  "image_filename": "dog.jpg",
  "predicted_breed": "골든 리트리버",
  "confidence_score": 0.892,
  "all_predictions": {
    "0": "골든 리트리버",
    "1": "래브라도"
  },
  "all_confidence_scores": {
    "0": 0.892,
    "1": 0.234
  },
  "analysis_timestamp": "2024-01-01T12:00:00",
  "model_used": "YOLOv8_DogCharacteristic"
}
```

## 문제 해결

### 1. 모델 로드 오류
- 모델 파일 경로가 올바른지 확인
- 모델 파일이 존재하는지 확인

### 2. Firebase 연결 오류
- Firebase 인증 파일이 올바른지 확인
- Firebase 프로젝트 설정이 올바른지 확인

### 3. 이미지 분석 오류
- 이미지 파일이 지원되는 형식인지 확인
- 이미지 파일이 손상되지 않았는지 확인

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 