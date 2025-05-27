import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torch.optim import Adam
from sklearn.metrics import f1_score
import numpy as np

# ✅ 다중 라벨용 커스텀 데이터셋 로더 (ImageFolder 기반 수정 필요 시 확장 가능)

# ✅ 전처리 정의
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ✅ 클래스 정의
NOSE_FEATURES = ["dark_skin", "large_nostril", "right_scar", "pink_tone", "triangular"]
NUM_FEATURES = len(NOSE_FEATURES)

# ✅ 데이터셋 로딩 (클래스별 폴더 대신 CSV 또는 수동 텐서 라벨링 필요할 수 있음)
# 임시 구조: ImageFolder + 수동 다중 라벨
train_dataset = ImageFolder(root='../../dataset/nose/train', transform=transform)
val_dataset = ImageFolder(root='../../dataset/nose/val', transform=transform)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

# ✅ 모델 정의
class NoseFeatureClassifier(nn.Module):
    def __init__(self, num_features):
        super().__init__()
        base = models.resnet18(pretrained=True)
        self.model = nn.Sequential(
            *list(base.children())[:-1],       # Global average pooling
            nn.Flatten(),
            nn.Linear(base.fc.in_features, 256),
            nn.ReLU(),
            nn.Linear(256, num_features),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = NoseFeatureClassifier(NUM_FEATURES).to(device)

# ✅ 학습 설정
criterion = nn.BCELoss()
optimizer = Adam(model.parameters(), lr=0.0001)

# ✅ 학습 루프
for epoch in range(10):
    model.train()
    total_loss = 0
    for x, _ in train_loader:
        x = x.to(device)
        y = torch.randint(0, 2, (x.size(0), NUM_FEATURES)).float().to(device)  # 예시용 랜덤 라벨 (실제 라벨로 교체 필요)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"[Epoch {epoch+1}] Loss: {total_loss:.4f}")

    # 검증 (랜덤 라벨이므로 의미 없음)
    model.eval()
    preds, trues = [], []
    with torch.no_grad():
        for x, _ in val_loader:
            x = x.to(device)
            y_true = torch.randint(0, 2, (x.size(0), NUM_FEATURES)).float()  # 예시 라벨
            out = model(x).cpu()
            preds.extend((out > 0.5).int().tolist())
            trues.extend(y_true.tolist())

    score = f1_score(trues, preds, average='micro')
    print(f"Val F1 (dummy): {score:.4f}")

# ✅ 모델 저장
torch.save(model.state_dict(), 'dog_nose_classifier.pt')
print("[✓] 코 특징 분류기 저장 완료: dog_nose_classifier.pt")
