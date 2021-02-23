from indico.types import BaseType


class SubmissionFile(BaseType):
    f"""
    A Submission File in the Indico Platform.

    Submissions files represent a single document, and can be grouped together under
    a single submission to a submission to a workflow.

    Attributes:
        id (int): the Submission file id
        filepath (str): URL of the input datafile within the Indico Platform.
        filename (str): name of the original file
        submission_id (int): the parent Submission id

    """

    id: int
    filepath: str
    filename: str
    submission_id: int
