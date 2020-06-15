from indico.types import BaseType


class Submission(BaseType):
    """
    A Submission in the Indico Platform.

    Submissions represent a single input which has been sent for processing by a specific workflow. 
    The input file is generally a PDF, and the processing broadly consists of an input processor, a
    series of processors and components associated with particular docbots, and finally an output processor
    to generate the result file.

    Attributes:
        id (int): the Submission id
        dataset_id (int): the Dataset id
        workflow_id (int): the Workflow id
        status (str): status of the submission
        input_file (str): URL of the input datafile within the Indico Platform. 
        input_filename (str): name of the original file
        result_file (str): URL of the result datafile within the Indico Platform
 
    """

    id: int
    dataset_id: int
    workflow_id: int
    status: str
    input_file: str
    input_filename: str
    result_file: str
