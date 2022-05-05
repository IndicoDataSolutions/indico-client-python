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

class SubmissionReviewFilter(Filter):
    __options__ = ("rejected", "created_by", "review_type")
    
    def __init__(self, rejected: bool = None, created_by: int = None, review_type: str = None):
        kwargs = {
            "rejected": rejected,
            "createdBy": created_by,
            "reviewType": review_type.upper() if review_type else review_type,
        }

        super().__init__(**kwargs)

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
        self, 
        input_filename: str = None, 
        status: str = None, 
        retrieved: bool = None, 
        reviews: SubmissionReviewFilter = None
    ):
        kwargs = {
            "inputFilename": input_filename,
            "status": status.upper() if status else status,
            "retrieved": retrieved,
            "reviews": reviews,
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

class DocumentReportFilter(Filter):
    """
    Create a filter for the DocumentReport query.

    Args:
        workflow_id (int): workflow id
        submission_id (int): submission id
        status (str): submission status
        created_at_start_date (datetime): earliest creation date
        created_at_end_date (datetime): latest creation date
        updated_at_start_date (datetime): earliest update ddate
        updated_at_end_date (datetime): latest update date
    Returns:
        dict containing query filter parameters
    """
    __options__ = ("workflow_id", "submission_id", "status", "created_at_start_date", "created_at_end_date",
                   "updated_at_start_date", "updated_at_end_date")

    def __init__(self, submission_id: int = None, workflow_id: int = None, status: str = None, created_at_start_date: datetime = None,
                 created_at_end_date: datetime = None,
                 updated_at_start_date: datetime = None, updated_at_end_date: datetime = None
                 ):

        kwargs = {
            "workflowId": workflow_id,
            "id": submission_id,
            "status": status


        }
        if created_at_start_date is not None and created_at_end_date is not None:
            kwargs["createdAt"] = {
                "from": created_at_start_date.strftime('%Y-%m-%d') if created_at_start_date is not None else "",
                "to": created_at_end_date.strftime('%Y-%m-%d') if created_at_end_date is not None else "",
            }
        if updated_at_start_date is not None and updated_at_end_date is not None:
            kwargs["updatedAt"] = {
                "from": updated_at_start_date.strftime('%Y-%m-%d') if updated_at_start_date is not None else "",
                "to": updated_at_end_date.strftime('%Y-%m-%d') if updated_at_end_date is not None else "",
            }
        super().__init__(**kwargs)
