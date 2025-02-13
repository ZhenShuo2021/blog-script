# /// script
# dependencies = [
#   "matplotlib",
# ]
# ///

# Test repo URL: https://github.com/raspberrypi/linux
import subprocess
import matplotlib.pyplot as plt

FONT_BIG = 16
FONT_MEDIUM = 12
FILE_NAME = "python/sparse-checkout-speed/result/reduce-clone-size-linux"

git_clone_results = [
    {
        "command": "git clone $REPO",
        "capacity": "6.1 GiB",
        "real_time": "15:13.30"
    },
    {
        "command": "git clone --depth=1000 $REPO $(basename $REPO)-d1k",
        "capacity": "1.7 GiB",
        "real_time": "1:30.47"
    },
    {
        "command": "git clone --depth=1000 --filter=blob:none $REPO $(basename $REPO)-d1k-blob",
        "capacity": "1.7 GiB",
        "real_time": "2:44.03"
    },
    {
        "command": "git clone --depth=1000 --filter=blob:none --no-checkout --sparse $REPO $(basename $REPO)-d1k-blob-sp",
        "capacity": "125.4 MiB",
        "real_time": "4.222"
    }
]

def time_to_seconds(time_str):
    parts = time_str.split(":")
    if len(parts) == 1:
        return float(parts[0])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return 0

commands = ['Baseline', 'depth=1000', 'blob:none', 'sparse']
times = [time_to_seconds(result["real_time"]) for result in git_clone_results]

def size_to_mb(size_str):
    if "GiB" in size_str:
        return float(size_str.replace(" GiB", "")) * 1024 * 1024 / 1000
    elif "MiB" in size_str:
        return float(size_str.replace(" MiB", "")) * 1024 / 1000
    return 0

sizes = [size_to_mb(result["capacity"]) for result in git_clone_results]
fig, ax1 = plt.subplots(figsize=(10, 6))
bar_width = 0.35
index = list(range(len(commands)))

# 計算兩個 bar 的位置
bar1_positions = index
bar2_positions = [i + bar_width for i in index]

# 計算 xticks 的位置 (兩個 bar 的中間)
xticks_positions = [i + bar_width/2 for i in index]

bar1 = ax1.bar(bar1_positions, sizes, bar_width, label='Repo Size (MB)', color='tab:blue')
ax2 = ax1.twinx()
bar2 = ax2.bar(bar2_positions, times, bar_width, label="Clone Time (seconds)", color='tab:red', alpha=0.5)

ax1.set_xlabel("Commands", fontsize=FONT_BIG)
ax1.set_ylabel("Repo Size (MB)", fontsize=FONT_BIG)
ax2.set_ylabel("Clone Time (seconds)", fontsize=FONT_BIG)

# 設定 xticks 在兩個 bar 的中間
ax1.set_xticks(xticks_positions)
ax1.set_xticklabels(commands)

ax1.set_ylim(0, max(sizes) + 500)
ax2.set_ylim(0, max(times) + 200)

fig.legend(bbox_to_anchor=(0.9, 0.95), labels=['Repo Size (MB)', 'Clone Time (seconds)'], handles=[bar1, bar2], fontsize=FONT_MEDIUM)

ax1.grid(True, linestyle=":", alpha=0.7)
plt.tight_layout()

for i, rect in enumerate(bar1):
    ax1.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), f'{int(sizes[i])}MB', ha='center', va='bottom')

for i, rect in enumerate(bar2):
    ax2.text(rect.get_x() + rect.get_width() / 2, rect.get_height(), f'{int(times[i])}s', ha='center', va='bottom')

plt.savefig(f'{FILE_NAME}.jpg', dpi=240)

subprocess.run(['magick', f'{FILE_NAME}.jpg', '-quality', '60', f'{FILE_NAME}.webp'])
subprocess.run(['rm', '-f', f'{FILE_NAME}.jpg'])
