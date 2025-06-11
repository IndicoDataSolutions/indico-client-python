from typing import List, Optional

from indico.types.base import BaseType


class TargetName(BaseType):
    id: int
    name: str


class LabelSet(BaseType):
    target_names: List[TargetName]


class Question(BaseType):
    labelset: LabelSet


class Questionnaire(BaseType):
    id: int
    questions_status: str
    odl: bool
    name: str
    num_total_examples: int
    num_fully_labeled: int
    question: Question


class ExampleContext(BaseType):
    """
    The portion of the source file that this example will cover
    """
    id: int
    source: Optional[str]
    datafile_id: Optional[int]
    spans: Optional[List[dict]]
    bounds: Optional[List[dict]]


class Example(BaseType):
    row_index: int
    # Deprecated fields - use the plural versions instead
    datarow_id: Optional[int]
    datafile_id: Optional[int]
    datapoint_id: Optional[int]
    # New plural fields
    datarow_ids: Optional[List[int]]
    datafile_ids: Optional[List[int]]
    datapoint_ids: Optional[List[int]]
    source_file_id: Optional[int]
    status: str
    source: str
    id: int
    partial: Optional[bool]
    autolabeled: Optional[bool]
    original_datafile_id: Optional[int]
    original_datafile_name: Optional[str]
    # Return one context for backwards compatibility
    context: Optional[ExampleContext]
    contexts: Optional[List[ExampleContext]]


class QuestionnaireExamples(BaseType):
    examples: List[Example]
