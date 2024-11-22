import asyncio
import threading
import time
from typing import Any, Dict, Callable, Tuple

BLOCK_MSG = "\n===main thread blocked, not showing immediately==="
NOT_BLOCK_MSG = "\n===main thread not blocked==="


async def io_task(duration: float, task_id: str, **kwargs: Dict[Any, Any]) -> str:
    await asyncio.sleep(duration)
    return f"Task {task_id} with args {duration, task_id} kwargs {kwargs} completed after {duration} seconds"


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Tuple[Any, Any], **kwargs: Dict[Any, Any]) -> Any:
        t = time.time()
        result = func(*args, **kwargs)
        print(f"program time: {(time.time() - t):.6f}")
        return result

    return wrapper


def print_thread_id(is_main_thread: bool=True) -> None:
    if is_main_thread:
        if threading.current_thread() == threading.main_thread():
            print("main thread id =", threading.get_ident())
    elif threading.current_thread() != threading.main_thread():
        print("sub thread id =", threading.get_ident())


def parse_input(params: tuple[Any, Any]) -> tuple[Any, Any]:
    if len(params) == 0:
        return (), {}
    elif len(params) == 1:
        if isinstance(params[0], dict):
            return (), params[0]
        else:
            return params[0], {}
    elif len(params) == 2:  # noqa: PLR2004
        return params
    else:
        return None
