
# Todo: glob file type to conf.py
# Todo: IPTC/EXIF writer
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict

from src.logger import LogLevel, LogManager
from utils.file_utils import ConfigLoader, safe_move, batch_move
from utils.string_utils import is_system, is_english, is_japanese, split_tags

# Some global constants
others_name = "others"   # key name in config
EN = "EN Artist"
JP = "JP Artist"
Other = "Other Artist"


class ICategorizer(ABC):
    def __init__(self, config_loader: ConfigLoader, logger):
        self.tag_delimiter = config_loader.get_delimiters()
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


class TaggedCategorizer(ICategorizer):
    def _prepare_folders(self, base_path: Path, tags: Dict[str, str]) -> None:
        self.other_folder = base_path / tags.get(others_name, "others")
        self.other_folder.mkdir(exist_ok=True)

    def _process_files(self, base_path: Path, tags: Dict[str, str]) -> None:
        for file_path in base_path.rglob('*'):
            if file_path.is_file() and not is_system(file_path.name):
                file_name = file_path.stem
                file_tags = split_tags(file_name, self.tag_delimiter)
                self._move_tagged(base_path, file_path, file_tags, tags)

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


class ArtistCategorizer(ICategorizer):
    def _prepare_folders(self, base_path: Path, tags: Dict[str, str]) -> None:
        self.folders = {
            "EN": base_path / EN,
            "JP": base_path / JP,
            "Other": base_path / Other
        }
        for folder in self.folders.values():
            folder.mkdir(parents=True, exist_ok=True)

    def _process_files(self, base_path: Path, tags: Dict[str, str] | None=None) -> None:
        for file_path in base_path.iterdir():
            if file_path.is_file() and not is_system(file_path.name):
                first_char = file_path.name[0]
                if is_english(first_char):
                    folder_name = self.folders["EN"]
                elif is_japanese(first_char):
                    folder_name = self.folders["JP"]
                else:
                    folder_name = self.folders["Other"]
                safe_move(file_path, folder_name / file_path.name)


class FileCategorizer:
    def __init__(self, config_loader: ConfigLoader, logger: LogManager):
        self.config_loader = config_loader
        self.combined_paths = config_loader.get_combined_paths()
        self.logger = logger
        self.strategies = {
            "character": TaggedCategorizer(self.config_loader, self.logger),
            "artist": ArtistCategorizer(self.config_loader, self.logger)
        }

    def categorize(self, category: str, base_path: Path, tags: Dict[str, str]) -> None:
        """Categorize files for single category (folder).

        Usage: 
        - file_categorizer.categorize("character", Path(combined_paths["IdolMaster"]['local']), categories["IdolMaster"]["tags"])
        - file_categorizer.categorize("artist", Path(combined_paths["others"]['local']), {})
        
        Args:
          category: Working directory.
          base_path: Download directory. Passed to ICategorizer.categorize.

        Returns:
          None
        """
        strategy = self.strategies.get(category)
        if strategy:
            strategy.categorize(base_path, tags)
        else:
            self.logger.error(f"Unknown category strategy: {category}")

    def categorize_tagged(self):
        """Categorize files for all category specified in config.

        Loop over all categories specified in config and categorize them based on pre-defined tags.
        """
        categories = self.config_loader.get_categories()
        for category in categories:
            self._pre_process(categories, category)
            self._categorize_tagged(categories, category)

    def _pre_process(self, categories: str, category: Dict):
        """Private helper function for categorization.
        
        Preprocess if "children" in category keys or category equals to "Others"
        """
        local_path = Path(self.combined_paths[category]["local"])
        tags = categories[category].get("tags")
        if "children" in categories[category]:
            batch_move(Path(local_path), categories[category]["children"])
        if "Others" == category:
            batch_move(Path(self.combined_paths[category]["local"]), [])
            if "tags" in categories[category]:
                self.categorize("character", Path(local_path), tags)
            else:
                self.categorize("artist", Path(local_path), {})

    def _categorize_tagged(self, categories: str, category: Dict):
        """Private helper function for categorization.

        Categorize all categories with "tags" key.
        """
        if "tags" in categories[category]:
            local_path = Path(self.combined_paths[category]["local"])
            tags = categories[category]["tags"]

            self.categorize("character", local_path, tags)
            self.logger.info(f"Categorized {category} based on tags")
        else:
            self.logger.debug(f"No tags found for {category}, skipping categorization")


def main():
    log_manager = LogManager(level=LogLevel.INFO, status="categorizer.py")
    logger = log_manager.get_logger()

    config_loader = ConfigLoader('config/config.toml')
    config_loader.load_config()

    file_categorizer = FileCategorizer(config_loader, logger)
    file_categorizer.categorize_tagged()


if __name__ == "__main__":
    main()
