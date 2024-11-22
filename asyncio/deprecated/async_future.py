import asyncio


async def perform_task(future):
    print("start...")
    await asyncio.sleep(2)
    future.set_result("end")


async def main():
    # 建立一個Future對象
    future = asyncio.Future()
    
    # 啟動異步任務，並將future傳入
    await perform_task(future)
    
    # 檢查是否Future已經完成，並手動處理結果
    if future.done():
        print(f"最終結果: {future.result()}")


asyncio.run(main())
