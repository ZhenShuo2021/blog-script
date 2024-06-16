#!/bin/bash
# Updates dates, alter time by a fix value.
# You can further increment the time by 10s as described in README.

base_folder="/your/base/folder"

for subdir in "$base_folder"/*/; do
  subdir_name=$(basename "$subdir")

  # Name your subfolder in "YYYY:MM:DD"!
  date_part=${subdir_name:0:8}
  formatted_date="${date_part:0:4}:${date_part:4:2}:${date_part:6:2} 09:00:00" # 09 is the time info. Specify it yourself.
  echo "Processing folder: $subdir_name with date: $formatted_date"
  exiftool -overwrite_original -AllDates="$formatted_date" -FileModifyDate="$formatted_date" -FileCreateDate="$formatted_date" "$subdir"/*.jpg
done
