import os
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
from tqdm import tqdm


# 전역 설정
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 1e-5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TRAIN_DIR = 'dataset/species/train'
VAL_DIR = 'dataset/species/val'


def main():
    # 1. 데이터 전처리
    transform_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.5] * 3, [0.5] * 3)
    ])

    transform_val = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.5] * 3, [0.5] * 3)
    ])

    # 2. 데이터셋 및 DataLoader
    train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=transform_train)
    val_dataset = datasets.ImageFolder(VAL_DIR, transform=transform_val)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=8, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE,
                            num_workers=8, pin_memory=True)

    num_classes = len(train_dataset.classes)
    print(f"클래스 수: {num_classes}, 클래스 목록: {train_dataset.classes[:5]} ...")

    # 3. 클래스 가중치 계산
    labels = train_dataset.targets
    class_weights = compute_class_weight('balanced', classes=np.unique(labels), y=labels)
    weights = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=weights)

    # 4. EfficientNet-B0 모델 불러오기
    model = models.efficientnet_b0(pretrained=True)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model = model.to(DEVICE)

    for param in model.parameters():
        param.requires_grad = True

    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

    # 5. 학습 루프
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0

        for images, labels in tqdm(train_loader, desc=f"[{epoch+1}/{EPOCHS}] Training"):
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
        scheduler.step(acc)
        print(f"Validation Accuracy: {acc:.2f}%")

    # 모델 저장
    torch.save(model.state_dict(), "dog_breed_efficientnet_b0.pth")
    print("✅ 모델이 저장되었습니다.")


if __name__ == "__main__":
    main()
