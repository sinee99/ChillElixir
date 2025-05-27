import os
from ultralytics import YOLO
from PIL import Image
import torch

# 경로 설정
input_image_path = 'images.jpg'       # 분석할 이미지 파일
output_dir = 'cropped_dogs'               # crop된 이미지 저장 경로

# 결과 저장 폴더 생성
os.makedirs(output_dir, exist_ok=True)

# 모델 로드 (COCO 사전 학습 모델)
model = YOLO('yolov8n.pt')  # ultralytics에서 COCO class 포함된 모델

# 이미지 감지
results = model(input_image_path)

# 이미지 열기
image = Image.open(input_image_path)

# 감지 결과에서 강아지(Bounding Box)만 Crop
for result_idx, result in enumerate(results):
    boxes = result.boxes
    for box_idx, box in enumerate(boxes):
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        # COCO class 16: 'dog'
        if cls_id == 16 and conf > 0.5:  # 신뢰도 임계값 조정 가능
            # bounding box 좌표 가져오기
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # crop 및 저장
            cropped_img = image.crop((x1, y1, x2, y2))
            cropped_path = os.path.join(output_dir, f'dog_{result_idx}_{box_idx}.jpg')
            cropped_img.save(cropped_path)
            print(f"[✓] Saved: {cropped_path}")

print("완료: 감지된 강아지 이미지가 crop 되어 저장되었습니다.")
