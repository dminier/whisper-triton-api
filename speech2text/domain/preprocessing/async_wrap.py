import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from functools import wraps, partial

MAX_PREPROCESS_WORKER = os.environ.get('MAX_PREPROCESS_WORKER')
executor = ProcessPoolExecutor(max_workers=MAX_PREPROCESS_WORKER)


def async_preprocess_wrap(func):
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_running_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run
