import json
from typing import Any
from indico.types.base import BaseType, JSONType

class Job(BaseType):
    id: int
    status: str
    result: JSONType
    ready: bool

    def __init__(self, **kwargs):
        if "jobId" in kwargs:
            kwargs["id"] = kwargs["jobId"]
            del kwargs["jobId"]
        super().__init__(**kwargs)
