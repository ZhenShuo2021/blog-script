import os
import subprocess, shutil

def add_to_7z(local_folder, smb_folder):
    # 將本地文件複製到 SMB 共享文件夾
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_file = os.path.join(root, file)
            smb_file = os.path.join(smb_folder, file)
            # 使用 shutil 將文件複製到 SMB 共享文件夾
            shutil.copy2(local_file, smb_file)
    
    # 定義壓縮檔案路徑
    archive_path = os.path.join(smb_folder, '和同事壞壞.7z')
    
    # 使用 7z 命令進行壓縮
    compress_cmd = f"7z a {archive_path} {smb_folder}/*"
    subprocess.run(compress_cmd, shell=True)
    
    print(f"Files from {local_folder} have been added to {archive_path}")

def main():
    local_folder = "/Users/leo/gallery-dl/"
    smb_folder = "/Volumes/photo/"
    
    add_to_7z(local_folder, smb_folder)

if __name__ == "__main__":
    main()
