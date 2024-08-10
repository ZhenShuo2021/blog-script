
# Todo: get_tags in ConfigLoader
import os
import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List

import tomlkit

from utils.string_utils import is_system
from conf import LogLevel, LogManager, logger
log_manager = LogManager(level=LogLevel.INFO, status="file_utils.py")
logger = log_manager.get_logger()

def generate_unique_path(path: Path) -> Path:
    counter = 1
    stem = path.stem
    suffix = path.suffix if path.is_file() else ''
    parent = path.parent

    new_path = parent / f"{stem}-{counter}{suffix}"
    while new_path.exists():
        counter += 1
        new_path = parent / f"{stem}-{counter}{suffix}"

    return new_path


def safe_mv(src: str | Path, dst: str | Path) -> None:
    logger = logging.getLogger(__name__)
    if src == dst:
        return

    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        logger.error(f"Source '{src}' does not exist.")
        raise FileNotFoundError(f"Source '{src}' does not exist.")

    try:
        if src_path.is_file():
            if dst_path.exists():
                dst_path = generate_unique_path(dst_path)
                logger.warning(f"Destination file already exists. It will be renamed to {dst_path}.")
            shutil.move(str(src_path), str(dst_path))
        elif src_path.is_dir():
            if dst_path.exists():
                logger.warning(f"Destination directory '{dst_path}' already exists. It will be renamed.")
                dst_path = generate_unique_path(dst_path)
            shutil.move(str(src_path), str(dst_path))
        logger.info(f"Moved '{src}' to '{dst}' successfully.")
    except PermissionError:
        logger.error(f"Permission denied when moving '{src}' to '{dst}'.")
    except Exception as e:
        logger.error(f"Error occurred while moving '{src}' to '{dst}': {e}")


def merge_path(data: Dict[str, Any]) -> Dict[str, Dict[str, Path]]:
    base_paths = data.get('BASE_PATHS', {})
    categories = data.get('CATEGORIES', {})

    merged_paths = {}

    for base_key, base_path_str in base_paths.items():
        base_path = Path(base_path_str)
        merged_paths[base_key] = {}

        for category_key, category_names in categories.items():
            category_name = category_names[0] if base_key == "local" else category_names[1]
            full_path = base_path / category_name
            merged_paths[base_key][category_key] = full_path

    return merged_paths


def count_files(paths: Dict[str, Path]) -> Dict[str, int]:
    logger = logging.getLogger(__name__)
    file_counts = {}

    for key, path in paths.items():
        if not path.is_dir():
            logger.error(f"FileNotFoundError: {path} does not exist or not a directory.")
        logger.info(f"Counting number of files for {path}.")

        file_count = 0
        for file_path in path.rglob('*'):
            if file_path.is_file() and not is_system(file_path):
                file_count += 1

        file_counts[key] = file_count

    return file_counts


class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None

    def load_config(self):
        try:
            with open(self.config_path, 'r') as file:
                self.config = tomlkit.load(file)
                logger.info("Configuration loaded successfully.")
                if logger.isEnabledFor(logging.DEBUG):
                    pretty_toml = tomlkit.dumps(self.config)
                    logger.debug(f"Configuration:\n{pretty_toml}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def get_base_paths(self):
        return self.config.get('BASE_PATHS', {})

    def get_categories(self):
        return self.config.get('CATEGORIES', {})

    def get_delimiters(self):
        return self.config.get('TAG_DELIMITER', {})


class PathManager:
    def __init__(self, config_loader):
        self.config_loader = config_loader

    def get_combined_paths(self):
        base_paths = self.config_loader.get_base_paths()
        categories = self.config_loader.get_categories()
        combined_paths = {}

        for category, data in categories.items():
            local_combined = os.path.join(base_paths['local_path'], data['local_path'])
            remote_combined = os.path.join(base_paths['remote_path'], data['remote_path'])
            combined_paths[category] = {
                'local': local_combined,
                'remote': remote_combined,
                'tags': data.get('tags', {}),
                'children': data.get('child', [])
            }
            logger.debug(f"Combined dict path for {category}:\n {json.dumps(combined_paths[category], ensure_ascii=False, indent=4)}")

        return combined_paths


if __name__ == "__main__":
    

    config_loader = ConfigLoader('data/config.toml')
    config_loader.load_config()
    tag_delimiters = config_loader.get_delimiters()

    path_manager = PathManager(config_loader)
    combined_paths = path_manager.get_combined_paths()

    # for category, paths in combined_paths.items():
    #     print(f"{category} - Local: {paths['local']}, Remote: {paths['remote']}")
    #     print(f"Tags: {paths['tags']}")
    #     print(f"Children: {paths['children']}")

    # safe_mv(Path('struct.txt'), Path('structA.txt'))
