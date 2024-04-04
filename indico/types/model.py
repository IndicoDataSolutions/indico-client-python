import json
from typing import Any, Dict, Optional

from indico.types.base import BaseType, JSONType


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
        domain (str): feature domain
        high_quality (bool): flag denoting if high quality was specified
        interlabeler_resolution (str): label resolution strategy specified
        sampling_strategy (str): sampling strategy specified
        seed (int): number of seed specified
        test_split (float): denotes specified test split
        weight_by_class_frequency (bool): flag denoting weight by class frequency
        word_predictor_strength (str): word predictor strength specified
        predict_options (dict): JSONString representation of the predict options specified
        model_training_options (dict): JSONString representation of the model training options specified
    """

    id: int
    domain: str
    high_quality: bool
    interlabeler_resolution: str
    sampling_strategy: str
    seed: int
    test_split: float
    weight_by_class_frequency: bool
    word_predictor_strength: str
    predict_options: JSONType
    model_training_options: JSONType
