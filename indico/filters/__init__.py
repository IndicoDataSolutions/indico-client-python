from enum import Enum
from typing import Any, Dict, Iterable


class FilterMode(Enum):
    AND = "and"
    OR = "or"


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

    def __init__(self, mapping: Dict[str, Any], mode: FilterMode = FilterMode.AND):
        self._validate_keys(mapping.keys())
        filters = [{key: val} for key, val in mapping.items()]
        self.update({mode.name: filters})

    def _validate_keys(self, keys):
        if not all(key in self._filterable_columns for key in keys):
            raise ValueError(
                f"Can only filter on {self._filterable_columns}, not {keys}"
            )

    def _update(self, key: str, value: Any, mode: FilterMode):
        self._validate_keys([key])
        existing_filters = self.pop(mode.name) if mode.name in self else None
        filters = (
            [*existing_filters, {key: value}] if existing_filters else [{key: value}]
        )
        self.update({mode.name: filters})

    def and_(self, key, value):
        return self._update(key, value, FilterMode.AND)

    def or_(self, key, value):
        return self._update(key, value, FilterMode.OR)

    @property
    def filterable_columns(self):
        return self._filterable_columns


class SubmissionFilter(BaseFilter):
    _filterable_columns = {"inputFilename", "status"}
