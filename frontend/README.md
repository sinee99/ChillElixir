# 🐾 LostPet Mobile App

React Native + Expo 기반의 강아지 유실 방지 및 식별 모바일 앱입니다.

## 📱 주요 기능

- **홈 화면**: 메인 대시보드 및 빠른 액션
- **반려견 등록**: 사진 촬영/선택하여 AI 분석 및 등록
- **유실견 찾기**: 코 사진으로 유사한 반려견 검색
- **내 반려견**: 등록된 반려견 목록 관리

## 🚀 실행 방법

### 1. 사전 준비

```bash
# Node.js 설치 확인 (v16 이상)
node --version

# Expo CLI 설치
npm install -g expo-cli
```

### 2. 의존성 설치

```bash
cd frontend
npm install
```

### 3. 백엔드 서버 설정

`services/api.js` 파일에서 API 주소를 실제 백엔드 서버 IP로 변경:

```javascript
const API_BASE_URL = 'http://YOUR_BACKEND_IP:8000';
```

### 4. 앱 실행

```bash
# 개발 서버 시작
npm start

# 또는 Expo CLI 직접 사용
expo start
```

### 5. 모바일에서 실행

1. 스마트폰에 **Expo Go** 앱 설치
2. 터미널에 표시된 QR 코드를 Expo Go 앱으로 스캔
3. 앱이 자동으로 로드됩니다

## 📂 프로젝트 구조

```
frontend/
├── App.js                  # 메인 앱 컴포넌트
├── screens/               # 화면 컴포넌트들
│   ├── HomeScreen.js      # 홈 화면
│   ├── RegisterScreen.js  # 반려견 등록
│   ├── FindScreen.js      # 유실견 찾기
│   └── MyPetsScreen.js    # 내 반려견 관리
├── services/              # API 서비스
│   └── api.js             # 백엔드 통신 로직
├── package.json           # 의존성 관리
└── app.json              # Expo 설정
```

## 🎨 디자인 시스템

- **Primary Color**: #0047AB (코발트 블루)
- **Secondary Color**: #4A90E2 (라이트 블루)
- **Accent Color**: #6BB6FF (스카이 블루)
- **Background**: #F8F9FA (라이트 그레이)

## 📋 요구사항

- **Node.js**: v16 이상
- **React Native**: 0.72.6
- **Expo SDK**: 49
- **iOS**: 11.0 이상
- **Android**: API 21 이상

## 🔧 개발 시 주의사항

1. **네트워크 연결**: 백엔드 서버와 모바일 기기가 같은 네트워크에 있어야 합니다
2. **권한 설정**: 카메라 및 갤러리 접근 권한이 필요합니다
3. **이미지 크기**: 업로드 시 자동으로 최적화됩니다

## 🐛 문제 해결

### 네트워크 오류
- 백엔드 서버가 실행 중인지 확인
- IP 주소가 올바른지 확인
- 방화벽 설정 확인

### 카메라/갤러리 오류
- 앱 권한 설정에서 카메라, 사진 접근 허용
- 기기 저장 공간 확인

### 빌드 오류
```bash
# 캐시 클리어
expo r -c

# 의존성 재설치
rm -rf node_modules
npm install
```

## 📱 지원 플랫폼

- **iOS**: iPhone, iPad
- **Android**: 스마트폰, 태블릿
- **Web**: 브라우저 (제한적 기능)

---

**LostPet 팀** | 2024년 