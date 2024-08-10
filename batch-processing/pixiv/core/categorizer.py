from pathlib import Path
from typing import List, Dict
from abc import ABC, abstractmethod
import shutil

from conf import LogLevel, LogManager, logger
from utils.file_utils import PathManager, ConfigLoader, safe_mv
from utils.string_utils import is_system, is_english, is_japanese

log_manager = LogManager(level=LogLevel.INFO, status="categorizer.py")
logger = log_manager.get_logger()

class CategoryStrategy(ABC):
    @abstractmethod
    def categorize(self, base_path: Path, tags: Dict[str, str], search_depth: int) -> None:
        pass


class CharacterCategoryStrategy(CategoryStrategy):
    def categorize(self, base_path: Path, tags: Dict[str, str], search_depth: int) -> None:
        if not base_path.is_dir():
            logger.error(f"The path {base_path} is not a directory.")
            return

        other_folder = base_path / tags.get("others", "others")
        other_folder.mkdir(exist_ok=True)

        for path in base_path.rglob('*'):
            if is_system(path.name):
                continue

            if path.is_dir():
                if path.name == tags.get("others"):
                    continue

                current_depth = len(path.relative_to(base_path).parts)
                if current_depth > search_depth:
                    continue

            elif path.is_file():
                file_name = path.stem
                tags_in_file = file_name.split(",")
                if tags_in_file:
                    tags_in_file[0] = tags_in_file[0].split("_")[-1]

                self._move_file_based_on_tags(base_path, path, tags_in_file, tags, other_folder)

    def _move_file_based_on_tags(self, base_path: Path, file_path: Path, tags_in_file: List[str], tags: Dict[str, str], other_folder: Path) -> None:
        for tag in tags_in_file:
            if tag in tags:
                target_folder = base_path / tags[tag]
                target_folder.mkdir(exist_ok=True)

                dst_file = target_folder / file_path.name
                safe_mv(file_path, dst_file)
                return
        safe_mv(file_path, other_folder / file_path.name)


class ArtistCategoryStrategy(CategoryStrategy):
    def categorize(self, base_path: Path, tags: Dict[str, str], search_depth: int) -> None:
        if not base_path.is_dir():
            logger.error(f"The path {base_path} is not a directory.")
            return

        folders = {
            "EN Artist": base_path / "EN Artist",
            "JP Artist": base_path / "JP Artist",
            "Other Artist": base_path / "Other Artist"
        }

        for folder in folders.values():
            folder.mkdir(parents=True, exist_ok=True)

        for file_path in base_path.iterdir():
            if file_path.is_file() and not is_system(file_path.name):
                first_char = file_path.name[0]

                if is_english(first_char):
                    safe_mv(file_path, folders["EN Artist"] / file_path.name)
                elif is_japanese(first_char):
                    safe_mv(file_path, folders["JP Artist"] / file_path.name)
                else:
                    safe_mv(file_path, folders["Other Artist"] / file_path.name)


class FileCategorizer:
    def __init__(self, config_loader: ConfigLoader, path_manager: PathManager):
        self.config_loader = config_loader
        self.path_manager = path_manager
        self.strategies = {
            "character": CharacterCategoryStrategy(),
            "artist": ArtistCategoryStrategy()
        }

    def categorize(self, category: str, base_path: Path, tags: Dict[str, str], search_depth: int) -> None:
        strategy = self.strategies.get(category)
        if strategy:
            strategy.categorize(base_path, tags, search_depth)
        else:
            logger.error(f"Unknown category strategy: {category}")

    def batch_move(self, parent_folder: Path, child_folders: List[str] = []) -> None:
        def walk_folder(walking_folder, parent_folder):
            for file_path in walking_folder.iterdir():
                if file_path.is_file() and not is_system(file_path.name):
                    safe_mv(file_path, parent_folder / file_path.name)

        parent_folder.mkdir(exist_ok=True)
        base_folder = parent_folder.parent

        if child_folders:
            for child_name in child_folders:
                child_path = base_folder / child_name
                if child_path.is_dir():
                    walk_folder(child_path, parent_folder)
                    shutil.rmtree(str(child_path))
                    logger.info(f"Batch move: deleing empty child folder {child_path}.")
                else:
                    logger.debug(f"Batch move: child folder {child_path} not exist.")
        else:
            walk_folder(base_folder, parent_folder)


def main():
    config_loader = ConfigLoader('data/config.toml')
    config_loader.load_config()

    path_manager = PathManager(config_loader)
    combined_paths = path_manager.get_combined_paths()

    file_categorizer = FileCategorizer(config_loader, path_manager)

    file_categorizer.batch_move(Path(combined_paths["IdolMaster"]['local']),
                                config_loader.get_categories()["IdolMaster"]["child"])
    file_categorizer.batch_move(Path(combined_paths["other"]['local']))

    # def process_categories(config_loader, combined_paths):
    #     categories = config_loader.get_categories()

    #     for key, value in categories.items():
    #         if "tags" not in value:
    #             # 執行myFunc函數，傳入相關參數
    #             local_path = Path(combined_paths[key]["local"])
    #             file_categorizer.categorize(key, local_path, value.get("tags", []), search_depth=1)

    # process_categories(config_loader, combined_paths)
    file_categorizer.categorize("character", Path(combined_paths["IdolMaster"]['local']),
                                config_loader.get_categories()["IdolMaster"]["tags"], search_depth=1)
    file_categorizer.categorize("character", Path(combined_paths["BlueArchive"]['local']),
                                config_loader.get_categories()["BlueArchive"]["tags"], search_depth=1)
    file_categorizer.categorize("artist", Path(combined_paths["other"]['local']), {}, search_depth=1)


if __name__ == "__main__":
    main()
