from dataclasses import dataclass
from math import sqrt
import numpy as np
import numba

import matplotlib.pyplot as plt
import matplotlib as mpl

from utils import async_worker

mpl.rcParams["figure.dpi"] = 240


def lsqr_numpy(A, b, itnlim=0, damp=0.0, atol=1.0e-9, btol=1.0e-9, conlim=1.0e8):
    """
    Solve the least-squares problem using LSQR.

    The function minimizes the residual ||Ax - b||, where A is the matrix and b is the target vector.

    Args:
        A (np.ndarray): Coefficient matrix of shape (m, n).
        b (np.ndarray): Target vector of shape (m,).
        itnlim (int, optional): Maximum number of iterations. Defaults to 0 (3 * n).
        damp (float, optional): Regularization parameter. Defaults to 0.0.
        atol (float, optional): Absolute tolerance for convergence. Defaults to 1.0e-9.
        btol (float, optional): Relative tolerance for convergence. Defaults to 1.0e-9.
        conlim (float, optional): Condition limit. Defaults to 1.0e8.

    Returns:
        np.ndarray: Solution vector x that minimizes ||Ax - b||.
    """
    m, n = A.shape

    if itnlim == 0:
        itnlim = 3 * n

    dampsq = damp * damp

    itn = 0
    istop = 0
    ctol = 0.0
    if conlim > 0.0:
        ctol = 1.0 / conlim
    Anorm = Acond = 0.0
    z = xnorm = xxnorm = ddnorm = res2 = 0.0
    cs2 = -1.0
    sn2 = 0.0

    x = np.zeros(n)
    xNrgNorm2 = 0.0

    u = b.copy()
    beta = np.linalg.norm(u)
    if beta > 0:
        u /= beta

        v = A.T @ u
        alpha = np.linalg.norm(v)

    if alpha > 0:
        v /= alpha
        w = v.copy()

    x_is_zero = False
    Arnorm = alpha * beta
    if Arnorm == 0.0:
        x_is_zero = True
        istop = 0

    rhobar = alpha
    phibar = beta
    bnorm = beta
    rnorm = beta
    r1norm = rnorm
    r2norm = rnorm

    # Main iteration loop.
    while itn < itnlim and not x_is_zero:
        itn = itn + 1

        u = A @ v - alpha * u
        beta = np.linalg.norm(u)
        if beta > 0:
            u /= beta

            Anorm = sqrt(Anorm**2 + alpha**2 + beta**2 + damp**2)

            v = A.T @ u - beta * v
            alpha = np.linalg.norm(v)
            if alpha > 0:
                v /= alpha

        rhobar1 = sqrt(rhobar**2 + damp**2)
        cs1 = rhobar / rhobar1
        sn1 = damp / rhobar1
        psi = sn1 * phibar
        phibar = cs1 * phibar

        rho = sqrt(rhobar1**2 + beta**2)
        cs = rhobar1 / rho
        sn = beta / rho
        theta = sn * alpha
        rhobar = -cs * alpha
        phi = cs * phibar
        phibar = sn * phibar
        tau = sn * phi

        t1 = phi / rho
        t2 = -theta / rho
        dk = (1.0 / rho) * w

        x += t1 * w
        w *= t2
        w += v
        ddnorm += np.linalg.norm(dk) ** 2

        xNrgNorm2 += phi * phi

        delta = sn2 * rho
        gambar = -cs2 * rho
        rhs = phi - delta * z
        zbar = rhs / gambar
        xnorm = sqrt(xxnorm + zbar**2)
        gamma = sqrt(gambar**2 + theta**2)
        cs2 = gambar / gamma
        sn2 = theta / gamma
        z = rhs / gamma
        xxnorm += z * z

        Acond = Anorm * sqrt(ddnorm)
        res1 = phibar**2
        res2 = res2 + psi**2
        rnorm = sqrt(res1 + res2)
        Arnorm = alpha * abs(tau)

        r1sq = rnorm**2 - dampsq * xxnorm
        r1norm = sqrt(abs(r1sq))
        if r1sq < 0:
            r1norm = -r1norm
        r2norm = rnorm

        test1 = rnorm / bnorm
        if Anorm == 0.0 or rnorm == 0.0:
            test2 = float("inf")
        else:
            test2 = Arnorm / (Anorm * rnorm)
        if Acond == 0.0:
            test3 = float("inf")
        else:
            test3 = 1.0 / Acond
        t1 = test1 / (1 + Anorm * xnorm / bnorm)
        rtol = btol + atol * Anorm * xnorm / bnorm

        if itn >= itnlim:
            istop = 7
        if 1 + test3 <= 1:
            istop = 6
        if 1 + test2 <= 1:
            istop = 5
        if 1 + t1 <= 1:
            istop = 4

        if test3 <= ctol:
            istop = 3
        if test2 <= atol:
            istop = 2
        if test1 <= rtol:
            istop = 1

        if istop > 0:
            break

    return x


@numba.njit
def njit_lsqr_numpy(A, b, itnlim=0, damp=0.0, atol=1.0e-9, btol=1.0e-9, conlim=1.0e8):
    """
    Solve the least-squares problem using LSQR.

    The function minimizes the residual ||Ax - b||, where A is the matrix and b is the target vector.

    Args:
        A (np.ndarray): Coefficient matrix of shape (m, n).
        b (np.ndarray): Target vector of shape (m,).
        itnlim (int, optional): Maximum number of iterations. Defaults to 0 (3 * n).
        damp (float, optional): Regularization parameter. Defaults to 0.0.
        atol (float, optional): Absolute tolerance for convergence. Defaults to 1.0e-9.
        btol (float, optional): Relative tolerance for convergence. Defaults to 1.0e-9.
        conlim (float, optional): Condition limit. Defaults to 1.0e8.

    Returns:
        np.ndarray: Solution vector x that minimizes ||Ax - b||.
    """
    m, n = A.shape

    if itnlim == 0:
        itnlim = 3 * n

    dampsq = damp * damp

    itn = 0
    istop = 0
    ctol = 0.0
    if conlim > 0.0:
        ctol = 1.0 / conlim
    Anorm = Acond = 0.0
    z = xnorm = xxnorm = ddnorm = res2 = 0.0
    cs2 = -1.0
    sn2 = 0.0

    x = np.zeros(n)
    xNrgNorm2 = 0.0

    u = b.copy()
    beta = np.linalg.norm(u)
    if beta > 0:
        u /= beta

        v = A.T @ u
        alpha = np.linalg.norm(v)

    if alpha > 0:
        v /= alpha
        w = v.copy()

    x_is_zero = False
    Arnorm = alpha * beta
    if Arnorm == 0.0:
        x_is_zero = True
        istop = 0

    rhobar = alpha
    phibar = beta
    bnorm = beta
    rnorm = beta
    r1norm = rnorm
    r2norm = rnorm

    # Main iteration loop.
    while itn < itnlim and not x_is_zero:
        itn = itn + 1

        u = A @ v - alpha * u
        beta = np.linalg.norm(u)
        if beta > 0:
            u /= beta

            Anorm = sqrt(Anorm**2 + alpha**2 + beta**2 + damp**2)

            v = A.T @ u - beta * v
            alpha = np.linalg.norm(v)
            if alpha > 0:
                v /= alpha

        rhobar1 = sqrt(rhobar**2 + damp**2)
        cs1 = rhobar / rhobar1
        sn1 = damp / rhobar1
        psi = sn1 * phibar
        phibar = cs1 * phibar

        rho = sqrt(rhobar1**2 + beta**2)
        cs = rhobar1 / rho
        sn = beta / rho
        theta = sn * alpha
        rhobar = -cs * alpha
        phi = cs * phibar
        phibar = sn * phibar
        tau = sn * phi

        t1 = phi / rho
        t2 = -theta / rho
        dk = (1.0 / rho) * w

        x += t1 * w
        w *= t2
        w += v
        ddnorm += np.linalg.norm(dk) ** 2

        xNrgNorm2 += phi * phi

        delta = sn2 * rho
        gambar = -cs2 * rho
        rhs = phi - delta * z
        zbar = rhs / gambar
        xnorm = sqrt(xxnorm + zbar**2)
        gamma = sqrt(gambar**2 + theta**2)
        cs2 = gambar / gamma
        sn2 = theta / gamma
        z = rhs / gamma
        xxnorm += z * z

        Acond = Anorm * sqrt(ddnorm)
        res1 = phibar**2
        res2 = res2 + psi**2
        rnorm = sqrt(res1 + res2)
        Arnorm = alpha * abs(tau)

        r1sq = rnorm**2 - dampsq * xxnorm
        r1norm = sqrt(abs(r1sq))
        if r1sq < 0:
            r1norm = -r1norm
        r2norm = rnorm

        test1 = rnorm / bnorm
        if Anorm == 0.0 or rnorm == 0.0:
            test2 = float("inf")
        else:
            test2 = Arnorm / (Anorm * rnorm)
        if Acond == 0.0:
            test3 = float("inf")
        else:
            test3 = 1.0 / Acond
        t1 = test1 / (1 + Anorm * xnorm / bnorm)
        rtol = btol + atol * Anorm * xnorm / bnorm

        if itn >= itnlim:
            istop = 7
        if 1 + test3 <= 1:
            istop = 6
        if 1 + test2 <= 1:
            istop = 5
        if 1 + t1 <= 1:
            istop = 4

        if test3 <= ctol:
            istop = 3
        if test2 <= atol:
            istop = 2
        if test1 <= rtol:
            istop = 1

        if istop > 0:
            break

    return x


def omp(S, y, sparsity, itrMax=100):
    """
    Orthogonal Matching Pursuit (OMP) algorithm.

    Args:
      S: Sensing matrix (numpy array)
      y: Measurement vector (numpy array)
      sparsity: Sparsity level (integer)
      itrMax: Maximum number of iterations (integer)

    Returns:
      x: Estimated sparse signal (numpy array)
    """

    n_feature = S.shape[1]
    support = int(sparsity * n_feature)
    x = np.zeros(n_feature)
    residual = y
    support_set = np.zeros(n_feature, dtype=np.bool_)

    for _ in range(max(itrMax, support)):
        corr_max = 0
        est_act = 0
        for ii in range(n_feature):
            corr = abs(np.dot(residual, S[:, ii]))
            if corr > corr_max:
                corr_max = corr
                est_act = ii

        support_set[est_act] = True
        S_active = S[:, support_set]
        x_hat = njit_lsqr_numpy(S_active, y)
        residual = y - S_active @ x_hat

        if np.sum(support_set) >= support:
            break
    x[support_set] = x_hat  # type: ignore
    return x


@numba.njit(nogil=True)
def njit_omp(S, y, sparsity, itrMax=100):
    n_feature = S.shape[1]
    support = int(sparsity * n_feature)
    x = np.zeros(n_feature)
    residual = y
    support_set = np.zeros(n_feature, dtype=np.bool_)

    for _ in range(max(itrMax, support)):
        corr_arr = np.zeros(n_feature)
        est_act = 0
        for ii in numba.prange(n_feature):
            corr_arr[ii] = abs(np.dot(residual, S[:, ii]))
        est_act = np.argmax(corr_arr)

        support_set[est_act] = True
        S_active = S[:, support_set]
        x_hat = njit_lsqr_numpy(S_active, y)
        residual = y - S_active @ x_hat

        if np.sum(support_set) >= support:
            break
    x[support_set] = x_hat  # type: ignore
    return x


@numba.jit(inline="always")
def gen_data_basis(n_observation, n_feature, sparsity):
    S = np.random.randn(n_observation, n_feature)
    x = np.zeros(n_feature)
    support = np.random.choice(n_feature, int(sparsity * n_feature), replace=False)
    x[support] = np.random.randn(len(support))
    return S, x


def generate_data(n_observation, n_feature, sparsity, noise_level=0.1):
    """
    Generates the sensing matrix, true coefficients, and observation vector.

    Args:
      n_observation (int):  The number of samples.
      n_feature (int): The number of features.
      sparsity (float):  The sparsity level.
      noise_level (float): The standard deviation of the noise.

    Returns:
      S (float): A n_observation-by-n_feature dimension matrix.
      x (float): A n_feature dimension vector.
      y (float): A n_feature dimension vector.
    """
    np.random.seed(42)
    S = np.random.randn(n_observation, n_feature)
    x = np.zeros(n_feature)
    support = np.random.choice(n_feature, int(sparsity * n_feature), replace=False)
    x[support] = np.random.randn(len(support))
    y = S @ x + np.random.randn(n_observation) * noise_level
    return S, x, y


@numba.njit
def njit_generate_data_npdot(n_observation, n_feature, sparsity, noise_level=0.1):
    S, x = gen_data_basis(n_observation, n_feature, sparsity)
    y = np.dot(S, x) + np.random.randn(n_observation) * noise_level
    return S, x, y


@numba.njit
def njit_generate_data_atsign(n_observation, n_feature, sparsity, noise_level=0.1):
    S, x = gen_data_basis(n_observation, n_feature, sparsity)
    y = S @ x + np.random.randn(n_observation) * noise_level
    return S, x, y


@numba.njit(parallel=True)
def njit_parallel_generate_data_npdot(n_observation, n_feature, sparsity, noise_level=0.1):
    S, x = gen_data_basis(n_observation, n_feature, sparsity)
    y = np.dot(S, x) + np.random.randn(n_observation) * noise_level
    return S, x, y


@numba.njit(parallel=True)
def njit_parallel_generate_data_atsign(n_observation, n_feature, sparsity, noise_level=0.1):
    S, x = gen_data_basis(n_observation, n_feature, sparsity)
    y = S @ x + np.random.randn(n_observation) * noise_level
    return S, x, y


@numba.njit(parallel=True, nogil=True)
def njit_parallel_generate_data_unroll(n_observation, n_feature, sparsity, noise_level=0.1):
    S, x = gen_data_basis(n_observation, n_feature, sparsity)

    # generate data
    noise = np.random.randn(n_observation)
    y = np.zeros(n_observation)
    for i in numba.prange(n_observation):
        # y[i] = np.dot(S[i], x) + noise[i] * noise_level
        sum_product = 0.0
        for j in range(n_observation):
            sum_product += S[i, j] * x[j]
        y[i] = sum_product + noise[i] * noise_level
    return S, x, y


# Utils for OMP simulation
def calculate_metrics(x, x_hat, y, S):
    residual = y - S @ x_hat
    mse = np.mean(residual**2)

    true_support = np.where(x != 0)[0]
    estimated_support = np.where(x_hat != 0)[0]
    tp = len(set(true_support) & set(estimated_support))
    tp_ratio = tp / len(true_support) if len(true_support) > 0 else 0
    fp = len(estimated_support) - tp
    fp_ratio = fp / len(estimated_support) if len(estimated_support) > 0 else 0

    return mse, tp_ratio, fp_ratio


def plot_results(x, x_hat, n_feature):
    plt.clf()
    plt.plot(x, label="True Coefficients")
    plt.plot(x_hat, label="Estimated Coefficients", linestyle="--")
    plt.xlabel("Coefficient Index")
    plt.ylabel("Coefficient Value")
    plt.title(f"BOMP Algorithm - True vs. Estimated Coefficients (n_feature={n_feature})")
    plt.legend()
    plt.savefig("123", bbox_inches="tight")
    plt.show()


def print_metrics(mse, tp_ratio, fp_ratio, n_feature):
    """
    Prints the evaluation metrics.

    Args:
      mse: The mean squared error.
      tp_ratio: The true positive ratio.
      fp_ratio: The false positive ratio.
      n_feature: The number of features.
    """
    print(f"n_feature: {n_feature}")
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"True Positive Ratio (TP ratio): {tp_ratio:.4f}")
    print(f"False Positive Ratio (FP ratio): {fp_ratio:.4f}")


@dataclass(frozen=True)
class Keys:
    # generate data
    np_array: str = "Baseline (numpy array)"
    njit_atsign: str = "njit_atsign"
    njit_npdot: str = "njit_npdot"
    njit_parallel_atsign: str = "njit_parallel_atsign"
    njit_parallel_npdot: str = "njit_parallel_npdot"
    njit_parallel_unroll: str = "njit_parallel_unroll"
    njit_parallel_unroll_threadpool: str = "njit_parallel_unroll_threadpool"
    
    # omp
    njit: str = "njit"
    njit_nogil_threadpool: str = "njit_threadpool"

methods_data = {
    Keys.np_array: {
        "style": {"marker": "o", "linestyle": "-", "color": "r"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_atsign: {
        "style": {"marker": "o", "linestyle": "-", "color": "g"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_npdot: {
        "style": {"marker": "o", "linestyle": "-", "color": "g"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_parallel_atsign: {
        "style": {"marker": "o", "linestyle": "-", "color": "b"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_parallel_npdot: {
        "style": {"marker": "o", "linestyle": "-", "color": "b"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_parallel_unroll: {
        "style": {"marker": "o", "linestyle": "-", "color": "b"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_parallel_unroll_threadpool: {
        "style": {"marker": "o", "linestyle": "-", "color": "b"},
        "result": {"time": [], "speedup_ratio": []},
    },
}

methods_omp = {
    Keys.np_array: {
        "style": {"marker": "o", "linestyle": "-", "color": "r"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit: {
        "style": {"marker": "o", "linestyle": "-", "color": "g"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_nogil_threadpool: {
        "style": {"marker": "o", "linestyle": "-", "color": "b"},
        "result": {"time": [], "speedup_ratio": []},
    },
}
