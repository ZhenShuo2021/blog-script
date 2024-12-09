# OMP algorithm with hand-craft LSQR algorithm to replace the LS algorithm.
# Estimating real signal from a under-determined system y=Ax+n where the
# columns of A is much larger than its rows. The real signal x is assumed to
# has the block-sparse property and the sparsity is known beforehand.

# Reference of LSQR algorithm: https://github.com/PythonOptimizers/pykrylov/blob/master/pykrylov/lls/lsqr.py
import time
import json

import numpy as np

from utils import async_worker, benchmark, plot, pop_results, NUM_THREADS
from utils_omp import (
    Keys,
    njit_parallel_generate_data_unroll,
    njit_parallel_generate_data_npdot,
    njit_parallel_generate_data_atsign,
    njit_generate_data_atsign,
    njit_generate_data_npdot,
    generate_data,
    njit_omp,
    omp,
    calculate_metrics,
    methods_data,
    methods_omp,
)


def njit_parallel_generate_data_unroll_threadpool(
    n_observation, n_feature, sparsity, noise_level=0.1, num_workers=NUM_THREADS
):
    func_input = [(n_observation, n_feature, sparsity, noise_level)] * num_workers
    worker = async_worker(
        njit_parallel_generate_data_unroll, func_input, num_workers, split_task=False
    )

    for result in worker:
        pass


def njit_omp_threadpool(S, y, sparsity, num_workers=NUM_THREADS):
    func_input = [(S, y, sparsity)] * num_workers
    worker = async_worker(njit_omp, func_input, num_workers, split_task=False)

    for result in worker:
        pass


def main(params, no_run=False):
    n_observation = params.get("n_observation")
    n_feature_list = params.get("n_feature_list")
    sparsity = params.get("sparsity")
    noise_level = params.get("noise_level")
    filename_data = params.get("filename_data")
    file_name_omp = params.get("file_name_omp")
    gen_data_iter = params.get("gen_data_iter")
    omp_iter = params.get("omp_iter")
    methods_data = params.get("methods_data")
    methods_omp = params.get("methods_omp")
    mode = "r" if no_run else "w"

    algorithms_data = [
        (Keys.njit_atsign, njit_generate_data_atsign),
        (Keys.njit_npdot, njit_generate_data_npdot),
        (Keys.njit_parallel_atsign, njit_parallel_generate_data_atsign),
        (Keys.njit_parallel_npdot, njit_parallel_generate_data_npdot),
        (Keys.njit_parallel_unroll, njit_parallel_generate_data_unroll),
        (Keys.njit_parallel_unroll_threadpool, njit_parallel_generate_data_unroll_threadpool),
    ]
    algorithms_omp = [(Keys.njit, njit_omp), (Keys.njit_nogil_threadpool, njit_omp_threadpool)]

    if not no_run:
        for n_feature in n_feature_list:
            print(f"\n測試訊號維度: {n_feature}")

            # Test generate_data: Baseline
            _, base_time, _ = benchmark(
                generate_data,
                Keys.np_array,
                None,
                methods_data,
                n_observation,
                n_feature,
                sparsity,
                noise_level,
                iteration=gen_data_iter,
            )
            # Test generate_data: Numba
            for alg_name, alg_func in algorithms_data:
                workers = NUM_THREADS if "threadpool" in alg_name else 1
                benchmark(
                    alg_func,
                    alg_name,
                    base_time,
                    methods_data,
                    n_observation,
                    n_feature,
                    sparsity,
                    noise_level,
                    iteration=gen_data_iter,
                    workers=workers,
                )
            # Test omp: Baseline
            S, x_true, y = generate_data(n_observation, n_feature, sparsity, noise_level)
            _, base_time, _ = benchmark(
                omp,
                Keys.np_array,
                None,
                methods_omp,
                S,
                y,
                sparsity,
                iteration=max(omp_iter // 4, 1),
            )

            # Test omp: Numba
            for alg_name, alg_func in algorithms_omp:
                t = time.time()
                benchmark(
                    alg_func, alg_name, base_time, methods_omp, S, y, sparsity, iteration=omp_iter
                )
                print(f"Total time: {time.time() - t:.6f}")

        pop_results(methods_data)
        pop_results(methods_omp)

    # store and visualize
    with open(filename_data + ".json", mode) as f:
        if no_run:
            methods_data = json.load(f)
        else:
            json.dump(methods_data, f, indent=4)

    with open(file_name_omp + ".json", mode) as f:
        if no_run:
            methods_omp = json.load(f)
        else:
            json.dump(methods_omp, f, indent=4)

    # plot and ignore first warmup iteration
    try:  # for setting iter=0, plot would raise error
        plot(
            methods_data,
            n_feature_list[1:],
            filename_data + ".png",
            autoplot=True,
            xticks=n_feature_list[1:][::1],
        )
        plot(
            methods_omp,
            n_feature_list[1:],
            file_name_omp + ".png",
            autoplot=True,
            xticks=n_feature_list[1:][::1],
        )
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    from utils_omp import print_metrics, plot_results

    def showcase():
        # OMP simulation showcase
        n_observation = 100
        n_feature = 500
        sparsity = 0.05
        noise_level = 0.1
        S, x, y = generate_data(n_observation, n_feature, sparsity, noise_level)
        x_hat = njit_omp(S, y, sparsity)
        mse, tp_ratio, fp_ratio = calculate_metrics(x, x_hat, y, S)
        print_metrics(mse, tp_ratio, fp_ratio, n_feature)
        plot_results(x, x_hat, n_feature)

    params = {
        "n_observation": 100,
        "n_feature_list": np.insert(np.arange(2000, 20001, 2000), 0, [100, 500, 1000]),
        "sparsity": 0.05,
        "noise_level": 0.1,
        "filename_data": "generate_data_speedup",
        "file_name_omp": "omp_speedup",
        "gen_data_iter": 0,
        "omp_iter": 64,
        "methods_data": methods_data,
        "methods_omp": methods_omp,
    }

    main(params, no_run=False)
    showcase()
