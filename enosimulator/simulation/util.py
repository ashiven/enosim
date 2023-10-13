import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

_pool = ThreadPoolExecutor()


@asynccontextmanager
async def async_lock(lock):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_pool, lock.acquire)
    try:
        yield
    finally:
        lock.release()
