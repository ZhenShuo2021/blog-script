import asyncio
import queue
import threading
import time
from typing import Optional

from help import BLOCK_MSG, NOT_BLOCK_MSG, io_task, print_thread_id, timer


class AsyncTaskManager:
    def __init__(self, maxsize: int = 5):
        self.maxsize = maxsize
        self.is_running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.task_queue = queue.Queue()  # 儲存所有等待執行的任務
        self.result_queue = queue.Queue()  # 儲存執行結果
        self.current_tasks = []  # 正在執行的任務清單

    async def _process_queue(self):
        while True:
            # 沒有任務則退出
            if self.task_queue.empty() and not self.current_tasks:
                break

            # 檢查並移除已完成的任務
            self.current_tasks = [task for task in self.current_tasks if not task.done()]

            # 有空位則啟動新任務
            while len(self.current_tasks) < self.maxsize:
                try:
                    func, args, kwargs = self.task_queue.get_nowait()
                    task = asyncio.create_task(self.run_task(func, *args, **kwargs))
                    self.current_tasks.append(task)
                except queue.Empty:
                    break

            if self.current_tasks:
                # 等待任務完成
                await asyncio.wait(self.current_tasks, return_when=asyncio.FIRST_COMPLETED)
            else:
                # 等待後再檢查
                await asyncio.sleep(0.1)

    async def run_task(self, func, *args, **kwargs):
        print(f"Task {func.__name__} with args {args} and kwargs {kwargs} start running!")
        print_thread_id(is_main_thread=False)
        result = await func(*args, **kwargs)
        self.result_queue.put(result)
        return result

    def add_task(self, func, *args, **kwargs):
        self.task_queue.put((func, args, kwargs))
        self._check_thread()

    def get_result(self):
        items = []
        while True:
            try:
                items.append(self.result_queue.get_nowait())
            except queue.Empty:
                break
        return items

    def _check_thread(self):
        if not self.is_running or self.thread is None or not self.thread.is_alive():
            self.is_running = True
            self.thread = threading.Thread(target=self._start_event_loop)
            self.thread.start()

    def _start_event_loop(self):
        self.loop = asyncio.new_event_loop()
        print_thread_id(is_main_thread=True)
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._process_queue())
        finally:
            self.loop.close()
            self.loop = None
            self.is_running = False
            self.current_tasks.clear()

    def close_thread(self):
        if self.thread is not None:
            print(f"\n===no job! clearing thread {self.thread.native_id}===")
            self.thread.join()
            self.thread = None
            print(f"===thread cleared! result: {self.thread}===\n")


@timer
def test():
    print_thread_id()
    block_time = time.time()

    manager = AsyncTaskManager(maxsize=5)

    manager.add_task(io_task, 1, "A1")
    manager.add_task(io_task, 2, "A2")
    manager.add_task(io_task, 3, "A3")

    manager.add_task(io_task, 3, "B1")
    manager.add_task(io_task, 4, "B2")
    manager.add_task(io_task, 5, "B3")

    manager.add_task(io_task, 3, "C1")
    manager.add_task(io_task, 4, "C2")
    manager.add_task(io_task, 5, "C3")

    print(NOT_BLOCK_MSG)

    # 模擬主執行緒工作需要 2.5 秒，在程式中間取得結果
    # 會顯示 A1/A2 的結果，因為它們在 2.5 秒後完成
    time.sleep(2.5)
    results = manager.get_result()

    block_time = time.time() - block_time
    print(NOT_BLOCK_MSG, f"({(block_time):.1f}s waiting for job of main thread itself)")  # not blocked
    for result in results:
        print(result)

    # 等待子執行緒結束
    manager.close_thread()
    print(BLOCK_MSG)

    results = manager.get_result()
    for result in results:
        print(result)

    # 可以在thread關閉後再次建立工作
    manager.add_task(io_task, 1, "D1")
    manager.add_task(io_task, 2, "D2")
    manager.add_task(io_task, 3, "D3")

    manager.close_thread()
    results = manager.get_result()
    for result in results:
        print(result)


if __name__ == "__main__":
    print_thread_id()
    test()
