from typing import List

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
    id: int
    datafile_id: int
    source: str


class Example(BaseType):
    datafile_ids: List[int]
    original_datafile_id: int
    original_datafile_name: str
    contexts: List[ExampleContext]
    status: str
    id: int


class QuestionnaireExamples(BaseType):
    examples: List[Example]
