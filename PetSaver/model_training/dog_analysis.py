import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.optim import Adam
from sklearn.metrics import accuracy_score

# ✅ 데이터 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ✅ 데이터셋 로딩
dataset_path = "dog_species_dataset"
train_data = datasets.ImageFolder(root=os.path.join(dataset_path, "train"), transform=transform)
val_data = datasets.ImageFolder(root=os.path.join(dataset_path, "val"), transform=transform)

train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
val_loader = DataLoader(val_data, batch_size=32)

# ✅ 모델 정의 (ResNet18)
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

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")

    # 🔍 검증 정확도
    model.eval()
    preds, trues = [], []
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            preds += outputs.argmax(1).cpu().tolist()
            trues += labels.tolist()

    acc = accuracy_score(trues, preds)
    print(f"Validation Accuracy: {acc*100:.2f}%")

# ✅ 모델 저장
torch.save(model.state_dict(), "dog_species_classifier.pt")
print("[✓] 모델 저장 완료: dog_species_classifier.pt")
