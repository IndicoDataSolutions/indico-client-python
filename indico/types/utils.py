import re


_cc_to_snake_re = re.compile(r"(?<!^)(?=[A-Z])")
_snake_to_cc_re = re.compile(r"(.*?)_([a-zA-Z])")


def cc_to_snake(string: str):
    return re.sub(_cc_to_snake_re, "_", string).lower()


def _camel(match):
    return match.group(1) + match.group(2).upper()


def snake_to_cc(string: str):
    return re.sub(_snake_to_cc_re, _camel, string, 0)
