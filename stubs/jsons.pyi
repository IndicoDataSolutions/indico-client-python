# the source lib is missing its py.typed marker

from typing import Callable

KEY_TRANSFORMER_CAMELCASE: Callable[[str], str]

def dump(
    obj: object, key_transformer: Callable[[str], str], strip_nulls: bool
) -> object: ...
def dumps(obj: object) -> str: ...
