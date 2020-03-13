from indico.types.base import BaseType
from indico.types.model import Model

class ModelGroup(BaseType):
    id: int
    status: str
    selected_model: Model
