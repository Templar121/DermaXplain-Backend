import asyncio
from concurrent.futures import ThreadPoolExecutor

# Global thread pool
executor = ThreadPoolExecutor(max_workers=3)

async def run_in_thread(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)
