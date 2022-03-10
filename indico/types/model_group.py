from enum import Enum
from typing import List

from indico.types.base import BaseType
from indico.types.model import Model


class TargetName(BaseType):
    id: int
    name: str


class LabelSet(BaseType):
    id: int
    target_names: List[TargetName]


class ModelGroup(BaseType):
    """
    A Model Group in the Indico Platform.

    Think of Model Groups as a container for individual models that are trained each
    time you click the Retrain button in Review or label more data in Teach. One of these
    models will be the current, "selected" model. It's usually the latest model but can also
    be the best performing.

    Attributes:
        id (int): The model group id
        name (str): The name of the model group
        status (str): "CREATED", "TRAINING", "COMPLETE" or "FAILED"
        selected model (Model): A Model object representing the selected (active) model.
        task_type (str): Type of machine learning task the model solves
    """

    id: int
    name: str
    status: str
    selected_model: Model
    task_type: str
    questionnaire_id: int
    labelset_column_id: int = None
    labelset: LabelSet


class ModelTaskType(Enum):
    """A list of valid task types for a model group."""

    CLASSIFICATION = 1
    FORM_EXTRACTION = 2
    OBJECT_DETECTION = 3


class ModelType(Enum):
    STANDARD = 1
    FINETUNE = 2
    OBJECT_DETECTION = 3
    FORM_EXTRACTION = 4
    DOCUMENT = 5
    TFIDF_LR = 6
    TFIDF_GBT = 7


class NewQuestionnaireArguments(BaseType):
    """instructions: String
Questionnaire instructions

forceTextMode: Boolean = false
Always use Text Labeling UI

showPredictions: Boolean = true
Show predictions at the global level

users: [Int]
User IDs to add to the questionnaire"""

    instructions: str
    force_text_mode: bool = False
    show_predictions: bool = True
    users: List[int]


class NewLabelsetArguments(BaseType):
    name: str
    num_labelers_required: int = 1
    datacolumn_id: int
    task_type: str  # This should be an enum maybe?
    target_names: List[str]

    def to_json(self):
        return {
            "name": self.name,
            "numLabelersRequired": self.num_labelers_required,
            "datacolumnId": self.datacolumn_id,
            "taskType": self.task_type,
            "targetNames": self.target_names,
        }
