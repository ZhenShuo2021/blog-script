import os
import re

def rename_item0(directory, item):
    pattern = re.compile(r"^{(\d+)}\s+(.+?)(\..+)?$")

    match = pattern.match(item)
    if match:
        number, name, extension = match.groups()

        if extension:
            new_name = f" {name} {{{number}}}{extension}"
        else:
            # 資料夾
            new_name = f" {name} {{{number}}}"

        old_path = os.path.join(directory, item)
        new_path = os.path.join(directory, new_name)

        try:
            os.rename(old_path, new_path)
            print(f"已重命名:\n{item}\n{new_name}\nEOF")
        except OSError as e:
            print(f"重命名 {item} 時發生錯誤: {e}")

def rename_item(directory, item):
    pattern = re.compile(r"^(.*?)\s*\((\d+)\)(\..+)?$")

    match = pattern.match(item)
    if match:
        name, number, extension = match.groups()

        name = name.strip()

        if extension:
            new_name = f"{{{number}}} {name}{extension}"
        else:
            # 資料夾
            new_name = f"{{{number}}} {name}"

        old_path = os.path.join(directory, item)
        new_path = os.path.join(directory, new_name)

        try:
            os.rename(old_path, new_path)
            print(f"已重命名:\n{item}\n{new_name}\nEOF")
        except OSError as e:
            print(f"重命名 {item} 時發生錯誤: {e}")

if __name__ == "__main__":
    directory = input("請輸入要處理的路徑: ")
    if os.path.isdir(directory):
        for item in os.listdir(directory):
            rename_item(directory, item)
    else:
        print("無效的路徑。")
