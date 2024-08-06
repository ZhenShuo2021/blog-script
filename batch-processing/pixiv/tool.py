from pathlib import Path
from types import SimpleNamespace
import os
import string
import shutil
import logging
import unittest
from conf import *

def is_system_file(filename):
    # Add more system-specific files as needed
    common_system_files = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}
    return filename in common_system_files

def is_english(character):
    return character in string.ascii_letters

def is_japanese(character):
    return (HIRAGANA_START <= character <= HIRAGANA_END) or (KATAKANA_START <= character <= KATAKANA_END)

def color_text(text, color=None, background=None, style=None):
    """
    返回帶有 ANSI 顏色控制碼的文本。
    
    :param color: red, green, yellow, blue, magenta, cyan, black, white
    :param background: red, green, yellow, blue, magenta, cyan, black, white
    :param style: bold, underline, 'reverse
    :return: f-string
    """
    color_codes = {
        'black': '30', 'red': '31', 'green': '32', 'yellow': '33',
        'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37'
    }
    background_codes = {
        'black': '40', 'red': '41', 'green': '42', 'yellow': '43',
        'blue': '44', 'magenta': '45', 'cyan': '46', 'white': '47'
    }
    style_codes = {
        'bold': '1', 'underline': '4', 'reverse': '7'
    }

    codes = []
    if color in color_codes:
        codes.append(color_codes[color])
    if background in background_codes:
        codes.append(background_codes[background])
    if style in style_codes:
        codes.append(style_codes[style])

    start_code = '\033[' + ';'.join(codes) + 'm' if codes else ''
    end_code = '\033[0m' if codes else ''

    return f'{start_code}{text}{end_code}'

def count_file_dirs(name_space):
    def count_files(directory):
        ctr = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if not os.path.islink(file_path) and not is_system_file(os.path.basename(file_path)):
                    ctr += 1
        return ctr

    total_count = 0
    for key, dir in vars(name_space).items():
        total_count += count_files(dir)
    return total_count

def merge_path():
    local_paths = {}
    remote_paths = {}

    for category, (local_subpath, remote_subpath) in CATEGORIES.items():
        local_paths[category] = os.path.join(BASE_PATHS["local"], local_subpath)
        remote_paths[category] = os.path.join(BASE_PATHS["remote"], remote_subpath)

    local = SimpleNamespace(**local_paths)
    remote = SimpleNamespace(**remote_paths)

    return SimpleNamespace(local=local, remote=remote)

def get_path(category, type):
    local, remote = CATEGORIES[category]
    return BASE_PATHS[type] + (local if type == "local" else remote)

paths = merge_path()
local = paths.local
remote = paths.remote

logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.INFO)

def safe_mv(src, dst):
    if src == dst:
        return
    
    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        raise ValueError(f"Source '{src}' does not exist.")

    try:
        if src_path.is_file():
            if dst_path.exists():
                dst_path = generate_unique_path(dst_path)
                logging.warning(f"Destination file already exists. It will be renamed to {dst_path}.")
            shutil.move(str(src_path), str(dst_path))
        elif src_path.is_dir():
            if dst_path.exists():
                logging.warning(f"Destination directory '{dst_path}' already exists. It will be renamed.")
                dst_path = generate_unique_path(dst_path)
            shutil.move(str(src_path), str(dst_path))

    except PermissionError:
        logging.error(f"Permission denied when moving '{src}' to '{dst}'.")
    except Exception as e:
        logging.error(f"Error occurred while moving '{src}' to '{dst}': {e}")

def generate_unique_path(path):
    counter = 1
    stem = path.stem
    suffix = path.suffix if path.is_file() else ''
    parent = path.parent

    new_path = parent / f"{stem}-{counter}{suffix}"
    while new_path.exists():
        counter += 1
        new_path = parent / f"{stem}-{counter}{suffix}"

    return new_path

class TestSafeMove(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path('test_env')
        self.test_dir.mkdir(exist_ok=True)
        
        (self.test_dir / 'file.txt').write_text('content')
        (self.test_dir / 'dir').mkdir(exist_ok=True)
        (self.test_dir / 'dir' / 'nested.txt').write_text('nested content')
        (self.test_dir / 'nested_dir').mkdir(exist_ok=True)
        (self.test_dir / 'nested_dir' / 'nested_file.txt').write_text('nested file content')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_move_file_new_path(self):
        src = self.test_dir / 'file.txt'
        dst = self.test_dir / 'new_file.txt'
        safe_mv(src, dst)
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())

    def test_move_file_existing_path(self):
        src = self.test_dir / 'file.txt'
        dst = self.test_dir / 'file.txt'
        safe_mv(src, dst)
        self.assertTrue((self.test_dir / 'file-1.txt').exists())
        self.assertFalse(src.exists())

    def test_move_dir_new_path(self):
        src = self.test_dir / 'dir'
        dst = self.test_dir / 'new_dir'
        safe_mv(src, dst)
        self.assertTrue(dst.exists())
        self.assertFalse(src.exists())

    def test_move_dir_existing_path(self):
        src = self.test_dir / 'dir'
        dst = self.test_dir / 'dir'
        safe_mv(src, dst)
        self.assertTrue((self.test_dir / 'dir-1').exists())
        self.assertFalse(src.exists())

    def test_move_nested_dir(self):
        src = self.test_dir / 'nested_dir'
        dst = self.test_dir / 'new_nested_dir'
        safe_mv(src, dst)
        self.assertTrue(dst.exists())
        self.assertTrue((dst / 'nested_file.txt').exists())
        self.assertFalse(src.exists())

    def test_invalid_source(self):
        with self.assertRaises(ValueError):
            safe_mv(self.test_dir / 'nonexistent', self.test_dir / 'dst')

if __name__ == '__main__':
    unittest.main()
