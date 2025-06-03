import os
import shutil
import random

# 설정
train_dir = "dataset/species/train"
val_dir = "dataset/species/val"
val_ratio = 0.2  # 검증 데이터 비율 (예: 20%)

# 클래스별로 처리
for class_name in os.listdir(train_dir):
    class_path = os.path.join(train_dir, class_name)
    if not os.path.isdir(class_path):
        continue

    images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(images)
    val_count = int(len(images) * val_ratio)

    val_class_path = os.path.join(val_dir, class_name)
    os.makedirs(val_class_path, exist_ok=True)

    for img_name in images[:val_count]:
        src = os.path.join(class_path, img_name)
        dst = os.path.join(val_class_path, img_name)

        # 파일 이름 충돌 방지
        if os.path.exists(dst):
            base, ext = os.path.splitext(img_name)
            i = 1
            while os.path.exists(os.path.join(val_class_path, f"{base}_{i}{ext}")):
                i += 1
            dst = os.path.join(val_class_path, f"{base}_{i}{ext}")

        shutil.move(src, dst)

    print(f"[✓] {class_name}: {val_count}개 이동 완료")
