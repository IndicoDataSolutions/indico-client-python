from typing import List
from indico.types.base import BaseType


class Questionnaire(BaseType):
    id: int
    questions_status: str
    odl: bool
    name: str
    num_total_examples: int
    num_fully_labeled: int


class Span(BaseType):
    start: int
    end: int
    page_num: int
    value: str


class Context(BaseType):
    id: int
    spans: List[Span]


class Example(BaseType):
    id: int
    row_index: int
    datafile_id: int
    source: str
    context: Context


class QuestionnaireExamples(BaseType):
    examples: List[Example]
