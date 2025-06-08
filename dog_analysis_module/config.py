import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # 모델 설정
    MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/best.pt")
    
    # Firebase 설정
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "https://your-project.firebaseio.com/")
    
    # API 설정
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # 이미지 설정
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # YOLOv8 설정
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    
    # 강아지 특성 클래스 (실제 훈련된 클래스에 맞게 수정 필요)
    DOG_CLASSES = {
        0: "골든 리트리버",
        1: "래브라도",
        2: "불독",
        3: "치와와",
        4: "허스키",
        5: "진돗개",
        6: "포메라니안",
        7: "비글",
        8: "말티즈",
        9: "푸들"
    } 