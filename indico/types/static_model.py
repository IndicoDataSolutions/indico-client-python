from typing import Any

from indico.types.base import BaseType


class StaticModelMeta(BaseType):
    """
    Static model metadata.

    This is the data that is extracted from the static model metadata.json file that is required to create a static model.
    """

    task_type: str
    model_type: str
    data_type: str
    model_file_path: str
    model_options: dict | None = None
    fields: list[dict[str, Any]]
    source_host: str
    source_ipa_version: str


class StaticModelConfig(BaseType):
    export_meta: StaticModelMeta
