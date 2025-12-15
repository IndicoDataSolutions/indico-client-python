from typing import TYPE_CHECKING, Any, ClassVar, Tuple

from indico.errors import IndicoInputError

if TYPE_CHECKING:  # pragma: no cover
    from typing import List, Optional


class FilterV2(list):
    """
    Base filter class for V2 filters that serialize to a list of column filters.
    Structure: [{"column": "col_name", "filter": {"value": "val"}}, ...]
    """

    __options__: "ClassVar[Tuple[Any, ...]]" = tuple()

    def __init__(self, data: "Optional[List[dict]]" = None, **kwargs: "Any"):
        # Subclasses should handle complex logic and pass a list of dicts as 'data'.
        # If 'data' is provided, we use it directly.
        # Otherwise, we construct standard filters from kwargs.

        if data is None:
            data = []

            # Validate options if defined
            if self.__options__:
                for k in kwargs:
                    if k not in self.__options__:
                        raise IndicoInputError(
                            f"Argument {k} not in valid options: {self.__options__}"
                        )

            for k, v in kwargs.items():
                if v is not None:
                    if isinstance(v, list):
                        for item in v:
                            data.append({"column": k, "filter": {"value": item}})
                    else:
                        data.append({"column": k, "filter": {"value": v}})

        super().__init__(data)
