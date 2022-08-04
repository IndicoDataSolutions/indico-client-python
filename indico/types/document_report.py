from typing import List

from indico.types import BaseType
from indico.types import SubmissionFile


class DocumentReport(BaseType):
    """
    A Document report about the associated input files.


    """
    dataset_id: int
    workflow_id: int
    submission_id: int
    status: str
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str
    completed_at: str
    errors: str
    retrieved: bool
    input_files: List[SubmissionFile]
    deleted: bool

