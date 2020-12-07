from indico.types import BaseType

class Workflow(BaseType):
    id: int
    name: str
    review_enabled: bool
    auto_review_enabled: bool
