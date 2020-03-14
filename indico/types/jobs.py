from indico.types.base import BaseType

class Job(BaseType):
    id: int
    status: str
    result: dict
    ready: bool

    def __init__(self, **kwargs):
        if "jobId" in kwargs:
            kwargs["id"] = kwargs["jobId"]
            del kwargs["jobId"]
        super().__init__(**kwargs)