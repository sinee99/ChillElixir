import torch
from torchvision import models, transforms
from PIL import Image
import os

# 설정
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "dog_breed_efficientnet_b0.pth"
CLASS_DIR = "dataset/species/train"  # 학습 시 사용한 폴더 경로 (클래스 이름 추출용)

# 1. 클래스 이름 불러오기
class_names = sorted(os.listdir(CLASS_DIR))

# 2. 이미지 전처리
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

# 3. 모델 로드
def load_model():
    model = models.efficientnet_b0(pretrained=False)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(class_names))
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

# 4. 예측 함수 (Top-3)
def predict_image(image_path, model):
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)
        top_probs, top_indices = torch.topk(probs, k=3)  # Top-3 예측

    # 결과 정리
    results = []
    for i in range(3):
        class_name = class_names[top_indices[0][i].item()]
        confidence = top_probs[0][i].item() * 100
        results.append((class_name, confidence))

    return results


if __name__ == "__main__":
    # 테스트할 이미지 경로 지정
    test_image_path = "test_images/sample.jpg"  # 예: test_images/푸들1.jpg

    model = load_model()
    results = predict_image(test_image_path, model)

    print("✅ 예측 결과 (Top-3):")
    for i, (cls, prob) in enumerate(results, 1):
        print(f"{i}. {cls} ({prob:.2f}%)")
