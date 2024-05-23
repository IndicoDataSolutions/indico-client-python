import asyncio
import time
from functools import wraps
from random import randint
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Awaitable, Callable, Optional, Tuple, Type, TypeVar, Union

    from typing_extensions import ParamSpec

    P = ParamSpec("P")
    T = TypeVar("T")


def retry(
    *ExceptionTypes: "Type[Exception]", tries: int = 3, delay: int = 1, backoff: int = 2
) -> "Callable[[Callable[P, T]], Callable[P, T]]":
    """
    Retry with exponential backoff

    Original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """

    def retry_decorator(f: "Callable[P, T]") -> "Callable[P, T]":
        @wraps(f)
        def retry_fn(*args: "P.args", **kwargs: "P.kwargs") -> "T":
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
    *ExceptionTypes: "Type[Exception]",
    tries: int = 3,
    delay: "Union[int, Tuple[int, int]]" = 1,
    backoff: int = 2,
    condition: "Optional[Callable[[Exception], bool]]" = None,
) -> "Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]":
    """
    Retry with exponential backoff

    Original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    Options:
        condition: Callable to evaluate if an exception of a given type
            is retryable for additional handling
        delay: an initial time to wait (seconds). If a tuple, choose a random number
            in that range to start. This can helps prevent retries at the exact
            same time across multiple concurrent function calls
    """

    def retry_decorator(f: "Callable[P, Awaitable[T]]") -> "Callable[P, Awaitable[T]]":
        @wraps(f)
        async def retry_fn(*args: "P.args", **kwargs: "P.kwargs") -> "T":
            n_tries = tries
            if isinstance(delay, tuple):
                # pick a random number to sleep
                n_delay = randint(*delay)
            else:
                n_delay = delay
            while True:
                try:
                    return await f(*args, **kwargs)
                except ExceptionTypes as e:
                    if condition and not condition(e):
                        raise
                    await asyncio.sleep(n_delay)
                    n_tries -= 1
                    n_delay *= backoff
                    if n_tries <= 0:
                        raise

        return retry_fn

    return retry_decorator
