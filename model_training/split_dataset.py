import os
import shutil
import random

def split_dataset(base_dir, output_dir, train_ratio=0.8):
    """
    base_dir: 분할 전 원본 이미지 폴더 (ex. dataset/species_raw/)
    output_dir: 결과 저장 경로 (ex. dataset/species/)
    train_ratio: 학습용 데이터 비율
    """
    classes = os.listdir(base_dir)
    for cls in classes:
        cls_path = os.path.join(base_dir, cls)
        if not os.path.isdir(cls_path):
            continue

        images = [f for f in os.listdir(cls_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(images)
        train_count = int(len(images) * train_ratio)

        # train/val 디렉토리 생성
        for split in ['train', 'val']:
            os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)

        # 이미지 복사
        for i, img in enumerate(images):
            src_path = os.path.join(cls_path, img)
            if i < train_count:
                dst_path = os.path.join(output_dir, 'train', cls, img)
            else:
                dst_path = os.path.join(output_dir, 'val', cls, img)
            shutil.copyfile(src_path, dst_path)

        print(f"[✓] {cls} 클래스 분할 완료: train={train_count}, val={len(images) - train_count}")

if __name__ == "__main__":
    # 종 데이터셋 예시
    split_dataset(
        base_dir='../../dataset/species_raw',
        output_dir='../../dataset/species',
        train_ratio=0.8
    )

    # nose 데이터셋도 동일하게 사용할 수 있음 (클래스별 폴더 구성 시)
    # split_dataset('../../dataset/nose_raw', '../../dataset/nose', 0.8)
