import asyncio
import functools

def retry(max_attempts=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    print(f"    ⚠️ Attempt {attempt} failed in {func.__name__}: {e}. Retrying...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
