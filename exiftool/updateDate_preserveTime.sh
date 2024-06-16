#!/bin/bash
# Update date, preserve time.

if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/basefolder"
  exit 1
fi

# Set base folder
base_folder="$1"

# Check base folder exists
if [ ! -d "$base_folder" ]; then
  echo "Error: $base_folder does not exist."
  exit 1
fi

for subdir in "$base_folder"/*/; do
  subdir_name=$(basename "$subdir")

  # Important, format your subfolders in "YYYYMMDD title"!
  date_part=${subdir_name:0:8}
  formatted_date="${date_part:0:4}:${date_part:4:2}:${date_part:6:2}"
  echo "Processing dir ${subdir}..."

  for filepath in "$subdir"/*; do
    # Obtain time info
    filename=$(basename "$filepath")
    echo "Processing file: ${filename}"
    original_time=$(exiftool -s3 -DateTimeOriginal "$filepath")
    create_time=$(exiftool -s3 -CreateDate "$filepath")

    # Use original time if exist. Otherwise, use download time (FileModifyTime)
    if [[ ! -z "$original_time" ]]; then
        formatted_time="${original_time:11:2}:${original_time:14:2}:${original_time:17:8}"
    else
        formatted_time="${create_time:11:2}:${create_time:14:2}:${create_time:17:8}"
    fi

    output_date="${formatted_date} ${formatted_time}"
    
    # echo "Processing file: "${subdir_name}/${filename}" with date: $output_date"
    exiftool -q -overwrite_original -AllDates="${output_date}" -FileModifyDate="${output_date}" "${subdir}/${filename}"
  done
  echo -e "---Finish dir ${subdir}---\n"
done