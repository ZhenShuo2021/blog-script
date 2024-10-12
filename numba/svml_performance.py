"""
Demonstrate Numba SVML
1. About ~5 times faster with SVML.
2. Data dtype: Only float32 and float64 enable SVML.
3. Fastmath: Enables SVML when turned on in this case.
"""

import os

os.environ["NUMBA_DISABLE_INTEL_SVML"] = "0"
import time
import numpy as np
import numba as nb


@nb.njit(fastmath=True)
def foo(a, b):
    res = 0.0
    for i in range(a.size):
        res += np.exp2(np.cos(a[i]) ** 2) + np.sqrt(np.log10(b[i]))
    return res


def run_test_float(n_size, n_time):
    a = np.random.rand(n_size)
    b = np.random.rand(n_size)

    foo(a, b)
    start_time = time.time()
    for _ in range(n_time):
        foo(a, b)
    end_time = time.time()

    return end_time - start_time


def run_test_complex(n_size, n_time):
    a = np.random.rand(n_size) + 1j * np.random.rand(n_size)
    b = np.random.rand(n_size) + 1j * np.random.rand(n_size)

    foo(a, b)
    start_time = time.time()
    for _ in range(n_time):
        foo(a, b)
    end_time = time.time()

    return end_time - start_time


if __name__ == "__main__":
    n_size = 100000
    n_time = 1000
    t1 = run_test_float(n_size, n_time)
    print(f"Elapsed time (float): {t1:.2f}s")

    t2 = run_test_complex(n_size, n_time)
    print(f"Elapsed time (complex): {t2:.2f}s")

# Without SVML
# Elapsed time (float): 2.48s
# Elapsed time (complex): 16.41s

# With SVML
# Elapsed time (float): 0.55s
# Elapsed time (complex): 16.47s
