from typing import List

from indico.types.base import BaseType


class Export(BaseType):
    """
    An export of a dataset.

    Attributes:
        id (int): Id of the export
        dataset_id (int): Dataset id of the export
        status (str): Export job status
        column_ids (List(int)): Data columns for export
        labelset_ids (List(int)): Labelsets columns for export
        subset_ids (List(int)): Subsets requested for export rows
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
    labelset_ids: List[int]
    subset_ids: List[int]
    num_labels: int
    anonymous: bool
    download_url: str
    created_at: str
