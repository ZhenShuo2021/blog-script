#!/bin/bash
# Extract date from folder name
# Update all "dates" by folder name with option to set fixed time or preserve original time

# 根據資料夾名稱修改 exif 「日期」。如果加上 -c 則會把所有「時間」固定成九點。

usage() {
    echo "Usage: $0 [-c] /path/to/basefolder"
    echo "  -c: Set a fixed time (09:00:00) instead of preserving original time"
    exit 1
}

# Default to preserving time
clear_time=false

# Parse command line options
while getopts ":c" opt; do
    case ${opt} in
        c )
            clear_time=true
            ;;
        \? )
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Check if base folder is provided
if [ -z "$1" ]; then
    usage
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

    if $clear_time; then
        # Set fixed time
        output_date="${formatted_date} 09:00:00"
        echo "Using fixed time: $output_date"
        exiftool -overwrite_original -AllDates="$output_date" -FileModifyDate="$output_date" -FileCreateDate="$output_date" "$subdir"/*.jpg
    else
        # Preserve original time
        for filepath in "$subdir"/*; do
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
            
            exiftool -q -overwrite_original -AllDates="${output_date}" -FileModifyDate="${output_date}" "${subdir}/${filename}"
        done
    fi
    echo -e "---Finish dir ${subdir}---\n"
done