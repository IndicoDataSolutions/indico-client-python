import inspect
import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, cast, get_origin

from indico.types.utils import cc_to_snake

if TYPE_CHECKING:  # pragma: no cover
    from typing import Iterable, Optional

    from indico.typing import AnyDict

generic_alias_cls = type(List[Any])


def list_subtype(cls: "Any") -> "Optional[Any]":
    if not issubclass(type(cls), generic_alias_cls):
        return None

    origin: "Optional[type]" = getattr(
        cls, "__origin__", getattr(cls, "__extra__", None)
    )
    if (
        origin is not None
        and type(origin) == type
        and issubclass(origin, list)
        and cls.__args__
    ):
        return cls.__args__[0]

    return None


def valid_type(v: "Any") -> bool:
    if v is None:
        return False

    return (
        (inspect.isclass(v) and issubclass(v, BaseType))
        or v in [str, int, float, bool, JSONType, datetime]
        or get_origin(v) is dict
        or valid_type(list_subtype(v))
    )


# TODO: all the introspection here class makes the typing sus
class BaseType:
    def _get_attrs(self) -> "AnyDict":
        classes = inspect.getmro(self.__class__)
        props: "AnyDict" = dict()

        for c in classes:
            if not getattr(c, "__annotations__", None):
                continue
            props.update({k: v for k, v in c.__annotations__.items() if valid_type(v)})

        return props

    def __init__(self, **kwargs: "Any"):
        attrs: "AnyDict" = self._get_attrs()

        for k, v in kwargs.items():
            k = cc_to_snake(k)
            if k in attrs:
                attr_type = attrs[k]
                if (
                    v is not None
                    and inspect.isclass(attr_type)
                    and issubclass(attr_type, BaseType)
                ):
                    v = attrs[k](**v)

                if attr_type == JSONType and v is not None:
                    v = json.loads(v)

                if attr_type == datetime and v is not None:
                    try:
                        v = datetime.fromtimestamp(float(v))
                    except ValueError:
                        v = datetime.fromisoformat(v)

                subtype = list_subtype(attr_type)
                if subtype and issubclass(subtype, BaseType):
                    v = [subtype(**x) for x in cast("Iterable[Any]", v)]

                setattr(self, k, v)


class JSONType:
    pass
