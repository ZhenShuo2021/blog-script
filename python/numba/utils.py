import sys

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["figure.dpi"] = 240
FONT_SMALL = 14
FONT_BIG = 20
NUM_THREADS = 4
INT_MIN = sys.float_info.min


def async_worker(func, func_input, num_workers, split_task=False):
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []

        # 多項任務分配給 worker
        if not split_task:
            futures = {executor.submit(func, *args): args for args in func_input}

            for future in as_completed(futures):
                result = future.result()
                yield result

        # 單一任務拆分給 worker
        else:
            chunk_size = len(func_input) // num_workers
            for i in range(num_workers):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i != num_workers - 1 else len(func_input)
                futures.append(executor.submit(func, func_input, start, end))

            total_result = 0.0
            for future in futures:
                total_result += np.sum(future.result())
            yield total_result


def benchmark(
    func, name, base_time, methods, *function_args, iteration=1000, precision=6, workers=1
):
    if iteration == 0:
        return 0, 0, 0
    res = None
    print(f"計算{name}中...", end="", flush=True)
    start = time.time()
    for _ in range(iteration):
        res = func(*function_args)
    end = time.time()
    print("\r" + " " * 30 + "\r", end="", flush=True)

    elapsed = (end - start) / iteration / workers  # multi-thread
    speedup = base_time / (elapsed + 1e-9) if base_time else 1
    methods[name]["result"]["speedup_ratio"].append(speedup)
    methods[name]["result"]["time"].append(elapsed)

    print(f"{name} 平均耗時: {elapsed:.{precision}f} 秒，速度提升: {speedup:.2f}x")
    return res, elapsed, speedup


def plot(methods, x_val, filename, autoplot=True, order=None, xticks=None, yticks=None):
    fig, ax = plt.subplots(figsize=(9, 6))
    baseline_name = "Baseline (numpy array)"
    kw = {"markersize": 6, "markeredgewidth": 1, "linewidth": 2.5, "clip_on": False}

    # not specifing line order
    if autoplot:
        for method, data in reversed(list(methods.items())):
            color = "black" if method == baseline_name else None  # None will use the default color
            if not data["result"]["speedup_ratio"]:
                print(f"{method} skipped")
                continue
            ax.plot(
                x_val,
                data["result"]["speedup_ratio"],
                marker=data["style"].get("marker", "o"),
                linestyle=data["style"].get("linestyle", "-"),
                label=method,
                color=color,
                **kw,
            )

    # specify line order manually
    else:
        if order is None:
            raise ValueError("Input parameter 'order' missed")
        for key in order:
            color = "black" if key == baseline_name else None  # None will use the default color
            ax.plot(
                x_val,
                methods[key]["result"]["speedup_ratio"],
                label=key,
                marker=methods[key]["style"].get("marker", "o"),
                linestyle=methods[key]["style"].get("linestyle", "-"),
                color=color,
                **kw,
            )

    ax.tick_params(
        axis="x", which="both", direction="in", length=3, pad=6, labelsize=FONT_SMALL, rotation=45
    )
    ax.tick_params(axis="y", which="both", direction="in", length=3, pad=6, labelsize=FONT_SMALL)
    ax.set_xlabel("Data size", fontsize=FONT_BIG, labelpad=6)
    ax.set_ylabel("Speed up ratio", fontsize=FONT_BIG, labelpad=6)
    # ax.set_xscale("log")
    # ax.set_xlim(x_val[0], x_val[-1])
    ax.set_ylim(-0.3, 8)
    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.legend(loc="upper left", fontsize=FONT_SMALL - 1, frameon=False)
    ax.minorticks_off()
    plt.tight_layout()
    plt.savefig(filename, bbox_inches="tight")
    plt.show()


def pop_results(result_dict):
    for val in result_dict.values():
        try:
            val["result"]["time"].pop(0)
            val["result"]["speedup_ratio"].pop(0)
        except Exception as e:
            print(f"Error: {e}")
