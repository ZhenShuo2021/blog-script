# trace compute time with viztracer, no lock.
import asyncio
import threading
from dataclasses import dataclass
from logging import Logger, getLogger
from typing import Any, Dict, Tuple, Callable, Optional

from help import io_task, print_thread_id, timer


@dataclass
class Task:
    task_id: str
    func: Callable[..., Any]
    args: Tuple[Any, ...] = ()
    kwargs: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.kwargs = self.kwargs or {}


class AsyncService:
    def __init__(self, logger: Logger, max_workers: int = 5) -> None:
        self.logger = logger

        # 任務運行相關設定
        self._running_tasks = 0
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self._loop_ready = threading.Event()
        self.sem = asyncio.Semaphore(max_workers)

        # 儲存結果
        self.results: Dict[str, Any] = {}

    def submit_task(self, task: Task) -> None:
        self._ensure_thread_active()

        self._running_tasks += 1
        asyncio.run_coroutine_threadsafe(self._schedule_tasks(task), self.loop)

    def submit_tasks(self, tasks: list[Task]) -> None:
        for task in tasks:
            self.submit_task(task)

    def fetch_result(self, task_id: str) -> Optional[Any]:
        return self.results.pop(task_id, None)

    def fetch_results(self, max_results: int = 0) -> Dict[str, Any]:
        if max_results <= 0:
            results_to_return = self.results.copy()
            self.results.clear()
            return results_to_return

        keys = list(self.results.keys())[:max_results]
        return {key: self.results.pop(key) for key in keys}

    def shutdown(self, timeout: Optional[float] = None) -> None:
        if self.thread is None or self.loop is None:
            return

        while True:
            if self._running_tasks == 0:
                break

        self.loop.call_soon_threadsafe(self.loop.stop)  # 停止事件迴圈
        self.thread.join(timeout=timeout)

        print(f"\n===no job! clearing thread {self.thread.native_id}===")
        self.thread = None
        print(f"===thread cleared! result: {self.thread}===\n")

    def _ensure_thread_active(self) -> None:
        if self.thread is None or not self.thread.is_alive():
            self._loop_ready.clear()
            self.thread = threading.Thread(target=self._start_event_loop)
            self.thread.start()
            self._loop_ready.wait()  # 等待事件迴圈啟動

    def _start_event_loop(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._loop_ready.set()
        self.loop.run_forever()
        try:
            self.loop.close()
        finally:
            self.loop = None
            self._loop_ready.clear()

    async def _schedule_tasks(self, task: Task) -> None:
        async with self.sem:
            print(
                f"Task {task.func.__name__} with args {task.args} and kwargs {task.kwargs} start running!"
            )
            try:
                result = await task.func(*task.args, **task.kwargs)
                self.results[task.task_id] = result
            except Exception as e:
                self.logger.error(f"Error processing task {task.task_id}: {e}")
                self.results[task.task_id] = None
            finally:
                self._running_tasks -= 1



@timer
def test() -> None:
    print_thread_id()
    logger = getLogger()
    task_template = [(0, "D1"), (0, "D2"), (0, "D3")]
    task_groups = [task_template for _ in range(300)]

    manager = AsyncService(logger, max_workers=5)

    for group in task_groups[:-1]:
        tasks = [Task(task[1], io_task, task) for task in group]
        manager.submit_tasks(tasks)

    results = manager.fetch_results()
    for result in results:
        print(result)

    manager.shutdown()

    for _ in range(3):
        results = manager.fetch_results()
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