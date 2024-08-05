# 幫檔案自動分類到資料夾
import os
import shutil
import sys
import subprocess
from tool import is_system_file, is_english, is_japanese, color_text, local, remote
from conf import bluearchive_tags, idolmaster_tags, idolmaster_path_child
from datetime import datetime

# Parameters
# 在 main 中修改

# Functions
def sync_folders(source, destination):
    if not os.path.exists(source):
        print(color_text(f"警告：來源位置 '{source}' 不存在，程式結束", "red"))
        os.makedirs(source)
        # return

    if not os.path.exists(destination):
        print(color_text(f"警告：目標位置 '{destination}' 不存在，已自動新建", "red"))
        os.makedirs(destination)
        # return

    os.makedirs(os.path.join(os.path.join(os.getcwd(), 'gen')), exist_ok=True)
    log_name = os.path.join(os.getcwd(), 'gen', f'{os.path.basename(source)}.log')
    # print(f"開始同步到{destination}...")
    command = [
        'rsync', '-aq', '--ignore-existing', '--remove-source-files', '--progress', 
        f'--log-file={log_name}', f'{source}/', f'{destination}/'
    ]
    subprocess.run(command, check=True)

def merge_log(destination):
    output_file = f"./gen/rsync_log {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt"
    if not os.path.exists(destination):
        print(f"The directory {destination} does not exist.")
        return
    
    log_files = [f for f in os.listdir(destination) if f.endswith('.log')]
    
    if not log_files:
        print("No .txt files found in the directory.")
        return
    
    merged_content = ""
    
    for log_file in log_files:
        file_path = os.path.join(destination, log_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            merged_content += f"\n\n====================[{log_file}]====================\n\n{content}"
        os.remove(os.path.join("./gen/", log_file))
    
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write(merged_content)
    
    # print(f"All files have been merged into {output_file}")

def move_to_parent(parent_folder, child_folders=None, only_files=False):
    """
    新增父資料夾並把子資料夾移進父資料夾
    only_files [true] 只移動檔案到父資料夾 
               [false] 只移動資料夾名單到父資料夾
    """
    os.makedirs(parent_folder, exist_ok=True)
    
    if not only_files:
        if child_folders is None:
            raise ValueError("當 only_files 為 False 時, child_folders 參數不能為 None。")
        
        base_folder = os.path.dirname(parent_folder)
        for folder_name in child_folders:
            folder_path = os.path.join(base_folder, folder_name)
            if os.path.isdir(folder_path):
                shutil.move(folder_path, os.path.join(parent_folder, folder_name))
    else:
        base_folder = os.path.dirname(parent_folder)
        for file_name in os.listdir(base_folder):
            file_path = os.path.join(base_folder, file_name)
            if os.path.isfile(file_path):
                shutil.move(file_path, os.path.join(parent_folder, file_name))

def categorize_artist(path):
    if not os.path.isdir(path):
        print(f"The path {path} is not a directory.")
        return

    english_folder = os.path.join("others", path, "EN Artist")
    japanese_folder = os.path.join("others", path, "JP Artist")
    other_folder = os.path.join("others", path, "Other Artist")
    
    os.makedirs(english_folder, exist_ok=True)
    os.makedirs(japanese_folder, exist_ok=True)
    os.makedirs(other_folder, exist_ok=True)

    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)) and not is_system_file(filename):
            first_char = filename[0]

            if is_english(first_char):
                shutil.move(os.path.join(path, filename), os.path.join(english_folder, filename))
            elif is_japanese(first_char):
                shutil.move(os.path.join(path, filename), os.path.join(japanese_folder, filename))
            else:
                shutil.move(os.path.join(path, filename), os.path.join(other_folder, filename))
    
def categorize_character(base_path, tags, search_depth):
    other_folder = os.path.join(base_path, tags["others"])
    if not os.path.exists(other_folder):
        os.makedirs(other_folder)
        
    for root, dirs, files in os.walk(base_path):
        if os.path.basename(root) == tags["others"]:
            # Avoid re-categorizing
            continue

        current_depth = root[len(base_path):].count(os.sep)
        if current_depth > search_depth:
            continue

        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if is_system_file(file_name):
                continue
            tags_in_file = file_name.split(",")

            if len(tags_in_file) > 0:
                tags_in_file[0] = tags_in_file[0].split("_")[-1]

            moved = False
            for tag in tags_in_file:
                if tag in tags:
                    target_folder = os.path.join(base_path, tags[tag])
                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)
                    
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_folder, file)
                    shutil.move(src_file, dst_file)
                    moved = True
                    break

            if not moved:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(other_folder, file)
                shutil.move(src_file, dst_file)

if __name__ == "__main__":
    print("開始分類檔案...")
    move_to_parent(local.idolmaster, idolmaster_path_child)
    move_to_parent(local.other, only_files=True)

    categorize_character(local.bluearchive, bluearchive_tags, search_depth=1)
    categorize_character(local.idolmaster, idolmaster_tags, search_depth=2)
    categorize_artist(local.other)

    print("開始同步檔案...")
    sync_folders(local.bluearchive, remote.bluearchive)
    sync_folders(local.idolmaster, remote.idolmaster)
    sync_folders(local.other, remote.other)
    sync_folders(local.marin, remote.marin)
    sync_folders(local.genshin, remote.genshin)
    merge_log(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen"))