import datetime

from indico.types import BaseType


class OutputFile(BaseType):
    """
    An Output File in the Indico Platform.

    Attributes:
        id (int): The Output file id
        filepath (str): URL of the output datafile within the Indico Platform.
        submission_id (int): The parent Submission id
        component_id (int): The id of the corresponding component the output is linked to
        created_at (datetime): The date the output file was created
    """

    id: int
    filepath: str
    submission_id: int
    component_id: int
    created_at: datetime
