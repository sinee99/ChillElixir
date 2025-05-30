# ✅ main.py (최종 버전: 종 분류 + 코 임베딩 저장/검색)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io, torch, uuid, numpy as np
from torchvision import models, transforms
from ultralytics import YOLO
from firebase_admin import credentials, initialize_app, storage, firestore
import faiss

# 앱 및 미들웨어 초기화
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 초기화
cred = credentials.Certificate("firebase_key.json")
initialize_app(cred, {"storageBucket": "your-bucket-name.appspot.com"})
db = firestore.client()

# 모델 및 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
yolo_model = YOLO("yolov8n.pt")
species_model = models.resnet18()
species_model.fc = torch.nn.Linear(species_model.fc.in_features, 119)  # 119 클래스 기준으로 수정
species_model.load_state_dict(torch.load("dog_species_classifier.pt", map_location=device))
species_model.eval().to(device)

# 클래스 목록 불러오기
with open("class_names.txt", "r") as f:
    target_classes = [line.strip() for line in f.readlines()]

# 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# 임베딩 모델
class Embedder(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.feature = torch.nn.Sequential(*list(models.resnet18(pretrained=True).children())[:-1])

    def forward(self, x):
        x = self.feature(x)
        return x.view(x.size(0), -1)

embedder = Embedder().to(device).eval()

# FAISS 설정
index = faiss.IndexFlatL2(512)
embedding_map = {}  # idx -> UID 매핑

# 🐶 분석 엔드포인트
@app.post("/analyze")
async def analyze_dog(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    np_img = np.array(image)

    results = yolo_model(np_img)
    boxes = [b for b in results[0].boxes if int(b.cls[0]) == 16]  # class 16 = dog
    if len(boxes) != 1:
        return {"error": f"강아지 수: {len(boxes)}. 1마리만 포함된 이미지를 업로드해주세요."}

    x1, y1, x2, y2 = map(int, boxes[0].xyxy[0].tolist())
    w, h = x2 - x1, y2 - y1
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    side = max(w, h)
    box = [max(0, cx - side//2), max(0, cy - side//2), min(image.width, cx + side//2), min(image.height, cy + side//2)]
    dog_crop = image.crop(box)

    # 코 영역 crop
    nose_cx, nose_cy = cx, y2 - int(h * 0.2)
    nose_side = int(min(w, h) * 0.2)
    nose_box = [max(0, nose_cx - nose_side//2), max(0, nose_cy - nose_side//2), min(image.width, nose_cx + nose_side//2), min(image.height, nose_cy + nose_side//2)]
    nose_crop = image.crop(nose_box)

    uid = str(uuid.uuid4())
    dog_crop.save("tmp_dog.jpg")
    nose_crop.save("tmp_nose.jpg")

    # Firebase 업로드
    bucket = storage.bucket()
    blob1 = bucket.blob(f"cropped/{uid}_dog.jpg")
    blob1.upload_from_filename("tmp_dog.jpg")
    blob2 = bucket.blob(f"cropped/{uid}_nose.jpg")
    blob2.upload_from_filename("tmp_nose.jpg")

    # 종 분류
    species_tensor = transform(dog_crop).unsqueeze(0).to(device)
    species = target_classes[species_model(species_tensor).argmax(1).item()]

    # 코 임베딩 저장
    nose_tensor = transform(nose_crop).unsqueeze(0).to(device)
    emb = embedder(nose_tensor).cpu().numpy()
    index.add(emb)
    embedding_map[index.ntotal - 1] = uid

    db.collection("dogs").document(uid).set({
        "species": species,
        "dog_img_url": blob1.public_url,
        "nose_img_url": blob2.public_url
    })

    return {
        "uid": uid,
        "species": species,
        "dog_img_url": blob1.public_url,
        "nose_img_url": blob2.public_url
    }

# 🔍 유실견 검색
@app.post("/match")
async def match_dog(file: UploadFile = File(...)):
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)
    query_emb = embedder(tensor).cpu().numpy()
    D, I = index.search(query_emb, 3)
    matches = [embedding_map[i] for i in I[0] if i in embedding_map]
    return {"matches": matches}

# 🔧 관리자 API
@app.get("/admin/list")
def list_dogs():
    docs = db.collection("dogs").stream()
    return [{**doc.to_dict(), "uid": doc.id} for doc in docs]

@app.delete("/admin/delete/{uid}")
def delete_dog(uid: str):
    db.collection("dogs").document(uid).delete()
    return {"deleted": uid}
