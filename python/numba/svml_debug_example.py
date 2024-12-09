# This script is an example to verify whether a function is successfully parallelized using SVML.
# Usage: Run `python svml_debug_example.py | grep svml` to check for SVML optimizations.
# If SVML is utilized, the output should include the following machine instructions:
# movabsq $__svml_sqrt4, %r13

from numba import njit
import numpy as np

# Uncommend for full debug info
# import llvmlite.binding as llvm
# llvm.set_option("", "--debug-only=loop-vectorize")


@njit(fastmath=True)
def foo(x):
    acc = 0
    for i in x:
        y = np.sqrt(i)
        acc += y
    return acc

foo(np.arange(100.))
print(foo.inspect_asm(foo.signatures[0]))
