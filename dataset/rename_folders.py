import os
import shutil

base_path = "dataset/species/train"
rename_log = []

for folder in os.listdir(base_path):
    folder_path = os.path.join(base_path, folder)

    if os.path.isdir(folder_path) and '-' in folder:
        new_name = folder.split('-')[-1]
        new_path = os.path.join(base_path, new_name)

        if os.path.exists(new_path):
            print(f"⚠️ 폴더 병합: {folder} → {new_name}")
            for filename in os.listdir(folder_path):
                src_file = os.path.join(folder_path, filename)
                dst_file = os.path.join(new_path, filename)

                # 동일한 이름의 파일이 이미 있으면 이름 바꿔 저장
                if os.path.exists(dst_file):
                    base, ext = os.path.splitext(filename)
                    i = 1
                    while os.path.exists(os.path.join(new_path, f"{base}_{i}{ext}")):
                        i += 1
                    dst_file = os.path.join(new_path, f"{base}_{i}{ext}")

                shutil.move(src_file, dst_file)

            # 병합 후 원본 폴더 제거
            os.rmdir(folder_path)
        else:
            os.rename(folder_path, new_path)

        rename_log.append((folder, new_name))

# 결과 요약
print("\n📋 변경 요약:")
for old, new in rename_log:
    print(f" - {old} → {new}")
