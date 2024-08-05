# Rename file: "AAA_idxxxxx_BBB" -> "idxxxxx_AAA_BBB"

import os
import sys
from pathlib import Path
import re

def rename_files_move_id_block(directory):
    files = list(directory.glob("*"))

    for file_path in files:
        if file_path.is_file() and not file_path.name.startswith('.'):
            # 獲取檔案名稱和副檔名
            name, ext = os.path.splitext(file_path.name)
            
            # 使用正則表達式找到第一個 "_id" 區塊
            match = re.search(r"(_id\d+)", name)
            if match:
                id_block = match.group(1)
                parts = name.split(id_block)
                
                if len(parts) == 2:
                    new_name = f"{id_block[1:]}_{parts[0]}{parts[1]}{ext}"
                    new_file_path = file_path.parent / new_name

                    # 確保新的檔名不存在
                    if not new_file_path.exists():
                        os.rename(file_path, new_file_path)
                        print(f"Renamed {file_path} to {new_file_path}")
                    else:
                        print(f"File {new_file_path} already exists. Skipping.")
            else:
                print(f"No '_id' block found in {file_path.name}. Skipping.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 rm.py <path>")
        sys.exit(1)

    input_directory = Path(sys.argv[1])
    if input_directory.is_dir():
        rename_files_move_id_block(input_directory)
    else:
        print(f"Invalid directory: {input_directory}")
        sys.exit(1)
