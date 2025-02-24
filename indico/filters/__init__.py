import datetime
from typing import Any, Iterable, List, Mapping, Union

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


class DatasetFilter(Filter):
    """
    Create a Filter when querying for Datasets via datasetsPage.

    Args:
        name (str): dataset name by which to filter
    Returns:
        dict containing query filter parameters
    """

    __options__ = ("name",)

    def __init__(self, name: str):
        super().__init__(name=name)


class SubmissionReviewFilter(Filter):
    __options__ = ("rejected", "created_by", "review_type")

    def __init__(
        self,
        rejected: Union[bool, None] = None,
        created_by: Union[int, None] = None,
        review_type: Union[str, None] = None,
    ):
        kwargs = {
            "rejected": rejected,
            "createdBy": created_by,
            "reviewType": review_type.upper() if review_type else review_type,
        }

        super().__init__(**kwargs)


class DateRangeFilter(dict):
    """
    Create a Filter when querying for Submissions within a certain date range
    Args:
        filter_from (str): A valid string representation of a datetime for start date to filter
        filter_to (str): A valid string representation of a datetime for end date to filter
    """

    def __init__(
        self, filter_from: Union[str, None] = None, filter_to: Union[str, None] = None
    ):
        kwargs = {"from": filter_from, "to": filter_to}
        self.update(kwargs)


class SubmissionFilter(Filter):
    """
    Create a Filter when querying for WorkflowSubmissions.

    Args:
        file_type (list): submissions with a file type in this list. Options:
            [CSV, PDF, EXCEL, DOC, DOCX, PPT, PPTX, PNG, JPG, TIFF, TXT, RTF, XLS, XLSX, UNKNOWN, MSG, EML]
        input_filename (str): submissions with input file names containing this string
        status (str): submissions in this status. Options:
            [PROCESSING, PENDING_REVIEW, PENDING_ADMIN_REVIEW, COMPLETE, FAILED]
        retrieved (bool): submissions that have been retrieved (True) or not (False)
        reviews (SubmissionReviewFilter): submissions whose completed reviews match this review filter
        review_in_progress (bool): submissions where a review is in progress (True) or not (False)
        files_deleted (bool): submissions that have had their internal files removed (True) or not (False)
        created_at (DateRangeFilter): submissions created during given time range
        updated_at (DateRangeFilter): submissions updated during given time range
    Returns:
        dict containing query filter parameters
    """

    __options__ = (
        "file_type",
        "input_filename",
        "status",
        "retrieved",
        "reviews",
        "review_in_progress",
        "files_deleted",
        "created_at",
        "updated_at",
    )

    def __init__(
        self,
        file_type: Union[List[str], None] = None,
        input_filename: Union[str, None] = None,
        status: Union[str, None] = None,
        retrieved: Union[bool, None] = None,
        reviews: Union[SubmissionReviewFilter, None] = None,
        review_in_progress: Union[bool, None] = None,
        files_deleted: Union[bool, None] = None,
        created_at: Union[DateRangeFilter, None] = None,
        updated_at: Union[DateRangeFilter, None] = None,
    ):
        kwargs = {
            "filetype": file_type,
            "inputFilename": input_filename,
            "status": status.upper() if status else status,
            "retrieved": retrieved,
            "reviews": reviews,
            "reviewInProgress": review_in_progress,
            "filesDeleted": files_deleted,
            "createdAt": created_at,
            "updatedAt": updated_at,
        }

        super().__init__(**kwargs)


class ModelGroupExampleFilter(Filter):
    """
    Create a Filter when querying for examples associated with model groups.

    Args:
        file_name (str): examples with input file names containing this string
        partial (bool): examples that are or are not partially labeled
        status (str): submissions in this status. Options:
            [COMPLETE, INCOMPLETE]
        text_search (bool): examples that contain this substring in their text
    Returns:
        dict containing query filter parameters
    """

    # TODO: extend to support full filter list
    __options__ = ("file_name", "partial", "status", "text_search")

    def __init__(
        self,
        file_name: Union[str, None] = None,
        partial: Union[bool, None] = None,
        status: Union[str, None] = None,
        text_search: Union[str, None] = None,
    ):
        kwargs = {
            "fileName": file_name,
            "partial": partial,
            "textSearch": text_search,
        }
        kwargs["status"] = status.upper() if status else None

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

    def __init__(
        self, user_id: Union[int, None] = None, user_email: Union[str, None] = None
    ):
        kwargs = {"userId": user_id, "userEmail": user_email}

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
        updated_at_start_date (datetime): earliest update date
        updated_at_end_date (datetime): latest update date
    Returns:
        dict containing query filter parameters
    """

    __options__ = (
        "workflow_id",
        "submission_id",
        "status",
        "created_at_start_date",
        "created_at_end_date",
        "updated_at_start_date",
        "updated_at_end_date",
    )

    def __init__(
        self,
        submission_id: Union[int, None] = None,
        workflow_id: Union[int, None] = None,
        status: Union[str, None] = None,
        created_at_start_date: Union[datetime.datetime, None] = None,
        created_at_end_date: Union[datetime.datetime, None] = None,
        updated_at_start_date: Union[datetime.datetime, None] = None,
        updated_at_end_date: Union[datetime.datetime, None] = None,
    ):
        kwargs = {"workflowId": workflow_id, "id": submission_id, "status": status}
        if created_at_end_date and not created_at_start_date:
            raise IndicoInputError("Must specify created_at_start_date")
        if created_at_start_date:
            kwargs["createdAt"] = {
                "from": created_at_start_date.strftime("%Y-%m-%d"),
                "to": (
                    created_at_end_date.strftime("%Y-%m-%d")
                    if created_at_end_date is not None
                    else datetime.datetime.now().strftime("%Y-%m-%d")
                ),
            }

        if updated_at_end_date and not updated_at_start_date:
            raise IndicoInputError("Must specify updated_at_start_date")
        if updated_at_start_date is not None:
            kwargs["updatedAt"] = {
                "from": updated_at_start_date.strftime("%Y-%m-%d"),
                "to": (
                    updated_at_end_date.strftime("%Y-%m-%d")
                    if updated_at_end_date is not None
                    else datetime.datetime.now().strftime("%Y-%m-%d")
                ),
            }
        super().__init__(**kwargs)


class ComponentBlueprintFilter(Filter):
    """
    Create a Filter when querying for ComponentBlueprints.

    Args:
        name (str): name of the component blueprint
        component_type (str): type of the component blueprint
        component_family (str): family of the component blueprint
        tags (list): tags of the component blueprint
    """

    __options__ = (
        "name",
        "component_type",
        "component_family",
        "tags",
    )

    def __init__(
        self,
        name: Union[str, None] = None,
        component_type: Union[str, None] = None,
        component_family: Union[str, None] = None,
        tags: Union[List[str], None] = None,
    ):
        kwargs = {
            "name": name,
            "componentType": component_type,
            "componentFamily": component_family,
            "tags": tags,
        }
        super().__init__(**kwargs)
