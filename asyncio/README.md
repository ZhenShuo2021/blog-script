# Asyncio Test  

- async_future.py: basic usage of an async future  
- help: helper functions for tests  
- v0_bad: my first bad attempt, just skip it   
- v1_basic: A basic attempt to run an event loop in a sub-thread  
- v2_no_lock: An attempt to remove locks  
- v3_queue: Use a queue for thread-safe operations  
- v4_no_queue: Removes the queue, only rely on a semaphore and run_coroutine_threadsafe  
- v3_queue_viz/v4_no_queue_viz: Test files for use with VizTracer  

Files before v3_queue can be ignored.
