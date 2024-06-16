import argparse
import os
from pathlib import Path
import subprocess
import time

class bcolors:
    HEADER = '\033[95m'  # 紫
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' # 亮黃
    FAIL = '\033[91m'    # 紅
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def convert_image(file_path, output_format, output_dir, quality, preserve_structure=False, input_base_dir=None, clean=False, force=False, sync_mtime=True):
    if preserve_structure and input_base_dir:
        relative_path = file_path.relative_to(input_base_dir)
        output_file = output_dir / relative_path.with_suffix(f".{output_format}")
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_file = output_dir / f"{file_path.stem}.{output_format}"

    if output_file.exists() and not force:
        overwrite = input(f"File {output_file} already exists. Overwrite? (y/n/all): ").strip().lower()
        if overwrite == 'n':
            return False
        elif overwrite == 'all':
            force = True
    
    cmd = [
        "magick", str(file_path),
        "-quality", str(quality), "-type", "truecolor",
        "-alpha", "on",
        str(output_file)
    ]
    
    subprocess.run(cmd, check=True)
    if clean:
        file_path.unlink()  # Clean the original file
    
    if sync_mtime:
        original_mtime = os.path.getmtime(file_path)
        os.utime(output_file, (original_mtime, original_mtime))

    return force

def process_directory(directory, output_format, recursive, quality, output_dir, verbose, force, preserve_structure):
    search_pattern = "**/*" if recursive else "*"
    files = [file for file in directory.glob(search_pattern) if file.is_file()]
    total_files = len(files) - 1
    processed_files = 0
    
    for file_path in files:
        if file_path.name.startswith('.'):
            continue
        elif file_path.suffix.lower() in {".jpg", "JPG", ".jpeg", ".png", ".PNG"}:
            force = convert_image(file_path, output_format, output_dir, quality, preserve_structure, directory, clean=False, force=force, sync_mtime=True)
            processed_files += 1
            if verbose:
                print(f"Successfully processed: {file_path.name}.")
            print(f"Processing\t\t: {processed_files}/{total_files}", end="\r")
        else:
            if preserve_structure:
                relative_path = file_path.relative_to(directory)
                target_path = output_dir / 'todo' / relative_path
            else:
                target_path = output_dir / 'todo' / file_path.name

            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            if target_path.exists():
                print(f"File {target_path} already exists. Skipping.")
                continue
            os.rename(file_path, target_path)
    print()

def get_total_size_and_count(directory, recursive):
    search_pattern = "**/*" if recursive else "*"
    files = list(directory.glob(search_pattern))
    total_size = sum(file_path.stat().st_size for file_path in files if file_path.is_file())
    file_count = sum(1 for file_path in files if file_path.is_file())
    return file_count, total_size

def main():
    parser = argparse.ArgumentParser(
        description="Convert images to a specified format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_path", type=str, help="Path to the input file or directory")
    parser.add_argument("output_format", type=str, nargs="?", default="webp", help="Output format. Ex: avif/webp/jpg")
    parser.add_argument("-q", "--quality", type=int, default=90, help="Quality of the output image")
    parser.add_argument("-o", "--output_dir", type=str, default="out", help="Name of output directory, same level of input path")
    parser.add_argument("-c", "--clean", action='store_true', help="Clean original files")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively search directories")
    parser.add_argument("--sync", action='store_false', help="Sync modify time for output file")
    parser.add_argument("--verbose", action="store_true", help="Magick processing verbose")
    parser.add_argument("--preserve-structure", action="store_true", help="Preserve the directory structure of the input files in the output directory")

    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_format = args.output_format
    recursive = args.recursive
    quality = args.quality
    clean = args.clean
    verbose = args.verbose
    preserve_structure = args.preserve_structure
    output_dir = input_path.parent / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    force = False

    # 獲取原始資料夾的檔案數量和總容量
    original_file_count, original_total_size = get_total_size_and_count(input_path, recursive)

    if input_path.is_file():
        force = convert_image(input_path, output_format, output_dir, quality, preserve_structure, input_path.parent, clean, force=force, sync_mtime=True)
    elif input_path.is_dir():
        process_directory(input_path, output_format, recursive, quality, output_dir, verbose, force, preserve_structure)
    else:
        print(f"Invalid input path: {input_path}")
        parser.print_help()
        return

    # 獲取輸出資料夾的檔案數量和總容量
    output_file_count, output_total_size = get_total_size_and_count(output_dir, recursive)

    # 計算檔案縮小比例
    size_reduction_ratio = (original_total_size - output_total_size) / original_total_size * 100 if original_total_size > 0 else 0

    # 打印統計資訊
    print(f"Original file count\t: {original_file_count}")
    print(f"Output file count\t: {output_file_count}")
    print(f"Original total size\t: {original_total_size / (1024 * 1024):.2f} MB")
    print(f"Output total size\t: {output_total_size / (1024 * 1024):.2f} MB")
    print(f"Size reduction\t\t: {bcolors.OKGREEN}{size_reduction_ratio:.2f}%{bcolors.ENDC}")

if __name__ == "__main__":
    main()
