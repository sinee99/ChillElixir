# 🐕 강아지 특징 분석기 (Dog Feature Analyzer)

YOLOv8n 모델을 사용하여 강아지 사진의 다양한 특징을 자동으로 감지하고 분석하는 도구입니다.

## 🎯 주요 기능

- ✅ **단일 이미지 분석**: 개별 강아지 사진의 특징 감지
- ✅ **배치 분석**: 폴더 내 모든 이미지 일괄 처리
- ✅ **시각화**: 감지된 특징을 바운딩 박스와 함께 표시
- ✅ **통계 분석**: 클래스별 감지 빈도 및 신뢰도 분석
- ✅ **결과 저장**: 분석 결과가 표시된 이미지 자동 저장

## 📋 요구사항

### 시스템 요구사항
- Python 3.7 이상
- CUDA 지원 GPU (선택사항, CPU에서도 실행 가능)

### 필수 패키지
```bash
pip install -r requirements.txt
```

포함된 패키지:
- `ultralytics` - YOLOv8 모델 실행
- `opencv-python` - 이미지 처리
- `numpy` - 수치 연산
- `matplotlib` - 그래프 생성
- `Pillow` - 이미지 로딩
- `torch` - PyTorch 프레임워크
- `torchvision` - 컴퓨터 비전 도구

## 🚀 사용법

### 1. 기본 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# 모델 확인
ls model_training/Dog_feature/best.pt
```

### 2. 단일 이미지 분석

```bash
# 기본 분석 (신뢰도 0.5)
python dog_feature_analyzer.py --image path/to/your/dog_image.jpg

# 신뢰도 조정 (더 민감하게)
python dog_feature_analyzer.py --image path/to/your/dog_image.jpg --conf 0.3

# 다른 모델 사용
python dog_feature_analyzer.py --image path/to/your/dog_image.jpg --model path/to/your/model.pt
```

### 3. 폴더 내 모든 이미지 분석

```bash
# 폴더 일괄 분석
python dog_feature_analyzer.py --folder path/to/image_folder

# 신뢰도 조정하여 분석
python dog_feature_analyzer.py --folder path/to/image_folder --conf 0.4
```

### 4. 테스트 실행

```bash
# test_images 폴더에 이미지를 넣고 실행
python dog_feature_analyzer.py

# 또는 예제 스크립트 실행
python example_usage.py
```

## 📊 출력 결과

### 콘솔 출력 예시
```
==================================================
이미지: dog_sample.jpg
==================================================
총 감지된 특징: 3개

[감지된 특징 목록]
1. nose (신뢰도: 0.85)
   위치: (145, 120) - (180, 155)
2. eye (신뢰도: 0.78)
   위치: (130, 100) - (150, 120)
3. ear (신뢰도: 0.72)
   위치: (120, 80) - (160, 110)

[클래스별 요약]
- nose: 1개
- eye: 1개  
- ear: 1개
```

### 결과 이미지
- 분석된 이미지는 `results/` 폴더에 저장됩니다
- 원본 파일명에 `_analyzed` 접미사가 추가됩니다
- 감지된 특징은 초록색 바운딩 박스로 표시됩니다

## 🔧 매개변수 설명

| 매개변수 | 설명 | 기본값 | 예시 |
|---------|-----|-------|------|
| `--image` | 분석할 단일 이미지 경로 | - | `--image dog.jpg` |
| `--folder` | 분석할 이미지 폴더 경로 | - | `--folder ./images` |
| `--model` | YOLOv8 모델 파일 경로 | `model_training/Dog_feature/best.pt` | `--model custom_model.pt` |
| `--conf` | 신뢰도 임계값 (0.0-1.0) | `0.5` | `--conf 0.3` |

## 📁 프로젝트 구조

```
├── dog_feature_analyzer.py     # 메인 분석기 클래스
├── example_usage.py           # 사용 예제 스크립트
├── requirements.txt           # 필수 패키지 목록
├── model_training/
│   └── Dog_feature/
│       └── best.pt           # YOLOv8n 모델 파일
├── test_images/              # 테스트 이미지 폴더
└── results/                  # 분석 결과 이미지 저장 폴더
```

## 🎯 지원되는 이미지 형식

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- BMP (`.bmp`)
- TIFF (`.tiff`)
- WebP (`.webp`)

## ⚙️ 성능 최적화 팁

1. **GPU 사용**: CUDA가 설치된 경우 자동으로 GPU를 사용합니다
2. **신뢰도 조정**: 
   - 높은 신뢰도 (0.7-0.9): 확실한 특징만 감지
   - 낮은 신뢰도 (0.2-0.4): 더 많은 특징 감지 (노이즈 증가 가능)
3. **배치 처리**: 여러 이미지는 배치 분석이 더 효율적입니다

## 🔍 문제 해결

### 일반적인 오류

1. **모델 로드 실패**
   ```
   [ERROR] 모델 로드 실패: [Errno 2] No such file or directory
   ```
   - 해결: 모델 파일 경로를 확인하세요
   - `model_training/Dog_feature/best.pt` 파일이 존재하는지 확인

2. **이미지 읽기 실패**
   ```
   [ERROR] 이미지를 읽을 수 없습니다
   ```
   - 해결: 이미지 파일 경로와 형식을 확인하세요
   - 지원되는 형식인지 확인

3. **감지된 특징이 없음**
   ```
   [INFO] 감지된 특징이 없습니다
   ```
   - 해결: `--conf` 매개변수로 신뢰도를 낮춰보세요 (예: `--conf 0.2`)

### 성능 문제

- CPU에서 실행이 느린 경우: GPU 환경 사용 권장
- 메모리 부족: 이미지 크기가 너무 큰 경우 리사이징 고려

## 📈 개발자 정보

이 도구는 YOLOv8n 모델을 기반으로 하며, 강아지의 다양한 특징(코, 눈, 귀 등)을 감지하도록 훈련되었습니다.

### 클래스 구조
```python
# 메인 클래스 사용 예시
from dog_feature_analyzer import DogFeatureAnalyzer

analyzer = DogFeatureAnalyzer("model_training/Dog_feature/best.pt")
result = analyzer.analyze_image("dog.jpg", conf_threshold=0.5)
```

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 사용할 수 있습니다.

## 🤝 기여 방법

1. 이슈 리포트: 버그나 개선사항을 Issues에 등록
2. 기능 제안: 새로운 기능에 대한 아이디어 공유
3. 코드 기여: Pull Request를 통한 코드 개선

---

**Happy Dog Analysis! 🐕✨** 