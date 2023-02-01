from indico.types import BaseType, List
from . import SubmissionFile

VALID_SUBMISSION_STATUSES = [
    "COMPLETE",
    "FAILED",
    "PENDING_REVIEW",
    "PROCESSING",
    "PENDING_ADMIN_REVIEW",
    "PENDING_AUTO_REVIEW",
    "POST_PROCRESSING"
]

VALID_REVIEW_TYPES = [
    "MANUAL",
    "AUTO",
    "ADMIN",
]

SUBMISSION_RESULT_VERSIONS = ["ONE", "TWO", "THREE", "OLDEST_SUPPORTED", "LATEST"]


class SubmissionRetries(BaseType):
    """
    Information about a retried submission.

    Attributes:
        id (int): The id of the retry attempt.
        previous_errors (str): Errors from the previous attempt.
        previous_status (str): The status from the previous attempt.
        retry_errors (str): Errors encountered on this retry.
        submission_id (int): The ID of the submission being retried.
    """
    id: int
    previous_errors: str
    previous_status: str
    retry_errors: str
    submission_id: int


class SubmissionReviews(BaseType):
    f"""
    Information about a submission's Reviews.

    Attributes:
        id (int): The ID of the review.
        submission_id (int): The ID of the submission that is being reviewed.
        created_at (str): Timestamp of when the document was checked out
        created_by (int): The ID of the User who submitted the review.
        completed_at (str): Timestamp of when the review was submitted.
        rejected (bool): Whether a submission has been rejected.
        review_type (str): Type of review. One of {VALID_REVIEW_TYPES}
        notes (str): Rejection reasons provided by user.
    """
    id: int
    submission_id: int
    created_at: str
    created_by: int
    completed_at: str
    rejected: bool
    review_type: str
    notes: str

class Submission(BaseType):
    f"""
    A Submission in the Indico Platform.

    Submissions represent a single input which has been sent for processing by a
    specific workflow. A submission consists of SubmissionFiles, generally a PDF.
    Processing broadly consists of an input processor, a series of processors and
    components associated with particular docbots, and finally an output processor
    to generate the result file.

    Attributes:
        id (int): the Submission id
        dataset_id (int): the Dataset id
        workflow_id (int): the Workflow id
        status (str): status of the submission. One of
            {VALID_SUBMISSION_STATUSES}
        input_files (list[SubmissionFile]): the SubmissionFiles for the Submission
        input_file (str): URL of the first input datafile within the Indico Platform.
        input_filename (str): name of the first original file
        result_file (str): URL of the result datafile within the Indico Platform
        retrieved (bool): Whether the submission has been retrieved by a user
            This flag is set manually by users.
        deleted (bool): Whether the submission result has been deleted from the server
        errors (str): Any errors raised while processing the submission
        retries (List[SubmissionRetries]): If requested, information about previous retries of this submission.
    """

    id: int
    dataset_id: int
    workflow_id: int
    status: str
    input_files: List[SubmissionFile]
    input_file: str
    input_filename: str
    result_file: str
    retrieved: bool
    deleted: bool
    errors: str
    retries: List[SubmissionRetries]
    reviews: List[SubmissionReviews]
