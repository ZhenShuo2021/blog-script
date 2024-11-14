import asyncio
import time


class AsyncQueueWorker:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.task_queue = asyncio.Queue()

    async def producer(self, task_id):
        print(f"producer id {task_id} start")
        await asyncio.sleep(1)
        await self.task_queue.put(task_id)
        print(f"producer id {task_id} finish")

    async def consumer(self):
        while True:
            task_id = await self.task_queue.get()
            if task_id is None:
                break
            print(f"consumer id {task_id} start")
            await asyncio.sleep(0.5)
            print(f"consumer id {task_id} finish")
            self.task_queue.task_done()

    async def start(self):
        tasks = []
        for _ in range(self.max_workers):
            tasks.append(asyncio.create_task(self.consumer()))
        return tasks

    async def stop(self):
        for _ in range(self.max_workers):
            await self.task_queue.put(None)


async def main():
    start_time = time.time()

    worker = AsyncQueueWorker(max_workers=3)
    worker_tasks = await worker.start()

    tasks = []
    for i in range(3):
        tasks.append(worker.producer(i))

    await asyncio.gather(*tasks)

    for i in range(3):
        tasks.append(worker.producer(i))

    t = time.time()
    await asyncio.sleep(0.1)
    print("main func time", time.time() - t)

    tasks = []
    for i in range(10, 13):
        tasks.append(worker.producer(i))
    await asyncio.gather(*tasks)

    await worker.stop()

    end_time = time.time()
    print(f"program time {end_time - start_time:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
