from dataclasses import dataclass


@dataclass(frozen=True)
class Keys:
    np_array: str = "Baseline (numpy array)"
    njit: str = "njit"
    njit_parallel: str = "njit_parallel"
    njit_nogil_threadpool: str = "njit_nogil_threadpool"
    njit_parallel_nogil_threadpool: str = "njit_parallel_nogil_threadpool"
    njit_nogil: str = "njit_nogil"
    njit_parallel_nogil: str = "njit_parallel_nogil"
    vectorize: str = "vectorize"
    guvectorize: str = "guvectorize"


methods: dict[str, dict] = {
    Keys.np_array: {
        "style": {"marker": "o", "linestyle": "-", "color": "k"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit: {
        "style": {"marker": "s", "linestyle": "-", "color": "r"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_parallel: {
        "style": {"marker": "s", "linestyle": "-", "color": "b"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.njit_nogil_threadpool: {
        "style": {"marker": "s", "linestyle": "-", "color": "g"},
        "result": {"time": [], "speedup_ratio": []},
    },
    # Keys.njit_nogil: {
    #     "style": {"marker": "s", "linestyle": "--", "color": "g"},
    #     "result": {"time": [], "speedup_ratio": []},
    # },
    # Keys.njit_parallel_nogil: {
    #     "style": {"marker": "s", "linestyle": "-", "color": "g"},
    #     "result": {"time": [], "speedup_ratio": []},
    # },
    Keys.njit_parallel_nogil_threadpool: {
        "style": {"marker": "s", "linestyle": "-", "color": "m"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.vectorize: {
        "style": {"marker": "D", "linestyle": ":", "color": "c"},
        "result": {"time": [], "speedup_ratio": []},
    },
    Keys.guvectorize: {
        "style": {"marker": "D", "linestyle": ":", "color": "y"},
        "result": {"time": [], "speedup_ratio": []},
    },
}

if __name__ == "__main__":
    import json

    print(json.dumps(methods, indent=4))
    print(Keys.np_array)
