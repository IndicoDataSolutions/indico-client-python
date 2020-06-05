from indico.types import BaseType


class Submission(BaseType):
    """
    A Submission in the Indico Platform

    Attributes:
        id (int): the Submission id
        dataset_id (int): the Dataset id
        workflow_id (int): the Workflow id
        status (str): status of the submission
        input_file (str): local url to stored input
        input_filename (str): name of the original file
        result_file (str): local url to the stored output
    """

    id: int
    dataset_id: int
    workflow_id: int
    status: str
    input_file: str
    input_filename: str
    result_file: str
