# 🐶 DogIdentifierProject

강아지 유실 방지를 위한 종/코 분석 및 식별 시스템. YOLOv8 + 분류기 + 비문(코) 임베딩을 기반으로 하며, React Native 앱과 FastAPI 백엔드로 구성됨.

---

## 📦 전체 폴더 구조

```
DogIdentifierProject/
├── frontend/            # React Native (Expo 기반)
├── backend/             # FastAPI 서버 (YOLO + 분류기 + Firebase)
├── dataset/             # 학습용 데이터셋 (종 / 코)
├── model_training/      # 학습 코드 (train_species.py, train_nose_classifier.py 등)
├── test_images/         # 테스트 이미지 샘플
└── README.md            # 이 문서
```

---

## 🚀 기능 개요

### 1. FastAPI 백엔드

* YOLOv8로 강아지 탐지 및 crop
* 종 분류기 (ResNet18)
* 코 특징 분류기 (다중 라벨)
* 비문 임베딩 추출 (ResNet18 기반)
* Firebase Storage/Firestore 저장
* FAISS 유사도 검색 (분실견 찾기)

### 2. React Native 프론트엔드

* Expo 기반 이미지 업로드/분석
* 분석 결과 출력 (종 + 코 특징)
* 분실견 탐지 기능 (/match)

### 3. 모델 학습

* 종 분류기 (`train_species.py`)
* 코 특징 분류기 (`train_nose_classifier.py`)
* 자동 데이터 분할 (`split_dataset.py`)

---

## ✅ 실행 순서

### 1. 종/코 이미지 준비 후 분할

```
python model_training/split_dataset.py
```

### 2. 모델 학습

```
python model_training/train_species.py
python model_training/train_nose_classifier.py
```

### 3. 백엔드 실행 (backend 디렉토리)

```
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. 프론트 실행 (frontend 디렉토리)

```
npm install
npm start
```

---

## 🔐 Firebase 설정

* `backend/firebase_key.json`에 Firebase Admin SDK 키 저장
* Storage 버킷: `your-bucket-name.appspot.com` 으로 변경

---

## 📮 API 요약

### POST `/analyze`

* 입력: 이미지 파일
* 출력: 종 + 코 특징 + 이미지 URL + UID 저장

### POST `/match`

* 입력: 코 이미지
* 출력: 유사 UID 리스트

### GET `/admin/list`

* 등록된 모든 강아지 조회

### DELETE `/admin/delete/{uid}`

* 특정 개체 삭제

---

## 🧠 개발자 참고

* 프론트에서 서버 접속 시: PC 로컬 IP 주소로 접속 (예: `http://192.168.0.5:8000`)
* 모바일 Expo Go 앱에서 QR 스캔 → 즉시 사용 가능
* 모델 학습 시 `dataset/species_raw` 와 `dataset/nose_raw` 폴더에 종별 이미지 정리 필요

---

## ✨ 기여

* 기획 및 설계: 사용자
* 기술 구현: React Native, FastAPI, Firebase, PyTorch, FAISS, YOLOv8
