# 🐾 Dog Identifier Project

YOLOv8, ResNet, Firebase, FastAPI, React Native를 활용한 **반려견 유실방지 및 식별 시스템**입니다.  
강아지의 **외형(종/색상/코 특징 등)**을 등록하고, 유실견 발생 시 코 사진을 기반으로 **유사 개체를 탐색**할 수 있습니다.

---

## 🔧 기능 요약

- ✅ YOLOv8으로 강아지 자동 감지 및 Crop
- ✅ ResNet 기반 종 분류기 (Shiba Inu, Maltese 등)
- ✅ 코 특징 다중 분류기 (색상, 크기, 상처 등)
- ✅ Firebase Storage에 이미지 업로드
- ✅ Firestore에 메타데이터 저장
- ✅ FAISS 임베딩 유사도 검색으로 유실견 추론

---

## 🚀 실행 방법


### 1. 환경 준비

```bash
# FastAPI 백엔드
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# React Native 프론트엔드
cd frontend
npm install
npm start


### 📁 프로젝트 구조
DogIdentifierProject/
├── frontend/ # React Native (Expo)
├── backend/ # FastAPI + YOLO + Firebase
├── dataset/ # 학습용 데이터셋
├── model_training/ # 모델 학습 스크립트
└── README.md

📮 API 문서
메서드	경로	설명
POST	/analyze	강아지 이미지 분석 (종/코 특징)
POST	/match	코 이미지로 유사 개체 검색
GET	/admin/list	등록된 모든 강아지 조회
DELETE	/admin/delete/{uid}	특정 개체 삭제

🧠 사용 기술
🔍 YOLOv8 (Ultralytics)

🧠 PyTorch (ResNet)

🔥 Firebase (Storage + Firestore)

⚙️ FastAPI

📱 React Native (Expo)

🧭 FAISS (유사도 검색)

📝 라이센스
MIT License © 2024 [당신의 GitHub 이름]

🙋‍♀️ 기여
이 프로젝트는 누구든 자유롭게 포크/수정할 수 있습니다.
피드백, 버그 제보, 기능 추가는 언제든 환영합니다!