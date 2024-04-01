import datetime
from typing import Optional

from indico.types import BaseType, List

from . import OutputFile, SubmissionFile

VALID_SUBMISSION_STATUSES = [
    "COMPLETE",
    "FAILED",
    "PENDING_REVIEW",
    "PROCESSING",
    "PENDING_ADMIN_REVIEW",
    "PENDING_AUTO_REVIEW",
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


class SubmissionReview(BaseType):
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

class SubmissionReviewFull(BaseType):
    f"""
    Information about a submission's Reviews. Includes changes

    Attributes:
        id (int): The ID of the review.
        submission_id (int): The ID of the submission that is being reviewed.
        created_at (str): Timestamp of when the document was checked out
        created_by (int): The ID of the User who submitted the review.
        completed_at (str): Timestamp of when the review was submitted.
        rejected (bool): Whether a submission has been rejected.
        review_type (str): Type of review. One of {VALID_REVIEW_TYPES}
        notes (str): Rejection reasons provided by user.
        changes (dict): Changes for this review.
    """
    id: int
    submission_id: int
    created_at: str
    created_by: int
    completed_at: str
    rejected: bool
    review_type: str
    notes: str
    changes: dict


class Submission(BaseType):
    f"""
    A Submission in the Indico Platform.

    Submissions represent a single input which has been sent for processing by a
    specific workflow. A submission consists of SubmissionFiles, generally a PDF.
    Processing broadly consists of an input processor, a series of processors and
    components associated with particular docbots, and finally an output processor
    to generate the result file.

    Attributes:
        id (int): The Submission id
        dataset_id (int): The Dataset id
        workflow_id (int): The Workflow id
        status (str): status of the submission. One of
            {VALID_SUBMISSION_STATUSES}
        created_at (datetime): Datetime the submission was created
        updated_at (datetime): Datetime the submission was updated
        created_by (int): Id of the user who created the submission
        updated_by (int): Id of the user who updated the submission
        completed_at (datetime): Datetime the submission reached a completed state
        files_deleted (bool): Submission files have been deleted (True) or not deleted (False) from file store
        input_files (List[SubmissionFile]): The SubmissionFiles for the Submission
        input_file (str): URL of the first input datafile within the Indico Platform.
        input_filename (str): Name of the first original file
        result_file (str): URL of the latest result file for this submission
        output_files (List[OutputFile]): List of output files from submission
        retrieved (bool): Whether the submission has been retrieved by a user
            This flag is set manually by users.
        auto_review (SubmissionReview): Latest auto review for submission
        errors (str): Any errors raised while processing the submission
        retries (List[SubmissionRetries]): If requested, information about previous retries of this submission.
        reviews (List[SubmissionReview]): Completed reviews of this submission, without changes
        review_in_progress (bool): True if the submission is being actively reviewed
    """

    id: int
    dataset_id: int
    workflow_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    completed_at: datetime
    files_deleted: bool
    input_files: List[SubmissionFile]
    input_file: str
    input_filename: str
    result_file: str
    output_files: List[OutputFile]
    retrieved: bool
    auto_review: SubmissionReview
    errors: str
    retries: List[SubmissionRetries]
    reviews: List[SubmissionReview]
    review_in_progress: bool
