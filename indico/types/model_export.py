import datetime

from indico.types.base import BaseType


class ModelExport(BaseType):
    """
    The returned model export object.
    """

    id: int
    name: str
    status: str
    model_id: int
    file_path: str
    created_at: datetime.datetime
    created_by: int
    signed_url: str
