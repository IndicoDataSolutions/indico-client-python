from typing import List
from indico.types.base import BaseType


class Questionnaire(BaseType):
    id: int
    questions_status: str
    odl: bool
    name: str
    num_total_examples: int
    num_fully_labeled: int


class Example(BaseType):
    row_index: int
    datafile_id: int
    status: str
    source: str
    id: int


class QuestionnaireExamples(BaseType):
    examples: List[Example]
