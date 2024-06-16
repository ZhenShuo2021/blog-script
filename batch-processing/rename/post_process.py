# Deprecated. This script:
# 1. fix_file_mtime: by json file
# 2. update_exif_times: so that mtime sorting works
# 3. rename_all: to {prefix}001_{filename}

import os
import subprocess
from pathlib import Path
import argparse
import json
import re
import sys
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def check_hidden_file(filename):
    return filename.startswith('.')

def fix_file_mtime(files, directory):
    """
    Fix file mtime according to the json file.
    """
    for filename in files:
        if check_hidden_file(filename):
            continue

        filepath = os.path.join(directory, filename)
        file_cond = os.path.isfile(filepath) and not filename.endswith('.json')
        if file_cond:
            try:
                json_filepath = os.path.join(directory, f"{filename}.json")
                
                if Path(json_filepath).exists():
                    with open(json_filepath, 'r') as f:
                        data = json.load(f)

                    published_time = data.get('published')

                    published_timestamp = time.mktime(time.strptime(published_time, '%Y-%m-%dT%H:%M:%S'))

                    os.utime(filepath, (published_timestamp, published_timestamp))

                    os.remove(json_filepath)

                    print(f"{bcolors.OKGREEN}Modified mtime for file: {filename}{bcolors.ENDC}")
                else:
                    print(f"{bcolors.WARNING}No JSON file found for: {filename}{bcolors.ENDC}")
            except Exception as e:
                print(f"{bcolors.FAIL}Error processing file: {filename}{bcolors.ENDC}")
                print(e)

def sort_by_mtime(directory):
    """
    Sort file according to the mtime.
    """
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.endswith('.json')]
    return sorted(files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))

def sort_by_name(directory):
    """
    Sort file according to the file name.
    """
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.')]
    return sorted(files)

def remove_pattern(filename, pattern, directory):
    """
    Remove the given pattern of file name.
    """
    new_filename = re.sub(pattern, '', filename)
    if new_filename != filename:
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
    return new_filename

def rename_all(files, directory, prefix, pattern_name, r_pattern=False):
    """
    Numbering the files. Choose to remove pattern.
    """
    files = sort_by_mtime(directory)   # Since the files are sorted by the exiftool, we numbering it with mtime
    for index, filename in enumerate(files, start=1):
        if check_hidden_file(filename):
            continue
        
        if r_pattern:
            filename = remove_pattern(filename, pattern_name, directory)
            new_filename = f"{prefix}{index:03d}" + '_' + filename
        else:
            new_filename = f"{prefix}{index:03d}" + '_' + filename
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
        print(f"{bcolors.OKGREEN}Add number to {new_filename}{bcolors.ENDC}")

def update_exif_times(directory):
    exif_cmd = f"exiftool -overwrite_original '-filemodifydate+<0:0:${{filesequence}}0' -q -fileorder filename {directory}"
    subprocess.run(exif_cmd, shell=True)
    subprocess.run(exif_cmd, shell=True)
    print(f"{bcolors.OKGREEN}EXIF time updated.{bcolors.ENDC}")

def main():
    parser = argparse.ArgumentParser(description='Process files in a directory.')
    parser.add_argument('directory', type=str, metavar='', help='The directory to process')
    parser.add_argument('-p', '--prefix', dest='p', default='ID', type=str, metavar='', help='New prefix for files')
    parser.add_argument('-r', '--remove-pattern', dest='r', action='store_true', help='Whether to remove a pattern')
    parser.add_argument('-pn', '--pattern-name', dest='pn', default=r'num\d{3}_', type=str, metavar='', help='The pattern to remove from filenames. For example, r"_num\d{3}" removes all "_numddd", d is numbers. Note: It Does Not Need a R String When Calling!')
    
    args = parser.parse_args()

    directory, prefix, pattern_name, r_pattern = args.directory, args.p, args.pn, args.r

    if not os.path.isdir(directory):
        print(f"{bcolors.FAIL}Error: The specified directory does not exist.{bcolors.ENDC}")
        sys.exit(1)
    
    files = sort_by_name(directory)
    fix_file_mtime(files, directory)
    update_exif_times(directory)
    rename_all(files, directory, prefix, pattern_name, r_pattern)

if __name__ == "__main__":
    main()
