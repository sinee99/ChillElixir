import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.optim import Adam
from sklearn.metrics import accuracy_score

# ✅ 전처리 정의
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ✅ 데이터셋 불러오기
train_data = datasets.ImageFolder(root='../../dataset/species/train', transform=transform)
val_data = datasets.ImageFolder(root='../../dataset/species/val', transform=transform)

train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
val_loader = DataLoader(val_data, batch_size=32)

# ✅ 모델 정의
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, len(train_data.classes))
model = model.to(device)

# ✅ 학습 설정
criterion = nn.CrossEntropyLoss()
optimizer = Adam(model.parameters(), lr=0.0001)

# ✅ 학습 루프
for epoch in range(10):
    model.train()
    total_loss = 0
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"[Epoch {epoch+1}] Loss: {total_loss:.4f}")

    # 검증
    model.eval()
    preds, trues = [], []
    with torch.no_grad():
        for x, y in val_loader:
            x = x.to(device)
            out = model(x)
            preds += out.argmax(1).cpu().tolist()
            trues += y.tolist()

    acc = accuracy_score(trues, preds)
    print(f"Validation Accuracy: {acc * 100:.2f}%")

# ✅ 모델 저장
torch.save(model.state_dict(), 'dog_species_classifier.pt')
print("[✓] 종 분류기 저장 완료: dog_species_classifier.pt")
