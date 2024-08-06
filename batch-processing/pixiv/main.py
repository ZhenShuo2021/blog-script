import os
from retrieve_artwork import retrieve_artwork_main
from retrieve_artwork import base_url, html_file
from post_process import categorize_character, move_to_parent, categorize_artist, sync_folders, merge_log
from post_process import bluearchive_tags, idolmaster_tags
from tag_stats import count_tags, read_tag_counts, plot_pie_chart
from tag_stats import file_name
from conf import BASE_PATHS, idolmaster_path_child
from tool import local, remote, count_file_dirs

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("開始分類檔案...")
move_to_parent(local.idolmaster, idolmaster_path_child)
move_to_parent(local.other, only_files=True)

categorize_character(local.bluearchive, bluearchive_tags, search_depth=1)
categorize_character(local.idolmaster, idolmaster_tags, search_depth=2)
categorize_artist(local.other)
file_count = count_file_dirs(local)

print("開始同步檔案...")
sync_folders(local.bluearchive, remote.bluearchive)
sync_folders(local.idolmaster, remote.idolmaster)
sync_folders(local.other, remote.other)
sync_folders(local.marin, remote.marin)
sync_folders(local.genshin, remote.genshin)
merge_log(os.path.join(script_dir, "gen"))

print("開始尋找遺失作品...")
retrieve_artwork_main(base_url, html_file)

print("開始統計標籤...")
count_tags(BASE_PATHS["remote"], output_file=file_name)
tag_counts = read_tag_counts(file_name)
plot_pie_chart(tag_counts, top_n=15, skip=2, output_file=file_name) # skip since the top tags are useless

print(f"\033[32m這次新增了\033[0m\033[32;1;4m {file_count} \033[0m\033[32m個檔案🍺\033[0m")