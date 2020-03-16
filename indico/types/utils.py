import re


_cc_to_snake_re = re.compile(r'(?<!^)(?=[A-Z])')

def cc_to_snake(string: str):
    return re.sub(_cc_to_snake_re, '_', string).lower()


