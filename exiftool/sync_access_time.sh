#!/bin/bash
# Iterate through images in specified folder
# Set FileAccessDate to FileModifyDate

# 檢查是否提供了資料夾路徑
if [ -z "$1" ]; then
  echo "請提供資料夾路徑"
  exit 1
fi

# 進入指定資料夾
cd "$1" || exit

# 遍歷資料夾中的所有照片
for file in *.jpg *.jpeg *.png; do
  if [ -f "$file" ]; then
    echo "正在處理 $file"
    # 使用exiftool將FileAccessDate改為和FileModifyDate一樣
    exiftool "-FileAccessDate<FileModifyDate" "$file"
  fi
done

echo "所有照片的EXIF資訊已更新完畢"
