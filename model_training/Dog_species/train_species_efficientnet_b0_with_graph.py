import os
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

# 설정
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 1e-5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TRAIN_DIR = 'dataset/species/train'
VAL_DIR = 'dataset/species/val'
CHECKPOINT_PATH = 'checkpoint.pth'


def main():
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

    train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=transform_train)
    val_dataset = datasets.ImageFolder(VAL_DIR, transform=transform_val)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=6, pin_memory=True, prefetch_factor=4, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE,
                            num_workers=6, pin_memory=True, prefetch_factor=4, persistent_workers=True)

    num_classes = len(train_dataset.classes)
    print(f"클래스 수: {num_classes}, 클래스 목록: {train_dataset.classes[:5]} ...")
    labels = train_dataset.targets
    class_weights = compute_class_weight('balanced', classes=np.unique(labels), y=labels)
    weights = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=weights)

    weights_enum = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights_enum)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model = model.to(DEVICE)

    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

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

    train_losses = []
    val_accuracies = []

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
        train_losses.append(avg_loss)
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
        val_accuracies.append(acc)
        scheduler.step(acc)
        print(f"Validation Accuracy: {acc:.2f}%")

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

    # 학습 결과 그래프 저장
    epochs_range = list(range(start_epoch + 1, EPOCHS + 1))

    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, train_losses, marker='o')
    plt.title("Training Loss per Epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("training_loss_graph.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(epochs_range, val_accuracies, marker='o')
    plt.title("Validation Accuracy per Epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("validation_accuracy_graph.png")
    plt.close()

    print("📊 그래프가 저장되었습니다: training_loss_graph.png, validation_accuracy_graph.png")


if __name__ == "__main__":
    main()
