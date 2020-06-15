from enum import Enum
from typing import Any, Dict, Iterable


class BaseFilter(dict):
    """
    Base filter class that allows users to construct filter statements for
    GraphQL queries. Columns are restricted to a particular set of database columns
    determined by the specific resource a user queries.

    Note:
        Class should be extended for specific Indico resources, and the subclasses 
        instantiated when a query is constructed.
    """

    _filterable_columns = set()

    def __init__(self, filters: Dict[str, Any]):
        self._validate(filters)
        super().__init__(**filters)

    def _validate(self, keys: Iterable):
        if not all(key in self._filterable_columns for key in keys):
            invalid_keys = self._filterable_columns.difference(set(keys))
            raise ValueError(
                f"Can only filter on {self._filterable_columns}, not {invalid_keys}"
            )

    @property
    def filterable_columns(self):
        return self._filterable_columns

    @classmethod
    def from_dict(cls, filters: Dict[str, Any]):
        return cls(filters)
