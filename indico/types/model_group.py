from enum import Enum
from typing import Any, Dict, Iterator, List, Mapping

from indico.types.base import BaseType
from indico.types.model import Model


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
    class_names: List[str]


class ModelTaskType(Enum):
    """A list of valid task types for a model group."""

    CLASSIFICATION = 1
    FORM_EXTRACTION = 2
    OBJECT_DETECTION = 3
    CLASSIFICATION_MULTIPLE = 4
    REGRESSION = 5
    ANNOTATION = 6
    CLASSIFICATION_UNBUNDLING = 7


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


class ValidationActionType(Enum):
    """Determines how validation failures are handled."""

    NO_ACTION = "NO_ACTION"
    WARN = "WARN"
    ERROR = "ERROR"
    REJECT = "REJECT"


class _ValidationConfig:
    """Base configuration for validation rules."""

    setting_name: str
    setting_value: dict[str, Any]
    on_failure: ValidationActionType


class ValidationInputConfig(_ValidationConfig, BaseType, Mapping[str, Any]):
    """Configuration that controls which additional validation checks should be run and what actions should be taken in case of their failure."""

    def to_json(self):
        """
        Convert to JSON serializable format

        Returns:
            dict: JSON-ready python dictionary
        """
        return {
            "settingName": self.setting_name,
            "settingValue": self.setting_value,
            "onFailure": (
                self.on_failure.value
                if isinstance(self.on_failure, ValidationActionType)
                else self.on_failure
            ),
        }

    # Implement Mapping interface so instances can be expanded with ** in BaseType
    def __iter__(self) -> Iterator[str]:
        return iter(self.to_json())

    def __len__(self) -> int:
        return len(self.to_json())

    def __getitem__(self, key):
        return self.to_json()[key]


class _FieldInput:
    """
    Basic inputs for a new field
    """

    required: bool
    multiple: bool
    datatype: str
    input_config: Dict[str, Any]
    format_config: Dict[str, Any]
    validation_config: List[ValidationInputConfig]


class FieldInput(_FieldInput, BaseType):
    """Field input with name for review UI and workflow result file"""

    name: str

    def to_json(self):
        return {
            "name": self.name,
            "required": self.required,
            "multiple": self.multiple,
            "datatype": self.datatype,
            "inputConfig": self.input_config,
            "formatConfig": self.format_config,
            "validationConfig": [vc.to_json() for vc in self.validation_config]
            if self.validation_config
            else [],
        }


class NewLabelsetArguments:
    def __init__(
        self,
        name: str,
        task_type: ModelTaskType,
        target_names: List[str],
        datacolumn_id: int,
        field_data: List[FieldInput],
        num_labelers_required: int = 1,
    ):
        self.name = name
        self.num_labelers_required = num_labelers_required
        self.task_type = task_type
        self.target_names = target_names
        self.datacolumn_id = datacolumn_id
        self.field_data = [f.to_json() for f in field_data]
