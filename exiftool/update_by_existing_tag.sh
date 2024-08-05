#!/bin/bash
# Get original or creation time
# Updates: all dates / modify date

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

for filepath in "$base_folder"/*; do
  # Obtain time info
  filename=$(basename "$filepath")
  original_time=$(exiftool -s3 -DateTimeOriginal "$filepath")
  create_time=$(exiftool -s3 -CreateDate "$filepath")
  new_time=""

  # Continue if time info not exist.
  if [[ ! -z "$original_time" ]]; then
    output_date=$original_time
    echo "Processing file: ${filename}, ${original_time}, success."
  elif [[ ! -z "$create_time" ]]; then
    output_date=$create_time
    echo "Processing file: ${filename}, ${create_time}, success."
  else
    echo "Processing file: ${filename}, time missed. Continue."
    continue
  fi

  # echo "Processing file: "${subdir_name}/${filename}" with date: $output_date"
  exiftool -q -overwrite_original -AllDates="${output_date}" -FileModifyDate="${output_date}" "${filepath}"
done

