import os
from pathlib import Path
from core.categorizer import FileCategorizer
from utils import file_utils, string_utils
from conf import LogLevel, LogManager

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def main():
    log_manager = LogManager(level=LogLevel.INFO, status="main.py")
    logger = log_manager.get_logger()

    config_loader = file_utils.ConfigLoader('data/config.toml')
    config_loader.load_config()
    categories = config_loader.get_categories()
    combined_paths = config_loader.get_combined_paths()

    file_categorizer = FileCategorizer(config_loader, logger)

    file_categorizer.batch_move(Path(combined_paths["IdolMaster"]['local']), categories["IdolMaster"]["child"])
    file_categorizer.batch_move(Path(combined_paths["other"]['local']))

    # Categorize a single category
    # file_categorizer.categorize("character", Path(combined_paths["IdolMaster"]['local']), categories["IdolMaster"]["tags"])
    # file_categorizer.categorize("character", Path(combined_paths["BlueArchive"]['local']), categories["BlueArchive"]["tags"])
    # file_categorizer.categorize("artist", Path(combined_paths["other"]['local']), {})
    file_categorizer.categorize_tagged()
    file_categorizer.categorize("artist", Path(combined_paths["other"]['local']), {})


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
