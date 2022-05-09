from typing import List
from enum import Enum

from indico.types.base import BaseType


class LabelResolutionStrategy(Enum):
    MAJORITY_VOTE_WITH_TIES = "majority_vote_with_ties"
    MAJORITY_VOTE_WITHOUT_TIES = "majority_vote_without_ties"
    UNANIMOUS = "unanimous"
    ALL = "all"


class Export(BaseType):
    """
    An export of a dataset.

    Attributes:
        id (int): Id of the export
        dataset_id (int): Dataset id of the export
        name (str): Name of the export
        status (ExportStatus): Export job status
        column_ids (List(int)): Data columns for export
        labelset_id (int): Labelset column for export
        model_ids (List(int)): Models to include predictions from
        frozen_labelset_ids (List(int)): Frozen labelsets to select examples
        num_labels (int): Number of labels on the dataset
        anonymous (bool): Whether to anonymize labelers
        download_url (str): Indico url of the export csv
        created_at (str): Unix timestamp for when the export was created
    """

    id: int
    dataset_id: int
    name: str
    status: str
    column_ids: List[int]
    labelset_id: int
    model_ids: List[int]
    frozen_labelset_ids: List[int]
    num_labels: int
    anonymous: bool
    download_url: str
    created_at: str
