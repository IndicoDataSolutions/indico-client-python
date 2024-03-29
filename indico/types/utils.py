import re
import time
from typing import TYPE_CHECKING

from indico.errors import IndicoTimeoutError

if TYPE_CHECKING:  # pragma: no cover
    from typing import NoReturn, Optional, Union

_cc_to_snake_re = re.compile(r"(?<!^)(?=[A-Z])")
_snake_to_cc_re = re.compile(r"(.*?)_([a-zA-Z])")


def cc_to_snake(string: str) -> str:
    return re.sub(_cc_to_snake_re, "_", string).lower()


def _camel(match: re.Match[str]) -> str:
    return match.group(1) + match.group(2).upper()


def snake_to_cc(string: str) -> str:
    return re.sub(_snake_to_cc_re, _camel, string, 0)


class Timer:
    def __init__(self, timeout: "Union[int, float]"):
        self.timeout: "Union[int, float]" = timeout
        self.start: float = time.time()
        self.elapsed: float = 0

    def check(self) -> "Optional[NoReturn]":
        self.elapsed = time.time() - self.start
        if self.timeout < self.elapsed:
            raise IndicoTimeoutError(self.elapsed)

        return None
