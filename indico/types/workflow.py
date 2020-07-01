from indico.types import BaseType

class Workflow(BaseType):
    id: int
    name: str
    review_enabled: bool
