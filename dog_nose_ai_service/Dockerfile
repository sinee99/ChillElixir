# PyTorch와 TensorFlow를 지원하는 Python 베이스 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 OpenCV 의존성 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    git \
    libglib2.0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 요구사항 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app.py .
COPY model_converter.py .

# 모델 디렉토리 생성
RUN mkdir -p /app/models

# 포트 5000 노출
EXPOSE 5000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Flask 앱 실행
CMD ["python", "app.py"] 