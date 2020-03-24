from indico.types.base import BaseType
from indico.types.model import Model

class ModelGroup(BaseType):
    id: int
    name: str
    status: str
    selected_model: Model
