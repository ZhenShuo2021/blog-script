# Remove characters after last "_"

import os
import sys
from pathlib import Path
from datetime import datetime

def rename_files_remove_suffix(directory):
    files = list(directory.glob("*"))

    for file_path in files:
        if file_path.is_file() and not file_path.name.startswith('.'):
            # 獲取檔案名稱和副檔名
            name, ext = os.path.splitext(file_path.name)
            
            # 找到最後一個 "_" 並截斷
            if "_" in name:
                name = name.rsplit("_", 1)[0]
            
            # 獲取檔案的修改時間並格式化
            mtime = file_path.stat().st_mtime
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            # 新的檔名
            new_name = f"{date_str}_{name}{ext}"
            new_file_path = file_path.parent / new_name

            # 確保新的檔名不存在
            if not new_file_path.exists():
                os.rename(file_path, new_file_path)
                print(f"Renamed {file_path} to {new_file_path}")

                # 將修改時間寫回檔案
                os.utime(new_file_path, (mtime, mtime))
            else:
                print(f"File {new_file_path} already exists. Skipping.")
        else:
            print(f"No '_' found in {file_path.name}. Skipping.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 rm_remove_suffix.py <path>")
        sys.exit(1)

    input_directory = Path(sys.argv[1])
    if input_directory.is_dir():
        rename_files_remove_suffix(input_directory)
    else:
        print(f"Invalid directory: {input_directory}")
        sys.exit(1)
