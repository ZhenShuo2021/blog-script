# Move files to parent folder
import os
import shutil
import sys

def move_files_to_parent_dir(parent_dir):
    # 檢查目標目錄是否存在
    if not os.path.isdir(parent_dir):
        print(f"The directory {parent_dir} does not exist.")
        return

    # 遍歷目標目錄下的所有子資料夾
    for root, dirs, files in os.walk(parent_dir):
        # 排除目標目錄本身
        if root == parent_dir:
            continue
        
        # 移動檔案到目標目錄
        for file in files:
            src_path = os.path.join(root, file)
            dest_path = os.path.join(parent_dir, file)
            
            # 防止覆蓋已有的同名檔案
            if os.path.exists(dest_path):
                print(f"File {dest_path} already exists, skipping {src_path}")
                continue
            
            print(f"Moving {src_path} to {dest_path}")
            shutil.move(src_path, dest_path)
        
        # 刪除空的子資料夾
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                print(f"Removing empty directory {dir_path}")
                os.rmdir(dir_path)

    # 最後再一次檢查，刪除所有可能已經變成空的資料夾
    for root, dirs, files in os.walk(parent_dir):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                print(f"Removing empty directory {dir_path}")
                os.rmdir(dir_path)

def main():
    if len(sys.argv) != 2:
        print("Usage: ./move.py /path/to/dir")
        return
    
    parent_dir = sys.argv[1]
    move_files_to_parent_dir(parent_dir)

if __name__ == "__main__":
    main()
