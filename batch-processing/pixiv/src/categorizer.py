
# Todo: glob file type to conf.py
# Todo: divide pattern to conf.py and string_utils.py
# Todo: IPTC/EXIF writer
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict

from src.logger import LogLevel, LogManager
from utils.file_utils import ConfigLoader, safe_move, batch_move
from utils.string_utils import is_system, is_english, is_japanese, split_tags


class ICategorizer(ABC):
    def __init__(self, tag_delimiter: Dict[str, str], logger):
        self.tag_delimiter = tag_delimiter
        self.logger = logger

    def categorize(self, base_path: Path, tags: Dict[str, str]) -> None:
        if not base_path.is_dir():
            self.logger.error(f"The path {base_path} is not a directory.")
            return

        self._prepare_folders(base_path, tags)
        self._process_files(base_path, tags)

    @abstractmethod
    def _prepare_folders(self, base_path: Path, tags: Dict[str, str]) -> None:
        pass

    @abstractmethod
    def _process_files(self, base_path: Path, tags: Dict[str, str]) -> None:
        pass

    def _move_tagged(self, base_path: Path, file_path: Path, file_tags: List[str], tags: Dict[str, str]) -> None:
        """
        Search the first file_tags in tags and move to target_folder.

        base_path: File destination. In configuration: BASE_PATHS / CATEGORIES.BlueArchive.remote
        file_path: File source.
        file_tags: Tags extract from file name.
        tags: Special tags for file name. In configuration: CATEGORIES.BlueArchive.tags
        """ 
        target_folder = self._get_tagged_path(base_path, file_tags, tags)
        if target_folder:
            safe_move(file_path, target_folder / file_path.name)
        else:
            safe_move(file_path, self.other_folder / file_path.name)

    def _get_tagged_path(self, base_path: Path, file_tags: List[str], tags: Dict[str, str]) -> Path:
        """ Return the target folder path based on the file tags. """
        for tag in file_tags:
            if tag in tags:
                target_folder = Path(base_path) / tags[tag]
                target_folder.mkdir(parents=True, exist_ok=True)
                return target_folder
        return None

class CharacterCategorizer(ICategorizer):
    def _prepare_folders(self, base_path: Path, tags: Dict[str, str]) -> None:
        self.other_folder = base_path / tags.get("others", "others")
        self.other_folder.mkdir(exist_ok=True)

    def _process_files(self, base_path: Path, tags: Dict[str, str]) -> None:
        for file_path in base_path.rglob('*'):
            if file_path.is_file() and not is_system(file_path.name):
                file_name = file_path.stem
                file_tags = split_tags(file_name, self.tag_delimiter)
                self._move_tagged(base_path, file_path, file_tags, tags)


class ArtistCategorizer(ICategorizer):
    def _prepare_folders(self, base_path: Path, tags: Dict[str, str]) -> None:
        self.folders = {
            "EN Artist": base_path / "EN Artist",
            "JP Artist": base_path / "JP Artist",
            "Other Artist": base_path / "Other Artist"
        }
        for folder in self.folders.values():
            folder.mkdir(parents=True, exist_ok=True)

    def _process_files(self, base_path: Path, tags: Dict[str, str]) -> None:
        for file_path in base_path.iterdir():
            if file_path.is_file() and not is_system(file_path.name):
                first_char = file_path.name[0]
                if is_english(first_char):
                    folder_name = self.folders["EN Artist"]
                elif is_japanese(first_char):
                    folder_name = self.folders["JP Artist"]
                else:
                    folder_name = self.folders["Other Artist"]
                safe_move(file_path, folder_name / file_path.name)


class FileCategorizer:
    def __init__(self, config_loader: ConfigLoader, logger: LogManager):
        self.config_loader = config_loader
        self.tag_delimiter = config_loader.get_delimiters()  # 讀取分隔符設定
        self.combined_paths = config_loader.get_combined_paths()
        self.logger = logger
        self.strategies = {
            "character": CharacterCategorizer(self.tag_delimiter, self.logger),
            "artist": ArtistCategorizer(self.tag_delimiter, self.logger)
        }

    def categorize(self, category: str, base_path: Path, tags: Dict[str, str]) -> None:
        strategy = self.strategies.get(category)
        if strategy:
            strategy.categorize(base_path, tags)
        else:
            self.logger.error(f"Unknown category strategy: {category}")

    def categorize_tagged(self):
        category_config = self.config_loader.get_categories()
        
        for key in category_config:
            if "tags" in category_config[key]:
                local_path = Path(self.combined_paths[key]["local"])
                tags = category_config[key]["tags"]
                
                self.categorize("character", local_path, tags)
                self.logger.info(f"Categorized {key} based on tags")
            else:
                self.logger.debug(f"No tags found for {key}, skipping categorization")


def main():
    log_manager = LogManager(level=LogLevel.INFO, status="categorizer.py")
    logger = log_manager.get_logger()

    config_loader = ConfigLoader('config/config.toml')
    config_loader.load_config()
    categories = config_loader.get_categories()
    combined_paths = config_loader.get_combined_paths()
    
    file_categorizer = FileCategorizer(config_loader, logger)
    
    batch_move(Path(combined_paths["IdolMaster"]['local']), categories["IdolMaster"]["child"])
    batch_move(Path(combined_paths["other"]['local']))

    # Categorize a single category
    # file_categorizer.categorize("character", Path(combined_paths["IdolMaster"]['local']), categories["IdolMaster"]["tags"])
    # file_categorizer.categorize("character", Path(combined_paths["BlueArchive"]['local']), categories["BlueArchive"]["tags"])
    # file_categorizer.categorize("artist", Path(combined_paths["other"]['local']), {})
    file_categorizer.categorize_tagged()
    file_categorizer.categorize("artist", Path(combined_paths["other"]['local']), {})
    
if __name__ == "__main__":
    main()
