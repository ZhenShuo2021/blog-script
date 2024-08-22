import os
from pathlib import Path
from src.categorizer import FileCategorizer
from utils import file_utils, string_utils
from src.logger import LogLevel, LogManager

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def main():
    # Initialize logger
    log_manager = LogManager(level=LogLevel.INFO, status="main.py")
    logger = log_manager.get_logger()

    # Initialize config
    log_manager = LogManager(level=LogLevel.INFO, status="categorizer.py")
    logger = log_manager.get_logger()

    config_loader = file_utils.ConfigLoader('config/config.toml')
    config_loader.load_config()

    file_categorizer = FileCategorizer(config_loader, logger)
    # file_categorizer.categorize_all()

    # Or you can categorize a single category
    # file_categorizer.categorize("character", 
    #                             Path(config_loader.combined_paths["BlueArchive"]['local']), 
    #                             config_loader.get_categories()["BlueArchive"]["tags"])
    # file_categorizer.categorize("artist", 
    #                             Path(config_loader.combined_paths["Others"]['local']), 
    #                             {})


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
