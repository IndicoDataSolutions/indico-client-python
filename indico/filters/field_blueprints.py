from typing import TYPE_CHECKING

from indico.filters.base import FilterV2

if TYPE_CHECKING:
    from typing import List, Optional, Union


class FieldBlueprintFilter(FilterV2):
    """
    Filter for querying Field Blueprints.

    Args:
        uid (str): Filter by unique identifier
        name (str): Filter by name
        id (int): Filter by ID
        task_type (str): Filter by task type
        enabled (bool): Filter by enabled status
        tags (str | List[str]): Filter by tags
    """

    __options__ = ("uid", "name", "id", "taskType", "enabled", "tags")

    def __init__(
        self,
        uid: "Optional[str]" = None,
        name: "Optional[str]" = None,
        id: "Optional[int]" = None,
        task_type: "Optional[str]" = None,
        enabled: "Optional[bool]" = None,
        tags: "Optional[Union[str, List[str]]]" = None,
    ):
        kwargs = {
            "uid": uid,
            "name": name,
            "id": id,
            "taskType": task_type,
            "enabled": enabled,
            "tags": tags,
        }
        # Filter out None values before passing to super (handled in super, but cleaner to map first)
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(data=None, **clean_kwargs)
