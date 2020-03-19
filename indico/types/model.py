from indico.types.base import BaseType

class TrainingProgress(BaseType):
    percent_complete: float

class Model(BaseType):
    id: int
    status: str
    training_progress: TrainingProgress

