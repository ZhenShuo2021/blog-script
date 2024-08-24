import os
from pathlib import Path
import src
import src.categorizer
import src.retriever
import src.synchronizer
import src.viewer
from utils import file_utils, string_utils
from src.logger import LogLevel, LogManager

root = Path(__file__).resolve().parent.parent
os.chdir(root)


def main():
    # Initialize
    log_manager = LogManager(level=LogLevel.DEBUG, status="main.py")
    logger = log_manager.get_logger()
    config_loader = file_utils.ConfigLoader('config/config.toml')
    combined_paths = config_loader.get_combined_paths()
    
    logger.info("開始分類檔案...")
    file_categorizer = src.categorizer.CategorizerUI(config_loader, logger)
    file_categorizer.categorize() 
    # Or categorize specific category
    # categories = list(config_loader.get_categories())
    # file_categorizer.categorize(categories[1])   # categorize the last category
    file_count = 0

    logger.info("開始同步檔案...")
    log_dir = root / Path("data")
    file_syncer = src.synchronizer.FileSyncer(config_loader, log_dir, logger).sync_folders()
    # Or sync specific category
    # file_syncer = src.synchronizer.FileSyncer(config_loader, log_dir, logger)
    # file_syncer.sync_folders(combined_paths["IdolMaster"]["local_path"], combined_paths["IdolMaster"]["remote_path"])
    # src.synchronizer.LogMerger(log_dir).merge_logs()
    
    # logger.info("開始尋找遺失作品...")
    # src.retriever.retrieve_artwork()

    # src.viewer.count_tags(combined_paths.get("remote_path"), output_file=src.viewer.file_name)
    # tag_counts = src.viewer.read_tag_counts(src.viewer.file_name)
    # src.viewer.plot_pie_chart(tag_counts, top_n=15, skip=2, output_file=src.viewer.file_name) # skip since the top tags are useless

    print(f"\033[32m這次新增了\033[0m\033[32;1;4m {file_count} \033[0m\033[32m個檔案🍺\033[0m")

if __name__ == "__main__":
    main()
