# 🐾 LostPet

**강아지 유실 방지 및 식별 시스템**  
YOLOv8, PyTorch, Firebase, FastAPI, React Native 기반으로,  
강아지의 종과 비문(코 무늬)을 등록하고 유실 시 빠르게 찾아주는 AI 기반 플랫폼입니다.

---

## 📸 데모 예시

| 분석 화면 | 유실견 찾기 화면 |
|-----------|------------------|
| ![분석 결과 예시](https://your-url.com/sample_analysis.png) | ![매칭 결과 예시](https://your-url.com/sample_match.png) |

---

## 🔧 주요 기능

- ✅ YOLOv8으로 강아지 탐지 및 정사각 crop
- ✅ 종 분류기 (ResNet18 기반)
- ✅ 코 특징 다중 분류기 (5가지 특징 분류)
- ✅ Firebase Storage + Firestore 연동
- ✅ 코 이미지 임베딩 → FAISS 기반 유사도 검색
- ✅ React Native 기반 앱 UI (사진 업로드, 분석 결과 확인, 유실견 찾기)

---

## 📁 프로젝트 구조

LostPet/
├── frontend/ # React Native (Expo 기반 모바일 앱)
├── backend/ # FastAPI 서버 + YOLO + Firebase + FAISS
├── model_training/ # 종/코 분류기 학습 코드
├── dataset/ # 학습용 이미지 데이터셋
├── test_images/ # 테스트 이미지 샘플
└── README.md



---

## 🚀 실행 방법

### 1. FastAPI 백엔드 실행
```
bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
2. React Native 프론트 실행 (Expo)
```
bash

cd frontend
npm install
npm start
```
3. 모델 학습 (선택)
```
bash

python model_training/train_species.py
python model_training/train_nose_classifier.py
```

---

📮 API 엔드포인트 요약
| 메서드      | 경로                    | 설명                      |
| -------- | --------------------- | ----------------------- |
| `POST`   | `/analyze`            | 강아지 사진 분석 및 Firebase 등록 |
| `POST`   | `/match`              | 유실견 코 이미지 → 유사도 검색      |
| `GET`    | `/admin/list`         | 전체 등록 강아지 조회            |
| `DELETE` | `/admin/delete/{uid}` | 특정 강아지 데이터 삭제           |

---

🧠 사용 기술
*💡 YOLOv8 (Ultralytics)

*🧠 PyTorch (ResNet 기반 분류기)

*☁️ Firebase Storage / Firestore

*⚡ FastAPI

*📱 React Native (Expo)

*🧭 FAISS (코 임베딩 유사도 검색)

---

🔐 Firebase 설정
*backend/firebase_key.json 파일에 Firebase Admin SDK 키 필요

*Storage 버킷 주소는 your-bucket-name.appspot.com으로 수정

*이미지 URL은 .public_url을 통해 접근 가능

---
📢 기여/참여
*이 프로젝트는 누구나 포크하여 사용할 수 있습니다.
*아이디어, 이슈, 기능 제안 또는 PR 기여를 환영합니다!