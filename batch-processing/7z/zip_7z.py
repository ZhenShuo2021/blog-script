import os
import subprocess
import shutil

def compress_folder(folder_path):
    parent_folder = os.path.dirname(folder_path)
    folder_name = os.path.basename(folder_path)
    output_path = os.path.join(parent_folder, f"{folder_name}.7z")

    # 使用 7z 命令進行壓縮
    subprocess.run(['7z', 'a', output_path, folder_path])
    print(f"Compressed {folder_path} to {output_path}")

def main(parent_folder):
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path):
            compress_folder(folder_path)

if __name__ == "__main__":
    # 替換成你的父資料夾路徑
    parent_folder = "/Users/leo/gallery-dl/"
    main(parent_folder)
