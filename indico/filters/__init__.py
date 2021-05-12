import datetime
from typing import Any, Iterable, Mapping

from indico.errors import IndicoInputError


def or_(*args: Iterable[Mapping[str, Any]]):
    return {"OR": list(args)}


def and_(*args: Iterable[Mapping[str, Any]]):
    return {"AND": list(args)}


class Filter(dict):
    """
    Base filter class that allows users to construct filter statements for
    GraphQL queries. Search keys are constrained by the implementing subclasses
    If multiple arguments are supplied, they are treated as arg1 AND arg2 AND ...
    """

    __options__ = None

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if not kwargs:
            raise IndicoInputError(f"One of {self.__options__} must be specified")
        self.update(and_(kwargs) if len(kwargs) > 1 else kwargs)


class SubmissionFilter(Filter):
    """
    Create a Filter when querying for WorkflowSubmissions.

    Args:
        input_filename (str): submissions with input file names containing this string
        status (str): submissions in this status. Options:
            [PROCESSING, PENDING_REVIEW, PENDING_ADMIN_REVIEW, COMPLETE, FAILED]
        retrieved(bool): Filter submissions on the retrieved flag
    Returns:
        dict containing query filter parameters
    """

    __options__ = ("input_filename", "status", "retrieved")

    def __init__(
        self, input_filename: str = None, status: str = None, retrieved: bool = None
    ):
        kwargs = {
            "input_filename": input_filename,
            "status": status.upper() if status else status,
            "retrieved": retrieved,
        }

        super().__init__(**kwargs)


class UserMetricsFilter(Filter):
    """
    Create a Filter when querying for UserSnapshots.

    Args:
        user_id (int): username to filter on
        user_email (str): email to filter for
    Returns:
        dict containing query filter parameters
    """
    __options__ = ("user_id", "user_email")

    def __init__(self, user_id: int = None, user_email: str = None):
        kwargs = {
            "userId": user_id,
            "userEmail": user_email
        }

        super().__init__(**kwargs)
