import datetime
from typing import Optional

from indico.types.base import BaseType


class ModelExport(BaseType):
    """
    The returned model export object.

    `signed_url` is deprecated and always None; use `download_url` or `DownloadModelExport`.
    """

    id: int
    name: str
    status: str
    model_id: int
    file_path: str
    created_at: datetime.datetime
    created_by: int
    signed_url: Optional[str] = None
    download_url: str


class ExportUpload(BaseType):
    """
    Where to upload a static model export and the storage uri it will have.
    """

    upload_url: str
    storage_uri: str
