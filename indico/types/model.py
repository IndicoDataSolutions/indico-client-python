from indico.types.base import BaseType


class TrainingProgress(BaseType):
    """
    Model training progress

    Shows percent complete for a model training

    Attributes:
        percent_complete (float): Percent complete for a model that's training
    """

    percent_complete: float


class Model(BaseType):
    """
    A Model in the Indico Platform.

    Models are a part of a Model Group

    Attributes:
        id (int): The model id. This is different from the model group id.
        status (str): "CREATED", "TRAINING", "COMPLETE" or "FAILED"
        training_progress (TrainingProgress): Percent complete training progress on a model.
    """

    id: int
    status: str
    training_progress: TrainingProgress


class ModelOptions(BaseType):
    """
    Model Options in the Indico Platform.

    Attributes:
        id (int): The model options id
        model_training_options (str): JSONString representation of the model training options specified
    """

    id: int
    model_training_options: str
