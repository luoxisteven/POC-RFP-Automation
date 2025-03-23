import asyncio

async def fetch_data(source):
    print(f"Fetching data from {source}...")
    await asyncio.sleep(2)  # 模拟耗时操作
    print(f"Data from {source} fetched!")
    return f"Data from {source}"

async def main():
    # 并行启动多个 fetch_data 任务
    task1 = fetch_data("Source 1")
    task2 = fetch_data("Source 2")
    task3 = fetch_data("Source 3")
    
    # 使用 asyncio.gather 并发等待所有任务完成
    results = await asyncio.gather(task1, task2, task3)
    print("All data fetched:", results)

# 运行主程序
asyncio.run(main())
