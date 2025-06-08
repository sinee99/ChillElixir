import os
import torch
from ultralytics import YOLO
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import yaml

# 설정
EPOCHS = 20
LEARNING_RATE = 1e-5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TRAIN_DIR = 'dataset/species/train'
VAL_DIR = 'dataset/species/val'
MODEL_NAME = 'yolov8n-cls.pt'  # yolov8n-cls, yolov8s-cls, yolov8m-cls, yolov8l-cls, yolov8x-cls 중 선택

def create_yaml_config():
    """YOLOv8 분류 모델을 위한 YAML 설정 파일 생성"""
    # YOLOv8 분류 모델은 상대 경로를 사용하는 것이 더 안전함
    config = f"""
# YOLOv8 Classification Dataset Configuration
path: .  # dataset root dir
train: {TRAIN_DIR}  # train images (relative to 'path')
val: {VAL_DIR}  # val images (relative to 'path')

# Class names (optional, will be auto-detected from folder names)
"""
    
    config_file = 'dataset_config.yaml'
    with open(config_file, 'w') as f:
        f.write(config.strip())
    
    print(f"📝 YAML 설정 파일 생성: {config_file}")
    print(f"   - 훈련 데이터 경로: {TRAIN_DIR}")
    print(f"   - 검증 데이터 경로: {VAL_DIR}")
    
    # 경로 존재 확인
    if not os.path.exists(TRAIN_DIR):
        print(f"⚠️ 경고: 훈련 데이터 경로가 존재하지 않습니다: {TRAIN_DIR}")
    if not os.path.exists(VAL_DIR):
        print(f"⚠️ 경고: 검증 데이터 경로가 존재하지 않습니다: {VAL_DIR}")
    
    return config_file

def main():
    print(f"🚀 YOLOv8 분류 모델 훈련을 시작합니다.")
    print(f"Device: {DEVICE}")
    print(f"Model: {MODEL_NAME}")
    print(f"Epochs: {EPOCHS}")
    print(f"Learning Rate: {LEARNING_RATE}")
    
    # 데이터셋 설정 파일 생성
    config_path = create_yaml_config()
    
    # YOLOv8 모델 로드
    model = YOLO(MODEL_NAME)
    
    # 모델 훈련 - 데이터셋 경로를 직접 지정하는 방법도 시도
    try:
        # 방법 1: 직접 경로 지정
        print(f"🔍 방법 1: 직접 경로 지정으로 시도합니다...")
        results = model.train(
            data=TRAIN_DIR,  # 직접 train 폴더 경로 지정
            epochs=EPOCHS,
            lr0=LEARNING_RATE,
            imgsz=224,
            batch=32,
            device=str(DEVICE).replace('cuda', '0') if 'cuda' in str(DEVICE) else str(DEVICE),
            project='runs/classify',
            name='species_classification',
            exist_ok=True,
            plots=True,
            save=True,
            val=True,
            patience=10,
            workers=0 if os.name == 'nt' else 6,  # Windows에서는 workers=0 사용
            pretrained=True,
            optimizer='Adam',
            verbose=True,
            seed=42,
            deterministic=True,
            single_cls=False,
            save_period=5,  # 5 에폭마다 체크포인트 저장
        )
    except Exception as e1:
        print(f"❌ 방법 1 실패: {e1}")
        print(f"🔍 방법 2: YAML 설정 파일 사용으로 재시도합니다...")
        try:
            results = model.train(
                data=config_path,
                epochs=EPOCHS,
                lr0=LEARNING_RATE,
                imgsz=224,
                batch=32,
                device=str(DEVICE).replace('cuda', '0') if 'cuda' in str(DEVICE) else str(DEVICE),
                project='runs/classify',
                name='species_classification2',
                exist_ok=True,
                plots=True,
                save=True,
                val=True,
                patience=10,
                workers=0 if os.name == 'nt' else 6,
                pretrained=True,
                optimizer='Adam',
                verbose=True,
                seed=42,
                deterministic=True,
                single_cls=False,
                save_period=5,
            )
        except Exception as e2:
            print(f"❌ 방법 2도 실패: {e2}")
            print("💡 다음 사항을 확인해주세요:")
            print("   1. 데이터셋 폴더 구조가 올바른지 확인")
            print("   2. 이미지 파일들이 올바른 위치에 있는지 확인")
            print("   3. ultralytics 라이브러리가 최신 버전인지 확인: pip install -U ultralytics")
            return
    
    print("✅ YOLOv8 모델 훈련이 완료되었습니다.")
    
    # 훈련 결과 불러오기 및 그래프 생성
    try:
        results_dir = Path('runs/classify/species_classification')
        csv_file = results_dir / 'results.csv'
        
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            df.columns = df.columns.str.strip()  # 공백 제거
            
            # 훈련 손실 그래프
            plt.figure(figsize=(10, 6))
            if 'train/loss' in df.columns:
                plt.subplot(2, 2, 1)
                plt.plot(df.index + 1, df['train/loss'], marker='o', label='Train Loss')
                plt.title('Training Loss per Epoch')
                plt.xlabel('Epoch')
                plt.ylabel('Loss')
                plt.grid(True)
                plt.legend()
            
            # 검증 손실 그래프
            if 'val/loss' in df.columns:
                plt.subplot(2, 2, 2)
                plt.plot(df.index + 1, df['val/loss'], marker='o', label='Val Loss', color='orange')
                plt.title('Validation Loss per Epoch')
                plt.xlabel('Epoch')
                plt.ylabel('Loss')
                plt.grid(True)
                plt.legend()
            
            # Top-1 정확도 그래프
            if 'metrics/accuracy_top1' in df.columns:
                plt.subplot(2, 2, 3)
                plt.plot(df.index + 1, df['metrics/accuracy_top1'] * 100, marker='o', label='Top-1 Accuracy', color='green')
                plt.title('Top-1 Accuracy per Epoch')
                plt.xlabel('Epoch')
                plt.ylabel('Accuracy (%)')
                plt.grid(True)
                plt.legend()
            
            # Top-5 정확도 그래프
            if 'metrics/accuracy_top5' in df.columns:
                plt.subplot(2, 2, 4)
                plt.plot(df.index + 1, df['metrics/accuracy_top5'] * 100, marker='o', label='Top-5 Accuracy', color='red')
                plt.title('Top-5 Accuracy per Epoch')
                plt.xlabel('Epoch')
                plt.ylabel('Accuracy (%)')
                plt.grid(True)
                plt.legend()
            
            plt.tight_layout()
            plt.savefig('yolov8_training_results.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("📊 훈련 결과 그래프가 저장되었습니다: yolov8_training_results.png")
            
            # 최종 결과 출력
            if len(df) > 0:
                final_row = df.iloc[-1]
                print("\n🎯 최종 훈련 결과:")
                if 'train/loss' in df.columns:
                    print(f"   - 최종 훈련 손실: {final_row['train/loss']:.4f}")
                if 'val/loss' in df.columns:
                    print(f"   - 최종 검증 손실: {final_row['val/loss']:.4f}")
                if 'metrics/accuracy_top1' in df.columns:
                    print(f"   - Top-1 정확도: {final_row['metrics/accuracy_top1']*100:.2f}%")
                if 'metrics/accuracy_top5' in df.columns:
                    print(f"   - Top-5 정확도: {final_row['metrics/accuracy_top5']*100:.2f}%")
        else:
            print("⚠️ 결과 CSV 파일을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"⚠️ 그래프 생성 중 오류 발생: {e}")
    
    # 모델 정보 출력
    model_path = results_dir / 'weights' / 'best.pt'
    if model_path.exists():
        print(f"🎯 최고 성능 모델 저장 위치: {model_path}")
    
    # 검증 수행
    print("\n🔍 최종 검증을 수행합니다...")
    validation_results = model.val(data=config_path, device=DEVICE)
    
    print("✅ 모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main() 