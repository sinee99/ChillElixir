import os
from ultralytics import YOLO
from PIL import Image

# 설정
input_image_path = 'dog_sample.jpg'
output_dir = 'cropped_dogs_square'
os.makedirs(output_dir, exist_ok=True)

# 모델 로드 (사전학습된 COCO YOLOv8n)
model = YOLO('yolov8n.pt')

# 이미지 감지
results = model(input_image_path)
image = Image.open(input_image_path)

# 감지된 강아지(boxes) 필터링
boxes = [
    box for box in results[0].boxes
    if int(box.cls[0]) == 16 and float(box.conf[0]) > 0.5  # class 16 = dog
]

# 강아지가 1마리일 때만 crop 진행
if len(boxes) != 1:
    print(f"[!] 감지된 강아지 수: {len(boxes)}. 사진을 다시 찍어주세요.")
else:
    box = boxes[0]
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    
    # 정사각형 보정
    box_width = x2 - x1
    box_height = y2 - y1
    side_length = max(box_width, box_height)
    
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    # 정사각형 좌표 계산
    half_side = side_length // 2
    crop_x1 = max(center_x - half_side, 0)
    crop_y1 = max(center_y - half_side, 0)
    crop_x2 = min(center_x + half_side, image.width)
    crop_y2 = min(center_y + half_side, image.height)
    
    # crop 및 저장
    cropped_img = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
    save_path = os.path.join(output_dir, 'dog_square.jpg')
    cropped_img.save(save_path)
    print(f"[✓] 1마리 감지됨. 정사각형 crop 저장 완료 → {save_path}")
