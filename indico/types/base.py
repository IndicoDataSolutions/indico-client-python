import inspect
import json
from typing import List, Any
from indico.types.utils import cc_to_snake

generic_alias_cls = type(List[Any])


def list_subtype(cls):
    if not issubclass(type(cls), generic_alias_cls):
        return None
    origin = getattr(cls, "__origin__", getattr(cls, "__extra__", None))
    if issubclass(origin, list) and cls.__args__:
        return cls.__args__[0]
    return None


def valid_type(v):
    if v is None:
        return False

    return (
        (inspect.isclass(v) and issubclass(v, BaseType))
        or v in [str, int, float, bool, JSONType]
        or valid_type(list_subtype(v))
    )


class BaseType:
    def _get_attrs(self):
        classes = inspect.getmro(self.__class__)
        props = dict()
        for c in classes:
            if not getattr(c, "__annotations__", None):
                continue

            props.update({k: v for k, v in c.__annotations__.items() if valid_type(v)})

        return props

    def __init__(self, **kwargs):
        attrs = self._get_attrs()
        for k, v in kwargs.items():
            k = cc_to_snake(k)
            if k in attrs:
                attr_type = attrs[k]
                if inspect.isclass(attr_type) and issubclass(attr_type, BaseType):
                    if v:
                        v = attrs[k](**v)
                if attr_type == JSONType:
                    v = json.loads(v)

                subtype = list_subtype(attr_type)
                if subtype and issubclass(subtype, BaseType):
                    v = [subtype(**x) for x in v]
                setattr(self, k, v)


class JSONType:
    pass
