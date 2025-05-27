# filename: api.py

from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io
import torch
from torchvision import models, transforms

app = FastAPI()

# 모델 로드
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, 3)  # 클래스 수 맞게 수정
model.load_state_dict(torch.load("dog_species_classifier.pt", map_location=device))
model.eval().to(device)

# 클래스 이름 리스트 (train_data.classes와 동일하게 맞춰야 함)
CLASS_NAMES = ['maltese', 'shiba_inu', 'golden_retriever']  # 예시

# 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

@app.post("/predict_species")
async def predict_species(file: UploadFile = File(...)):
    img_bytes = await file.read()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(img_tensor)
        pred = output.argmax(1).item()
        species = CLASS_NAMES[pred]

    return {"species": species}
