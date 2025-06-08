# PyTorch CUDA 기반 이미지 사용
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 최적화 (캐시 정리 포함)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libgthread2.0-0 \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Python 의존성 파일을 먼저 복사 (캐싱 최적화)
COPY requirements.txt .

# Python 패키지 설치 최적화
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# PyTorch 관련 라이브러리 설치 (CUDA 버전)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# 필요한 Python 패키지 설치
RUN pip install \
    tensorflow==2.12.0 \
    flask==2.3.2 \
    opencv-python-headless==4.8.0.74 \
    pillow==10.0.0 \
    numpy==1.24.3 \
    pandas==2.0.3 \
    scikit-learn==1.3.0 \
    matplotlib==3.7.2 \
    seaborn==0.12.2 \
    requests==2.31.0 \
    tqdm==4.65.0 \
    pyyaml==6.0 \
    scipy==1.11.1 \
    imgaug==0.4.0

# YOLOv5 리포지토리 미리 다운로드 (캐싱)
RUN python -c "import torch; torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=False)"

# 애플리케이션 코드 복사
COPY app.py .

# 모델 디렉토리 생성
RUN mkdir -p models

# 포트 노출
EXPOSE 5000

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 애플리케이션 실행
CMD ["python", "app.py"] 