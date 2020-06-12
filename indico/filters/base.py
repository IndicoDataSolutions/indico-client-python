from enum import Enum
from typing import Any, Dict, Iterable


class BaseFilter(dict):
    _filterable_columns = set()

    def __init__(self, filters: Dict[str, Any]):
        self._validate(filters)
        super().__init__(**filters)

    @property
    def filterable_columns(self):
        return self._filterable_columns

    @classmethod
    def _validate(cls, keys: Iterable):
        if not all(key in cls._filterable_columns for key in keys):
            raise TypeError()

    @classmethod
    def from_dict(cls, filters: Dict[str, Any]):
        cls._validate(filters.keys())
        return cls(filters)
