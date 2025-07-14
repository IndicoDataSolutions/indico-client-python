import datetime
from typing import TYPE_CHECKING, Dict

from indico.errors import IndicoInputError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, ClassVar, List, Optional, Tuple, Union

    from indico.typing import AnyDict


def or_(*args: "Any") -> "Dict[str, List[Any]]":
    return {"OR": list(args)}


def and_(*args: "Any") -> "Dict[str, List[Any]]":
    return {"AND": list(args)}


class Filter(Dict[str, "Any"]):
    """
    Base filter class that allows users to construct filter statements for
    GraphQL queries. Search keys are constrained by the implementing subclasses
    If multiple arguments are supplied, they are treated as arg1 AND arg2 AND ...
    """

    __options__: "ClassVar[Tuple[Any, ...]]" = tuple()

    def __init__(self, **kwargs: "Any"):
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
        rejected: "Optional[bool]" = None,
        created_by: "Optional[int]" = None,
        review_type: "Optional[str]" = None,
    ):
        kwargs = {
            "rejected": rejected,
            "createdBy": created_by,
            "reviewType": review_type.upper() if review_type else review_type,
        }

        super().__init__(**kwargs)


class DateRangeFilter(Dict[str, "Optional[str]"]):
    """
    Create a Filter when querying for Submissions within a certain date range
    Args:
        filter_from (str): A valid string representation of a datetime for start date to filter
        filter_to (str): A valid string representation of a datetime for end date to filter
    """

    def __init__(
        self, filter_from: "Optional[str]" = None, filter_to: "Optional[str]" = None
    ):
        kwargs: "Dict[str, Optional[str]]" = {"from": filter_from, "to": filter_to}
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
        file_type: "Optional[List[str]]" = None,
        input_filename: "Optional[str]" = None,
        status: "Optional[str]" = None,
        retrieved: "Optional[bool]" = None,
        reviews: "Optional[SubmissionReviewFilter]" = None,
        review_in_progress: "Optional[bool]" = None,
        files_deleted: "Optional[bool]" = None,
        created_at: "Optional[DateRangeFilter]" = None,
        updated_at: "Optional[DateRangeFilter]" = None,
    ):
        kwargs: "AnyDict" = {
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
        file_type (str): examples with this file type (e.g. "PDF")
        labeler (List[int]): examples labeled by these users
        include_class (List[int]): examples that are or are not included in this class
        exclude_class (List[int]): examples that are or are not excluded from this class
        partial (bool): examples that are or are not partially labeled
        autolabeled (bool): examples that are or are not autolabeled
        status (str): submissions in this status. Options:
            [COMPLETE, INCOMPLETE]
        text_search (bool): examples that contain this substring in their text
    Returns:
        dict containing query filter parameters
    """

    __options__ = (
        "file_name",
        "file_type",
        "labeler",
        "include_class",
        "exclude_class",
        "partial",
        "autolabeled",
        "status",
        "text_search",
    )

    def __init__(
        self,
        file_name: "Optional[str]" = None,
        file_type: "Optional[str]" = None,
        labeler: "Optional[List[int]]" = None,
        include_class: "Optional[List[int]]" = None,
        exclude_class: "Optional[List[int]]" = None,
        autolabeled: "Optional[bool]" = None,
        partial: "Optional[bool]" = None,
        status: "Optional[str]" = None,
        text_search: "Optional[str]" = None,
    ):
        kwargs: "Dict[str, Optional[Union[bool, str, List[int]]]]" = {
            "fileName": file_name,
            "fileType": file_type,
            "labeler": labeler,
            "includeClass": include_class,
            "excludeClass": exclude_class,
            "autolabeled": autolabeled,
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
        self,
        user_id: "Optional[int]" = None,
        user_email: "Optional[str]" = None,
    ):
        kwargs: "Dict[str, Optional[Union[int, str]]]" = {
            "userId": user_id,
            "userEmail": user_email,
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
        submission_id: "Optional[int]" = None,
        workflow_id: "Optional[int]" = None,
        status: "Optional[str]" = None,
        created_at_start_date: "Optional[datetime.datetime]" = None,
        created_at_end_date: "Optional[datetime.datetime]" = None,
        updated_at_start_date: "Optional[datetime.datetime]" = None,
        updated_at_end_date: "Optional[datetime.datetime]" = None,
    ):
        kwargs: "AnyDict" = {
            "workflowId": workflow_id,
            "id": submission_id,
            "status": status,
        }
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
        name: "Optional[str]" = None,
        component_type: "Optional[str]" = None,
        component_family: "Optional[str]" = None,
        tags: "Optional[List[str]]" = None,
    ):
        kwargs = {
            "name": name,
            "componentType": component_type,
            "componentFamily": component_family,
            "tags": tags,
        }
        super().__init__(**kwargs)
