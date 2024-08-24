import os
from pathlib import Path
import src
import src.categorizer
import src.synchronizer
from utils import file_utils, string_utils
from src.logger import LogLevel, LogManager

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def main():
    # Initialize
    log_manager = LogManager(level=LogLevel.DEBUG, status="main.py")
    logger = log_manager.get_logger()
    config_loader = file_utils.ConfigLoader('config/config.toml')
    
    # Start categorizing all categories
    file_categorizer = src.categorizer.CategorizerUI(config_loader, logger)
    file_categorizer.categorize() 
    # Or categorize specific category
    # categories = list(config_loader.get_categories())
    # file_categorizer.categorize(categories[1])   # categorize the last category

    # Sync file to remote storage
    log_dir = Path(script_dir).parent / Path("data")
    file_syncer = src.synchronizer.FileSyncer(config_loader, log_dir, logger).sync_folders()
    # Or sync specific category
    # combined_paths = config_loader.get_combined_paths()
    # file_syncer = src.synchronizer.FileSyncer(config_loader, log_dir, logger)
    # file_syncer.sync_folders(combined_paths["IdolMaster"]["local_path"], combined_paths["IdolMaster"]["remote_path"])
    # src.synchronizer.LogMerger(log_dir).merge_logs()
    

if __name__ == "__main__":
    main()

# print("開始同步檔案...")
# [sync_folders(getattr(local, key), getattr(remote, key)) for key in vars(local)]   # walk through keys using list comprehension
# merge_log(os.path.join(script_dir, "gen"))

# print("開始尋找遺失作品...")
# retrieve_artwork_main(base_url, html_file)

# print("開始統計標籤...")
# count_tags(BASE_PATHS["remote"], output_file=file_name)
# tag_counts = read_tag_counts(file_name)
# plot_pie_chart(tag_counts, top_n=15, skip=2, output_file=file_name) # skip since the top tags are useless

# print(f"\033[32m這次新增了\033[0m\033[32;1;4m {file_count} \033[0m\033[32m個檔案🍺\033[0m")
