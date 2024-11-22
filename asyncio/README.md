# Asyncio test

1. async_future.py: basic usage of async future 
2. help: helper function for tests
3. v0_bad: i don't know what i'm writting
4. v1_basic: basic attempt for running a event loop in a sub thread
5. v2_no_lock: no lock attempt
6. v3_queue: use a queue
7. v4_no_queue: remove queue, only Semaphore, use run_coroutine_threadsafe
8. v3_queue_viz/v4_no_queue_viz: test files designed for use with VizTracer

Files prior to v3 can be ignored.
