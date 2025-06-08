# 🐕 강아지 코 탐지 및 전처리 도구

이 도구는 YOLOv5를 사용하여 강아지 이미지에서 코 부분을 자동으로 탐지하고 전처리하는 프로그램입니다.

## 🌟 주요 기능

- **자동 코 탐지**: YOLOv5 모델을 사용한 정확한 코 영역 탐지
- **이미지 전처리**: CLAHE 기법을 활용한 이미지 품질 향상
- **배치 처리**: 폴더 내 모든 이미지 일괄 처리
- **유연한 설정**: 신뢰도, 크기 등 다양한 옵션 조정 가능

## 📁 파일 구조

```
model_training/Dog_nose/
├── nose.py                 # 메인 클래스
├── run_nose_detection.py   # 실행 스크립트
├── README_nose.md          # 사용 설명서
└── best.pt                 # YOLOv5 모델 파일 (선택사항)
```

## 🛠️ 설치 요구사항

```bash
pip install torch torchvision opencv-python numpy pathlib
```

YOLOv5는 자동으로 다운로드됩니다.

## 🚀 사용 방법

### 1. 기본 사용법

```bash
python run_nose_detection.py --input your_dog_images/ --output processed_noses/
```

### 2. 고급 옵션

```bash
python run_nose_detection.py \
    --input dog_photos/ \
    --output nose_crops/ \
    --model model_training/Dog_nose/best.pt \
    --confidence 0.7 \
    --size 256 256
```

### 3. 파이썬 코드에서 직접 사용

```python
from nose import DogNosePreprocessorYOLOv5

# 전처리기 초기화
preprocessor = DogNosePreprocessorYOLOv5(
    model_path='model_training/Dog_nose/best.pt',  # 커스텀 모델 (없으면 기본 모델 사용)
    target_size=(224, 224),
    confidence_threshold=0.5
)

# 단일 이미지 처리
result = preprocessor.process_image('dog_photo.jpg')
if result is not None:
    cv2.imwrite('nose_crop.jpg', (result * 255).astype(np.uint8))

# 폴더 일괄 처리
preprocessor.process_directory('input_folder/', 'output_folder/')
```

## ⚙️ 옵션 설명

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--input` `-i` | 입력 이미지 폴더 경로 | **필수** |
| `--output` `-o` | 출력 폴더 경로 | `processed_noses` |
| `--model` `-m` | YOLOv5 모델 파일 경로 | `model_training/Dog_nose/best.pt` |
| `--confidence` `-c` | 탐지 신뢰도 임계값 | `0.5` |
| `--size` `-s` | 출력 이미지 크기 (가로 세로) | `224 224` |

## 📸 지원하는 이미지 형식

- `.jpg`, `.jpeg`
- `.png`
- `.bmp`
- `.tiff`
- `.webp`

## 🔧 처리 과정

1. **탐지**: YOLOv5로 강아지 코 영역 탐지
2. **크롭**: 탐지된 영역 + 여백 추출
3. **전처리**:
   - 그레이스케일 변환
   - CLAHE 적용 (명암 대비 향상)
   - 지정 크기로 리사이즈
   - 정규화 (0-1 범위)
4. **저장**: 전처리된 이미지를 출력 폴더에 저장

## 💡 사용 팁

### 1. 모델 파일이 없는 경우
- 커스텀 모델 파일이 없어도 기본 YOLOv5s 모델로 동작합니다
- 기본 모델은 강아지 전체를 탐지하므로 정확도가 떨어질 수 있습니다

### 2. 신뢰도 조정
- 탐지가 너무 많이 실패하면 `--confidence` 값을 낮춰보세요 (예: 0.3)
- 잘못된 탐지가 많으면 값을 높여보세요 (예: 0.7)

### 3. 이미지 품질
- 고해상도 이미지일수록 탐지 성능이 좋습니다
- 코가 명확하게 보이는 정면/측면 사진이 최적입니다

### 4. 배치 크기
- GPU 메모리가 부족하면 이미지를 작은 배치로 나눠서 처리하세요

## 📊 출력 예시

```
🐕 강아지 코 탐지 시작!
==================================================
📁 입력 폴더: dog_photos
📁 출력 폴더: processed_noses
🤖 모델 경로: model_training/Dog_nose/best.pt
🎯 신뢰도 임계값: 0.5
📏 출력 크기: 224x224
==================================================
📸 총 10개의 이미지를 처리합니다.

[1/10] 처리 중: golden_retriever.jpg
  ✅ 탐지 성공! 신뢰도: 0.847, 박스: (145,89,201,134)
  💾 저장 완료: processed_noses/nose_golden_retriever.jpg

[2/10] 처리 중: poodle.jpg
  ✅ 탐지 성공! 신뢰도: 0.723, 박스: (98,76,142,115)
  💾 저장 완료: processed_noses/nose_poodle.jpg

...

📊 처리 결과: 성공 8개, 실패 2개

✅ 모든 작업이 완료되었습니다!
```

## ❓ 문제 해결

### 모델 로드 실패
```
❌ 모델 로드 실패: [Errno 2] No such file or directory: 'model_training/Dog_nose/best.pt'
기본 YOLOv5s 모델을 사용합니다.
```
- 커스텀 모델 파일이 없을 때 나타나는 정상적인 메시지입니다
- 기본 모델로도 어느 정도 동작하지만, 코 전용 모델이 있으면 더 정확합니다

### 탐지 실패가 많은 경우
1. 신뢰도 임계값을 낮춰보세요: `--confidence 0.3`
2. 이미지 품질을 확인해보세요 (너무 어둡거나 흐린 경우)
3. 강아지 코가 명확하게 보이는지 확인해보세요

### 메모리 부족
- 이미지 크기를 줄여보세요: `--size 128 128`
- 한 번에 처리하는 이미지 수를 줄여보세요

## 🔗 관련 도구

이 도구는 다음과 같은 용도로 활용할 수 있습니다:

1. **강아지 개체 식별**: 코 패턴을 이용한 개별 강아지 인식
2. **품종 분류**: 코 형태를 특징으로 한 품종 분류
3. **의료 진단**: 코 상태 분석을 통한 건강 진단
4. **데이터셋 구축**: 머신러닝 모델 훈련용 데이터 전처리

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. 필요한 라이브러리가 모두 설치되었는지
2. 입력 폴더에 지원하는 형식의 이미지가 있는지
3. 충분한 디스크 공간이 있는지
4. Python 버전이 3.7 이상인지 