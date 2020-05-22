from typing import List
from indico.types.base import BaseType


class Questionnaire(BaseType):
    id: int

class Example(BaseType):
    row_index: int
    datafile_id: int
    source: str

class QuestionnaireExamples(BaseType):
    examples: List[Example]