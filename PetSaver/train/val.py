import os
import shutil
import random

def split_dataset(base_dir, output_dir='dog_species_dataset', train_ratio=0.8):
    classes = os.listdir(base_dir)
    for cls in classes:
        img_dir = os.path.join(base_dir, cls)
        images = [f for f in os.listdir(img_dir) if f.lower().endswith(('jpg', 'png'))]
        random.shuffle(images)
        train_count = int(len(images) * train_ratio)

        for phase in ['train', 'val']:
            phase_dir = os.path.join(output_dir, phase, cls)
            os.makedirs(phase_dir, exist_ok=True)

        for i, img in enumerate(images):
            src = os.path.join(img_dir, img)
            dst_dir = 'train' if i < train_count else 'val'
            dst = os.path.join(output_dir, dst_dir, cls, img)
            shutil.copy(src, dst)

    print(f"[✓] {train_ratio*100:.0f}% train / {(1-train_ratio)*100:.0f}% val 분리 완료")

# 사용 예
split_dataset(base_dir='all_dog_species_images')
