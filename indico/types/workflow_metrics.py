from enum import Enum
from datetime import date, datetime
from indico.types.base import BaseType
from typing import List


class WorkflowMetricsOptions(Enum):
    ITEMS_SUBMITTED = 1
    ITEMS_THROUGH_REVIEW = 2


class SubmissionFact(BaseType):
    count: int
    date: str


class DailyCount(BaseType):
    date: str
    count: int


class DailyAvg(BaseType):
    date: str
    avg: float


class DailyTimeOnTask(BaseType):
    date: str
    minutes: float
    numReviews: int


class TimeOnTaskDaily(BaseType):
    review: List[DailyTimeOnTask]
    exceptions: List[DailyTimeOnTask]


class StpDaily(BaseType):
    pass


class SubmissionFactsDaily(BaseType):
    submitted: List[DailyCount]
    submitted_and_completed_in_review: List[DailyCount]
    completed: List[DailyCount]
    completed_in_review: List[DailyCount]
    completed_review_queue: List[DailyCount]
    completed_exception_queue: List[DailyCount]
    rejected_in_review: List[DailyCount]


class SubmissionFacts(BaseType):
    daily: SubmissionFactsDaily
    start_date: str


class WorkflowMetric(BaseType):
    submission_facts: SubmissionFacts
    id: int


class WorkflowMetrics(BaseType):
    workflows: List[WorkflowMetric]
