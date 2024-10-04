import re
import time
from typing import TYPE_CHECKING

from pydantic.alias_generators import to_snake

from indico.errors import IndicoTimeoutError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Match, NoReturn, Optional, Union

_snake_to_cc_re = re.compile(r"(.*?)_([a-zA-Z])")


def cc_to_snake(string: str) -> str:
    return to_snake(string)


def _camel(match: "Match[str]") -> str:
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
