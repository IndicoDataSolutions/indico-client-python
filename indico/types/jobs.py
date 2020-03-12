from indico.types.base import BaseType

class Job(BaseType):
    id: int
    status: str
    result: dict
    ready: bool