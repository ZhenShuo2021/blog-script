# A script tests false-sharing performance
# See https://docs.zsl0621.cc/docs/python/false-sharing-in-python

import time
import ctypes
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process, Array, Value
from numba import njit, prange

NUM_ITER = 10**6
NUM_PROCS = 4
PADDING_SIZE = 1
N_REPEATS = 20


def initialize_shared_data(arr, n_workers, use_padding=False):
    np.random.seed(84)
    random_values = np.random.random(n_workers) * 100
    if use_padding:
        for i in range(n_workers):
            arr[i * PADDING_SIZE] = random_values[i]
    else:
        for i in range(n_workers):
            arr[i] = random_values[i]


def run_single_process(n_iterations):
    current = 0.0
    start = time.time()
    for _ in range(n_iterations * NUM_PROCS):
        np.sin(current * 0.95 + 0.1)
    end = time.time()

    return end - start


def bad_worker(shared_data, worker_id, n_iterations):
    for _ in range(n_iterations):
        current = shared_data[worker_id]
        shared_data[worker_id] = (current * 0.95 + 0.1) % 100


def good_worker(shared_data, worker_id, n_iterations):
    padded_index = worker_id * PADDING_SIZE
    for _ in range(n_iterations):
        current = shared_data[padded_index]
        shared_data[padded_index] = (current * 0.95 + 0.1) % 100


def isolated_worker(val, n_iterations):
    for _ in range(n_iterations):
        current = val.value
        val.value = (current * 0.95 + 0.1) % 100


@njit("void(float64[:], int16)", parallel=True)
def numba_bad_worker(shared_data, n_iterations):
    for i in prange(shared_data.shape[0]):
        for _ in range(n_iterations):
            current = shared_data[i]
            shared_data[i] = (current * 0.95 + 0.1) % 100


@njit("void(float64[:], int16, int16)", parallel=True)
def numba_good_worker(shared_data, n_iterations, cache_line_size):
    for i in prange(shared_data.shape[0] // cache_line_size):
        padded_index = i * cache_line_size
        for _ in range(n_iterations):
            current = shared_data[padded_index]
            shared_data[padded_index] = (current * 0.95 + 0.1) % 100


def run_test(n_workers, n_iterations, use_padding=False, use_isolated=False):
    if use_isolated:
        shared_data = [Value(ctypes.c_double, 0.0, lock=False) for _ in range(n_workers)]
        worker_func = isolated_worker
        args_func = [(shared_data[i], n_iterations) for i in range(n_workers)]
    elif use_padding:
        shared_data = Array(ctypes.c_double, n_workers * PADDING_SIZE, lock=False)
        initialize_shared_data(shared_data, n_workers, use_padding=True)
        worker_func = good_worker
        args_func = [(shared_data, i, n_iterations) for i in range(n_workers)]
    else:
        shared_data = Array(ctypes.c_double, n_workers, lock=False)
        initialize_shared_data(shared_data, n_workers, use_padding=False)
        worker_func = bad_worker
        args_func = [(shared_data, i, n_iterations) for i in range(n_workers)]

    procs = [Process(target=worker_func, args=args) for args in args_func]
    start = time.time()
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    end = time.time()

    return end - start


def run_numba_test(n_workers, n_iterations, use_padding=False):
    shared_data = np.random.random(n_workers * (PADDING_SIZE if use_padding else 1)) * 100
    start = time.time()
    if use_padding:
        numba_good_worker(shared_data, n_iterations, PADDING_SIZE)
    else:
        numba_bad_worker(shared_data, n_iterations)
    end = time.time()

    return end - start


def run_average(func, *args, repeats=N_REPEATS, **kk):
    total_time = 0.0
    for _ in range(repeats):
        total_time += func(*args, **kk)
    return total_time / repeats


if __name__ == "__main__":
    print("==============================")
    print(f"test cache line size: {PADDING_SIZE}")
    print("==============================")
    n_iterations = NUM_ITER
    run_numba_test(NUM_PROCS, 1, use_padding=False)
    run_numba_test(NUM_PROCS, 1, use_padding=True)


    single_time = run_average(run_single_process, n_iterations)
    false_sharing_time = run_average(run_test, NUM_PROCS, n_iterations, use_padding=False)
    no_false_sharing_time = run_average(run_test, NUM_PROCS, n_iterations, use_padding=True)
    isolated_time = run_average(run_test, NUM_PROCS, n_iterations, use_isolated=True)
    numba_false_sharing_time = run_average(run_numba_test, NUM_PROCS, 1, use_padding=False)
    numba_no_false_sharing_time = run_average(run_numba_test, NUM_PROCS, n_iterations, use_padding=True)

    print(f"Single Process Time: {single_time:.4f} seconds")
    print(f"False Sharing Time: {false_sharing_time:.4f} seconds")
    print(f"No False Sharing (Padding) Time: {no_false_sharing_time:.4f} seconds")
    print(f"No False Sharing (Isolated Value) Time: {isolated_time:.4f} seconds")
    print(f"Numba False Sharing Time: {numba_false_sharing_time:.4f} seconds")
    print(f"Numba No False Sharing Time: {numba_no_false_sharing_time:.4f} seconds")

    improvement_false_sharing = single_time / false_sharing_time
    improvement_no_false_sharing = single_time / no_false_sharing_time
    improvement_isolated = single_time / isolated_time
    improvement_numba_false_sharing = single_time / numba_false_sharing_time
    improvement_numba_no_false_sharing = single_time / numba_no_false_sharing_time

    print(f"Efficiency Improvement (False Sharing): {improvement_false_sharing:.2f}x")
    print(f"Efficiency Improvement (No False Sharing, Padding): {improvement_no_false_sharing:.2f}x")
    print(f"Efficiency Improvement (No False Sharing, Isolated): {improvement_isolated:.2f}x")
    print(f"Efficiency Improvement (Numba False Sharing): {improvement_numba_false_sharing:.2f}x")
    print(f"Efficiency Improvement (Numba No False Sharing): {improvement_numba_no_false_sharing:.2f}x")

    plt.figure(figsize=(12, 8))

    labels = [
        "Single Process",
        "False Sharing",
        "Padding",
        "Isolated",
        "Numba\nFalse Sharing",
        "Numba\nPadding",
    ]
    times = [single_time, false_sharing_time, no_false_sharing_time, isolated_time, numba_false_sharing_time, numba_no_false_sharing_time]
    plt.bar(labels, times, color=["blue", "red", "green", "purple", "orange", "cyan"])
    plt.ylabel("Execution Time (seconds)", fontsize=20)
    plt.xticks(rotation=45, fontsize=16)
    plt.yticks([], fontsize=14)

    for i, t in enumerate(times):
        plt.text(i, t, f"{t:.4f}s\n{(single_time / t):.2f}x", ha="center", va="bottom", fontsize=14)

    x1, x2, y1, y2 = plt.axis()
    plt.tick_params(axis="y", which="both", left=False)
    plt.tick_params(axis="x", which="both", bottom=False)
    plt.axis((x1, x2, y1, y2 + 0.105))
    plt.tight_layout()
    plt.savefig(f"pad{PADDING_SIZE}.webp", dpi=240)
    plt.show()
