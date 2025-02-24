from typing import Any, Dict

from indico.types import BaseType


class SubmissionFile(BaseType):
    """
    A Submission File in the Indico Platform.

    Submissions files represent a single document, and can be grouped together under
    a single submission to a submission to a workflow.

    Attributes:
        id (int): The Submission file id
        submission_id (int): The parent Submission id
        filename (str): Name of the original file
        filepath (str): URL of the input datafile within the Indico Platform.
        filetype (str): The file type of the original file; most likely, this is "PDF".
        file_size (int): Size of file, in bytes
        num_pages (int): Number of pages in file
    """

    id: int
    submission_id: int
    filename: str
    filepath: str
    filetype: str
    file_size: int
    num_pages: int
    meta: Dict[str, Any]
