from indico.types import BaseType


class SubmissionFile(BaseType):
    """
    A Submission File in the Indico Platform.

    Submissions files represent a single document, and can be grouped together under
    a single submission to a submission to a workflow.

    Attributes:
        id (int): The Submission file id
        filepath (str): URL of the input datafile within the Indico Platform.
        filename (str): Name of the original file
        submission_id (int): The parent Submission id
        file_size (int): Size of file, in bytes
        num_pages (int): Number of pages in file
    """

    id: int
    filepath: str
    filename: str
    submission_id: int
    file_size: int
    num_pages: int
