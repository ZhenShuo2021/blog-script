# /// script
# dependencies = [
#   "matplotlib",
# ]
# ///

# Test repo URL: https://github.com/xuejianxianzun/PixivBatchDownloader
import subprocess
import matplotlib.pyplot as plt

FONT_BIG = 16
FONT_MEDIUM = 12
FILE_NAME = "python/sparse-checkout-speed/result/reduce-clone-size-pixiv"

git_clone_results = [
    {
        "command": "git clone -q $REPO",
        "time_seconds": 12.775,
        "size_before_checkout": "79.8 MiB",
        "size_after_checkout": "79.8 MiB"
    },
    {
        "command": "git clone -q --filter=blob:none --no-checkout $REPO $(basename $REPO)-blob-nc",
        "time_seconds": 1.249,
        "size_before_checkout": "2.2 MiB",
        "size_after_checkout": "44.2 MiB"
    },
    {
        "command": "git clone -q --filter=blob:none --no-checkout --depth=1 $REPO $(basename $REPO)-blob-nc-d1",
        "time_seconds": 1.013,
        "size_before_checkout": "144.0 KiB",
        "size_after_checkout": "42.0 MiB"
    },
    {
        "command": "git clone -q --filter=blob:none --no-checkout --depth=1 --sparse $REPO $(basename $REPO)-blob-nc-d1-sp",
        "time_seconds": 0.984,
        "size_before_checkout": "152.0 KiB",
        "size_after_checkout": "10.7 MiB"
    }
]

commands = ['Baseline', 'blob:none', 'depth=1', 'sparse']
times = [result["time_seconds"] for result in git_clone_results]

def size_to_mb(size_str):
    if "KiB" in size_str:
        return float(size_str.replace(" KiB", "")) * 1.024 / 1000
    elif "MiB" in size_str:
        return float(size_str.replace(" MiB", "")) * 1.048576
    return 0

sizes_before = [size_to_mb(result["size_before_checkout"]) for result in git_clone_results]
sizes_after = [size_to_mb(result["size_after_checkout"]) for result in git_clone_results]
size_diff = [after - before for before, after in zip(sizes_before, sizes_after)]

fig, ax1 = plt.subplots(figsize=(10, 6))
bar_width = 0.35
index = list(range(len(commands)))

bar1 = ax1.bar(index, sizes_before, bar_width, label='Size Before (MB)', color='tab:blue')
bar2 = ax1.bar(index, size_diff, bar_width, bottom=sizes_before, label='Size Difference (MB)', color='tab:orange')

ax2 = ax1.twinx()
bar3 = ax2.bar([i + bar_width for i in index], times, bar_width, label="Time (seconds)", color='tab:red', alpha=0.5)

ax1.set_xlabel("Commands", fontsize=FONT_BIG)
ax1.set_ylabel("Repo Size (MB)", fontsize=FONT_BIG)
ax2.set_ylabel("Clone Time (seconds)", fontsize=FONT_BIG)
ax1.set_xticks([i + bar_width/2 for i in index])
ax1.set_xticklabels(commands)

for i, (before, diff) in enumerate(zip(sizes_before, size_diff)):
    ax1.text(i, before + 0.5, f'{before:.1f} MB', ha='center', va='bottom')  # 標示 Size Before
    if i!= 0:
        ax1.text(i, before + diff + 0.5, f'{diff:.1f} MB', ha='center', va='bottom')  # 標示 Size Difference

for i, time in enumerate(times):
    ax2.text(i + bar_width, time + 0.1, f'{time:.1f} s', ha='center', va='bottom')

ax1.set_ylim(0, max([b + d for b, d in zip(sizes_before, size_diff)]) + 5)
ax2.set_ylim(0, max(times) + 2)
ax1.grid(True, linestyle=":", alpha=0.7)
plt.tight_layout()

fig.legend(bbox_to_anchor=(0.93, 0.97), labels=['Repo Size Before (MB)', 'Repo Size Before (MB)', 'Clone Time (seconds)'], handles=[bar1, bar2, bar3], fontsize=FONT_MEDIUM)

plt.savefig(f'{FILE_NAME}.jpg', dpi=240)

subprocess.run(['magick', f'{FILE_NAME}.jpg', '-quality', '60', f'{FILE_NAME}.webp'])
subprocess.run(['rm', '-f', f'{FILE_NAME}.jpg'])
