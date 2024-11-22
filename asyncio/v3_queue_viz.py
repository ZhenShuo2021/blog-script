import asyncio
import queue
import threading
import time
from dataclasses import dataclass
from logging import Logger, getLogger
from typing import Any, Dict, Tuple, Callable, Optional

from help import BLOCK_MSG, NOT_BLOCK_MSG, io_task, print_thread_id, timer


@dataclass
class Task:
    """Unified task container for both threading and async services."""

    task_id: str
    func: Callable[..., Any]
    args: Tuple[Any, ...] = ()
    kwargs: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.kwargs = self.kwargs or {}


class AsyncService:
    def __init__(self, logger: Logger, max_workers: int = 5) -> None:
        # 載入變數
        self.max_workers = max_workers
        self.logger = logger

        # 任務運行相關設定
        self.is_running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.sem = asyncio.Semaphore(self.max_workers)
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # 儲存任務和結果的資料結構
        self.task_queue: queue.Queue[Task] = queue.Queue()
        self.results: Dict[str, Any] = {}
        self.current_tasks: list[asyncio.Task[Any]] = []

    def start(self) -> None:
        self._check_thread()

    def add_task(self, task: Task) -> None:
        self.task_queue.put(task)
        self._check_thread()

    def add_tasks(self, tasks: list[Task]) -> None:
        for task in tasks:
            self.task_queue.put(task)
        self._check_thread()

    def get_result(self, task_id: str) -> Optional[Any]:
        with self._lock:
            return self.results.pop(task_id, None)

    def get_results(self, max_results: int = 0) -> Dict[str, Any]:
        with self._lock:
            if max_results <= 0:
                results_to_return = self.results.copy()
                self.results.clear()
                return results_to_return

            keys = list(self.results.keys())[:max_results]
            return {key: self.results.pop(key) for key in keys}

    async def _process_tasks(self) -> None:
        while True:
            self.current_tasks = [task for task in self.current_tasks if not task.done()]

            if self.task_queue.empty() and not self.current_tasks:
                break

            while not self.task_queue.empty() and len(self.current_tasks) < self.max_workers:
                try:
                    task = self.task_queue.get_nowait()
                    task_obj = asyncio.create_task(self._run_task(task))
                    self.current_tasks.append(task_obj)
                except queue.Empty:
                    break

            if self.current_tasks:
                await asyncio.wait(self.current_tasks, return_when=asyncio.FIRST_COMPLETED)

    async def _run_task(self, task: Task) -> Any:
        async with self.sem:
            print(
                f"Task {task.func.__name__} with args {task.args} and kwargs {task.kwargs} start running!"
            )
            try:
                result = await task.func(*task.args, **task.kwargs)
                with self._lock:
                    self.results[task.task_id] = result
                return result
            except Exception as e:
                self.logger.error(f"Error processing task {task.task_id}: {e}")
                with self._lock:
                    self.results[task.task_id] = None

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
            self.loop.run_until_complete(self._process_tasks())
        finally:
            self.loop.close()
            self.loop = None
            self.is_running = False
            self.current_tasks.clear()

    def stop(self, timeout: Optional[float] = None) -> None:
        if self.thread is not None:
            self.thread.join(timeout=timeout)
            print(f"\n===no job! clearing thread {self.thread.native_id}===")
            self.thread = None
            self.is_running = False
            print(f"===thread cleared! result: {self.thread}===\n")


@timer
def test() -> None:
    print_thread_id()
    logger = getLogger()
    task_template = [(0, "D1"), (0, "D2"), (0, "D3")]
    task_groups = [task_template for _ in range(300)]

    manager = AsyncService(logger, max_workers=5)

    for group in task_groups[:-1]:
        tasks = [Task(task[1], io_task, task) for task in group]
        manager.add_tasks(tasks)

    results = manager.get_results()
    for result in results:
        print(result)

    manager.stop()

    for _ in range(3):
        results = manager.get_results()
        for result in results:
            print(result)

    # 在thread關閉後提交第二批任務
    # tasks = [Task(task[1], io_task, task) for task in task_groups[-1]]
    # manager.add_tasks(tasks)
    # manager.stop()
    # results = manager.get_results()
    # for result in results:
    #     print(result)


if __name__ == "__main__":
    print_thread_id()
    test()
