import os
import string
from types import SimpleNamespace

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

def count_file_dirs(remote):
    def count_files(directory):
        ctr = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if not os.path.islink(file_path) and not is_system_file(os.path.basename(file_path)):
                    ctr += 1
        return ctr

    total_count = 0
    for key, dir in vars(remote).items():
        total_count += count_files(dir)
    return total_count

def Path():
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

paths = Path()
local = paths.local
remote = paths.remote
