import os

os.environ["NUMBA_DISABLE_INTEL_SVML"] = "0"  # 0: enable svml, else: disable svml
os.environ["NUMBA_ENABLE_AVX"] = "1"

import json

import numpy as np
from numba import njit, prange, vectorize, guvectorize

from utils import async_worker, plot, benchmark, pop_results, NUM_THREADS
from utils_svml import Keys, methods

# settings
sizes = 10 ** np.arange(2, 8)


# 運算函數
@njit(inline="always")
def alg(x: int):
    return np.cos(x) ** 2 + np.sin(x) ** 2


# 1. NumPy矩陣運算
def alg_np_array(arr: np.ndarray):
    return np.sum(np.cos(arr) ** 2 + np.sin(arr) ** 2)


# 2. Numba + njit
@njit
def alg_njit(arr):
    n = len(arr)
    res = np.zeros_like(arr)
    for i in range(n):
        res[i] = alg(arr[i])
    return np.sum(res)


# 3. Numba + njit + nogil + ThreadPool
@njit(nogil=True)
def njit_nogil_worker(arr, start, end):
    local_res = np.zeros(end - start)
    for i in prange(start, end):
        local_res[i - start] = alg(arr[i])
    return local_res


def alg_njit_nogil_threadpool(arr, num_workers=NUM_THREADS):
    return next(async_worker(njit_nogil_worker, arr, num_workers, split_task=True))


# 4. Numba + njit + parallel
@njit(parallel=True)
def alg_njit_parallel(arr):
    n = len(arr)
    res = np.zeros_like(arr)
    for i in prange(n):
        res[i] = alg(arr[i])
    return np.sum(res)


# 5. Numba + njit + parallel + nogil + ThreadPool
@njit(parallel=True, nogil=True)
def njit_parallel_nogil_worker(arr, start, end):
    local_res = np.zeros(end - start)
    for i in prange(start, end):
        local_res[i - start] = alg(arr[i])
    return local_res


def alg_njit_parallel_nogil_threadpool(arr, num_workers=NUM_THREADS):
    return next(async_worker(njit_parallel_nogil_worker, arr, num_workers, split_task=True))


# 6. Numba + vectorize
@vectorize(["float64(float64)"], nopython=True, target="parallel")
def vectorized_helper(x):
    return np.cos(x) ** 2 + np.sin(x) ** 2


# njit a vectorize function is not support, see https://github.com/numba/numba/issues/5720
def alg_vectorized(x):
    x = vectorized_helper(x)
    return np.sum(x)


# 7. Numba + guvectorize
@guvectorize(["float64[:], float64[:]"], "(n)->(n)", nopython=True, target="parallel")
def guvectorized_helper(arr, res):
    for i in prange(len(arr)):
        arr[i] = np.cos(arr[i]) ** 2 + np.sin(arr[i]) ** 2


# njit a vectorize function is not support, see https://github.com/numba/numba/issues/5720
def alg_guvectorized(arr):
    res = np.zeros_like(arr)
    guvectorized_helper(arr, res)
    return np.sum(res)


# 執行測試
def main(methods, n_iter=10000, n_iter_py=1000, no_run=False):
    filename = (
        "results_svml" if os.getenv("NUMBA_DISABLE_INTEL_SVML") == "0" else "results_original"
    )
    # configure algorithms to test
    algorithms = [
        (alg_njit, Keys.njit),
        (alg_njit_parallel, Keys.njit_parallel),
        (alg_njit_nogil_threadpool, Keys.njit_nogil_threadpool),
        (alg_njit_parallel_nogil_threadpool, Keys.njit_parallel_nogil_threadpool),
        (alg_vectorized, Keys.vectorize),
        (alg_guvectorized, Keys.guvectorize),
    ]

    # configure matplotlib line order
    order = [
        Keys.njit_parallel_nogil_threadpool,
        Keys.njit_nogil_threadpool,
        Keys.njit_parallel,
        Keys.njit,
        Keys.vectorize,
        Keys.guvectorize,
        Keys.np_array,
    ]

    # run simulation
    if not no_run:
        for size in sizes:
            print(f"\n測試數據長度: {size}")
            arr = np.random.rand(size) * 100

            _, base_time, _ = benchmark(
                alg_np_array, Keys.np_array, None, methods, arr, iteration=n_iter_py
            )

            for alg, key in algorithms:
                benchmark(alg, key, base_time, methods, arr, iteration=n_iter)

        # remove first warmup item
        pop_results(methods)

    # store and visualize
    mode = "r" if no_run else "w"
    with open(filename + ".json", mode) as f:
        if no_run:
            methods = json.load(f)
        else:
            json.dump(methods, f, indent=4)
        # remove the first warmup entry

    plot(methods, sizes[1:], filename + ".webp", autoplot=False, order=order)


if __name__ == "__main__":
    os.environ["NUMBA_DISABLE_INTEL_SVML"] = "0"
    main(methods, 10, no_run=True)

    # os.environ["NUMBA_DISABLE_INTEL_SVML"] = "1"
    # main(methods, no_run=1)
