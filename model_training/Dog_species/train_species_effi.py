import os
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
from tqdm import tqdm

# 설정
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 1e-5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TRAIN_DIR = 'dataset/species/train'
VAL_DIR = 'dataset/species/val'
CHECKPOINT_PATH = 'checkpoint.pth'


def main():
    # 1. 전처리
    transform_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])

    transform_val = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])

    # 2. 데이터셋
    train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=transform_train)
    val_dataset = datasets.ImageFolder(VAL_DIR, transform=transform_val)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=6, pin_memory=True, prefetch_factor=4, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE,
                            num_workers=6, pin_memory=True, prefetch_factor=4, persistent_workers=True)

    # 3. 클래스 가중치 및 손실 함수
    num_classes = len(train_dataset.classes)
    print(f"클래스 수: {num_classes}, 클래스 목록: {train_dataset.classes[:5]} ...")
    labels = train_dataset.targets
    class_weights = compute_class_weight('balanced', classes=np.unique(labels), y=labels)
    weights = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=weights)

    # 4. 모델

    # 1) 사전 학습 가중치 설정
    weights = EfficientNet_B0_Weights.DEFAULT

    # 2) 모델 정의
    model = efficientnet_b0(weights=weights)

    # 3) 분류기 수정
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model = model.to(DEVICE)

    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    # PyTorch 최신 버전에서는 verbose 사용 가능
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='max',
        factor=0.5,
        patience=2
    )

    # 5. 체크포인트 불러오기
    start_epoch = 0
    if os.path.exists(CHECKPOINT_PATH):
        checkpoint = torch.load(CHECKPOINT_PATH, map_location=DEVICE)
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
            start_epoch = checkpoint['epoch'] + 1
            print(f"🔄 체크포인트 로드 완료: {start_epoch} 에폭부터 재개합니다.")
        else:
            model.load_state_dict(checkpoint)
            print("⚠️ 단순 모델 가중치만 불러왔습니다. 에폭은 0부터 시작합니다.")
    else:
        print("🚨 체크포인트 없음: 처음부터 학습을 시작합니다.")

    # 6. 학습 루프
    for epoch in range(start_epoch, EPOCHS):
        model.train()
        total_loss = 0

        for images, labels in tqdm(train_loader, desc=f"[{epoch+1}/{EPOCHS}] Training", smoothing=0.1):
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1} - Loss: {avg_loss:.4f}")

        # 검증
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)

        acc = correct / total * 100
        scheduler.step(acc)  # 중요: ReduceLROnPlateau는 "성능"을 넣어야 작동함
        print(f"Validation Accuracy: {acc:.2f}%")

        # 체크포인트 저장
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
        }, CHECKPOINT_PATH)
        print(f"💾 체크포인트 저장 완료 (Epoch {epoch+1})")

    # 최종 모델 저장
    torch.save(model.state_dict(), "dog_breed_efficientnet_b0.pth")
    print("✅ 최종 모델이 저장되었습니다.")


if __name__ == "__main__":
    main()
