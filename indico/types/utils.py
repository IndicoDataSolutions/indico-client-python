import re
import signal
from indico.errors import IndicoTimeoutError

_cc_to_snake_re = re.compile(r"(?<!^)(?=[A-Z])")
_snake_to_cc_re = re.compile(r"(.*?)_([a-zA-Z])")


def cc_to_snake(string: str):
    return re.sub(_cc_to_snake_re, "_", string).lower()


def _camel(match):
    return match.group(1) + match.group(2).upper()


def snake_to_cc(string: str):
    return re.sub(_snake_to_cc_re, _camel, string, 0)

class Timer:
    def __init__(self, timeout: int):
        self.timeout = timeout

    def _handler(self, signum, frame):
        raise IndicoTimeoutError(self.timeout)

    def run(self):
        if self.timeout == 0:
            raise IndicoTimeoutError(self.timeout)
        signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(self.timeout)