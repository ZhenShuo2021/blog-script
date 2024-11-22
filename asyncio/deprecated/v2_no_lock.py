# forgot semaphore, leave as an example
import asyncio
import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from help import BLOCK_MSG, NOT_BLOCK_MSG, io_task, print_thread_id, timer


@dataclass
class AsyncTask:
    func: Callable[..., Any]
    args: tuple[Any, ...] = ()
    kwargs: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.kwargs = self.kwargs or {}


class AsyncTaskManager:
    def __init__(self, maxsize: int = 5):
        self.maxsize = maxsize
        self.is_running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.task_queue: queue.Queue[AsyncTask] = queue.Queue()
        self.result_queue: queue.Queue[Any] = queue.Queue()
        self.current_tasks: List[asyncio.Task[Any]] = []

    async def _consume_task(self) -> None:
        while True:
            self.current_tasks = [task for task in self.current_tasks if not task.done()]

            if self.task_queue.empty() and not self.current_tasks:
                break

            # 有空位才啟動新任務
            while len(self.current_tasks) < self.maxsize:
                try:
                    task = self.task_queue.get_nowait()
                    task_obj = asyncio.create_task(self.run_task(task))
                    self.current_tasks.append(task_obj)
                except queue.Empty:
                    break

            if self.current_tasks:
                await asyncio.wait(self.current_tasks, return_when=asyncio.FIRST_COMPLETED)

    async def run_task(self, task: AsyncTask) -> Any:
        print(
            f"Task {task.func.__name__} with args {task.args} and kwargs {task.kwargs} start running!"
        )
        result = await task.func(*task.args, **task.kwargs)  # type: ignore
        self.result_queue.put(result)
        return result

    def produce_task(self, task: AsyncTask) -> None:
        self.task_queue.put(task)
        self._check_thread()

    def produce_task_list(self, tasks: List[AsyncTask]) -> None:
        for task in tasks:
            self.task_queue.put(task)
        self._check_thread()

    def get_result(self, max_item_retrieve: int = 3) -> list[AsyncTask]:
        items: list[Any] = []
        retrieve_all = max_item_retrieve == 0
        while retrieve_all or len(items) < max_item_retrieve:
            try:
                items.append(self.result_queue.get_nowait())
            except queue.Empty:
                break
        return items

    def _check_thread(self) -> None:
        with self._lock:
            if not self.is_running or self.thread is None or not self.thread.is_alive():
                self.is_running = True
                self.thread = threading.Thread(target=self._start_event_loop)
                self.thread.start()

    def _start_event_loop(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._consume_task())
        finally:
            self.loop.close()
            self.loop = None
            self.is_running = False
            self.current_tasks.clear()

    def close_thread(self, timeout: Optional[int] = None) -> None:
        if self.thread is not None:
            self.thread.join(timeout=timeout)
            print(f"\n===no job! clearing thread {self.thread.native_id}===")
            self.thread = None
            print(f"===thread cleared! result: {self.thread}===\n")


@timer
def test() -> None:
    print_thread_id()
    task_groups = [
        [(1, "A1"), (2, "A2"), (3, "A3")],
        [(3, "B1"), (4, "B2"), (5, "B3")],
        [(3, "C1"), (4, "C2"), (5, "C3")],
        [(1, "D1"), (2, "D2"), (3, "D3")],
    ]

    manager = AsyncTaskManager(maxsize=5)

    # 提交第一批任務，使用新的produce_task_list方法
    for group in task_groups[:-1]:
        tasks = [AsyncTask(io_task, task) for task in group]
        manager.produce_task_list(tasks)

    print(NOT_BLOCK_MSG)

    # 模擬主執行緒工作需要 2.5 秒，在程式中間取得結果
    # 會顯示 A1/A2 的結果，因為它們在 2.5 秒後完成
    time.sleep(2.5)
    results = manager.get_result()
    print(NOT_BLOCK_MSG, "(2s waiting for main thread itself)")  # not blocked
    for result in results:
        print(result)

    # 等待子執行緒結束，造成阻塞
    manager.close_thread()
    print(BLOCK_MSG)

    for _ in range(3):
        results = manager.get_result()
        for result in results:
            print(result)

    # 在thread關閉後提交第二批任務，使用新的produce_task_list方法
    tasks = [AsyncTask(io_task, task) for task in task_groups[-1]]
    manager.produce_task_list(tasks)
    manager.close_thread()
    results = manager.get_result()
    for result in results:
        print(result)


if __name__ == "__main__":
    print_thread_id()
    test()
