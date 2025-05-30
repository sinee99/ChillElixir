import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import accuracy_score
from tqdm import tqdm

# 하이퍼파라미터
BATCH_SIZE = 32
EPOCHS = 100
LEARNING_RATE = 1e-5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# 데이터셋 경로
train_path = "dataset/species/train"
val_path = "dataset/species/val"

# 데이터셋 로드
train_dataset = datasets.ImageFolder(train_path, transform=transform)
val_dataset = datasets.ImageFolder(val_path, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

# 클래스 정보 출력
print(f"클래스 수: {len(train_dataset.classes)}")
print("클래스 목록:", train_dataset.classes)

# 모델 설정
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, len(train_dataset.classes))
model = model.to(DEVICE)

# 손실 함수 & 옵티마이저
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

# 학습 루프
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    print(f"\n🔄 Epoch {epoch+1}/{EPOCHS}")
    for x, y in tqdm(train_loader, desc="Training", leave=False):
        x, y = x.to(DEVICE), y.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(x)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"🟢 Train Loss: {total_loss:.4f}")

    # 검증
    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for x, y in tqdm(val_loader, desc="Validating", leave=False):
            x = x.to(DEVICE)
            outputs = model(x)
            preds = outputs.argmax(1).cpu().numpy()
            y_pred.extend(preds)
            y_true.extend(y.numpy())

    acc = accuracy_score(y_true, y_pred)
    print(f"✅ Validation Accuracy: {acc:.4f}")

# 모델 저장
torch.save(model.state_dict(), "dog_species_classifier.pt")
print("✅ 모델 저장 완료: dog_species_classifier.pt")
