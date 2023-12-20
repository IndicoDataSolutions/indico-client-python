import asyncio
import time
import typing as t
from functools import wraps



def retry(
    ExceptionTypes: t.Type[Exception], tries: int = 3, delay: int = 1, backoff: int = 2
) -> t.Callable:
    """
    Retry with exponential backoff

    Original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """

    def retry_decorator(f: t.Callable) -> t.Any:
        @wraps(f)
        def retry_fn(*args: t.Any, **kwargs: t.Any) -> t.Any:
            n_tries, n_delay = tries, delay
            while n_tries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionTypes:
                    time.sleep(n_delay)
                    n_tries -= 1
                    n_delay *= backoff
            return f(*args, **kwargs)

        return retry_fn

    return retry_decorator

def aioretry(
    ExceptionTypes: t.Type[Exception], tries: int = 3, delay: int = 1, backoff: int = 2
) -> t.Callable:
    """
    Retry with exponential backoff

    Original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """

    def retry_decorator(f: t.Callable) -> t.Callable:
        @wraps(f)
        async def retry_fn(*args: t.Any, **kwargs: t.Any) -> t.Any:
            n_tries, n_delay = tries, delay
            while True:
                try:
                    return await f(*args, **kwargs)
                except ExceptionTypes:
                    await asyncio.sleep(n_delay)
                    n_tries -= 1
                    n_delay *= backoff
                    if n_tries <= 0:
                        raise

        return retry_fn

    return retry_decorator
