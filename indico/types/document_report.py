from typing import List

from indico.types import BaseType


class InputFile(BaseType):
    filename: str
    submission_id: int
    num_pages: int
    file_size: int


class DocumentReport(BaseType):
    """
    A Document report about the associated InputFiles.


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
    input_files: List[InputFile]
    deleted: bool

