from enum import Enum
from indico.types.base import BaseType
from typing import List


class WorkflowMetricsOptions(Enum):
    """
    Options for pulling back specific metrics.

    Attributes:
        SUBMISSIONS: Generates SubmissionMetrics in the response.
        REIVEW: Generates review Queue metrics in the response.
        STRAIGHT_THROUGH_PROCESSING: Generates StraightThroughProcessing metrics in the response.
        TIME_ON_TASK: Average time spent by reviewers on documents.
    """
    SUBMISSIONS = 1
    REVIEW = 2
    STRAIGHT_THROUGH_PROCESSING = 3
    TIME_ON_TASK = 4


class TimeOnTaskMetric(BaseType):
    """
    Time on task metrics.

    Attributes:
        avg_mins_per_doc(float): Average amount of minutes reviewers spend on documents in this workflow
            across review and exceptions queue.
        avg_mins_per_doc_review(float): Average amount of minutes reviewers spend on documents in this workflow
            in the review queue.
        avg_min_per_doc_exceptions(float): Average amount of minutes reviewers spend on ducments for this workflow in
            the exceptions queue.
    """
    avg_mins_per_doc: float
    avg_mins_per_doc_review: float
    avg_min_per_doc_exceptions: float


class DailyTimeOnTaskMetric(TimeOnTaskMetric):
    """
    Daily time on task metrics.
    
    Attributes:
        avg_mins_per_doc(float): Average amount of minutes reviewers spend on documents in this workflow
            across review and exceptions queue.
        avg_mins_per_doc_review(float): Average amount of minutes reviewers spend on documents in this workflow
            in the review queue.
        avg_min_per_doc_exceptions(float): Average amount of minutes reviewers spend on ducments for this workflow in
            the exceptions queue.
        date(str): Date.
    """
    date: str


class TimeOnTaskMetrics(BaseType):
    """
    Time on task metrics.

    Attributes:
        aggregate(TimeOnTaskMetric): Aggregate level time on task metrics.
        daily(List[DailyTimeOnTaskMetric): Daily level time on task metrics.
    """
    aggregate: TimeOnTaskMetric
    daily: List[DailyTimeOnTaskMetric]


class SubmissionMetric(BaseType):
    """
    Submission metric.

     Attributes:
        submitted(int): Number of items submitted to this workflow on this day.
        completed(int): Number of items completed in this workflow on this day.
        completed_in_review(int): Number of items accepted in the review or the exceptions queue.
        completed_review_queue(int): Number of items accepted in the review queue.
        completed_exception_queue(int): Number of items accepted in the exceptions queue.
        rejected_in_review(int): Number of items rejected in the exceptions queue.
        date(str): Date.
    """
    submitted: int
    completed: int
    completed_in_review: int
    completed_review_queue: int
    completed_exception_queue: int
    rejected_in_review: int


class DailySubmissionMetric(SubmissionMetric):
    """
    Daily submission metrics.

    Attributes:
        submitted(int): Number of items submitted to this workflow on this day.
        completed(int): Number of items completed in this workflow on this day.
        completed_in_review(int): Number of items accepted in the review or the exceptions queue.
        completed_review_queue(int): Number of items accepted in the review queue.
        completed_exception_queue(int): Number of items accepted in the exceptions queue.
        rejected_in_review(int): Number of items rejected in the exceptions queue.
        date(str): Date.
    """
    date: str


class SubmissionMetrics(BaseType):
    """
    Submission metrics.

    Attributes:
        aggregate(SubmissionMetric): Aggregate level submission metrics.
        daily(List[SubmissionMetric]): Daily submission metrics.
    """
    aggregate: SubmissionMetric
    daily: List[DailySubmissionMetric]


class DailyQueueMetric(BaseType):
    """
    Daily cumulative metrics for queues
    Attributes:
        date (str): the date.
        subs_on_queue(int): Number of submissions queued for review
        hours_on_queue(float): Cumulative hours items wait on queue for review.
        avg_age_in_queue(float): Average cumulative age of items waiting in review queues.
    """
    date: str
    subs_on_queue: int
    hours_on_queue: float
    avg_age_in_queue: float


class QueueMetrics(BaseType):
    """
    Daily cumulative metrics for queues.
    Attributes:
        daily_cumulative(List[DailyQueueMetric]): list of cumulative queue metrics per day
    """
    daily_cumulative: List[DailyQueueMetric]


class PredictionMetric(BaseType):
    """
    The total number of model-generated predictions for specified workflow.
    Attributes:
        num_preds(int): the total number of model-generated predictions.
    """
    num_preds: int


class DailyPredictionMetric(PredictionMetric):
    """
    The total number of model-generated predictions for specified workflow, for this date.
    Attributes:
        date(str): the date of the prediction.
        num_preds(int): the total number of model-generated predictions.
    """
    date: str


class PredictionMetrics(BaseType):
    """
    Prediction metrics.

    Attributes:
        aggregate(PredictionMetric): Total number of predictions generated for this workflow.
        daily(List[PredictionMetrics]): Number of predictions generated per-date.
    """
    aggregate: PredictionMetric
    daily: List[PredictionMetric]


class StpMetric(BaseType):
    """
    Base Straight through processing (STP) metric for a model, class, or workflow.

    Attributes:
        review_numerator(int): The number of human accepted model predictions.
        auto_review_numerator(int): The nymber of human accepted auto review labels.
        review_denom(int): Total of user supplied labels and model predictions.
        auto_review_denom(int) Total of user supplied labels and auto review labels.
        review_stp_pct(float): Percent of human accepted model predictions. Present if auto review is disabled.
        auto_review_stp_pct(float): Percent of auto review labels accepted. Present if auto review is enabled.
    """
    review_numerator: int
    auto_review_numerator: int
    review_denom: int
    auto_review_denom: int
    review_stp_pct: float
    auto_review_stp_pct: float


class DailyStpMetric(StpMetric):
    """
    Daily Straight through processing (STP) metric for a model, class, or workflow.

    Attributes:
        review_numerator(int): The number of human accepted model predictions.
        auto_review_numerator(int): The nymber of human accepted auto review labels.
        review_denom(int): Total of user supplied labels and model predictions.
        auto_review_denom(int) Total of user supplied labels and auto review labels.
        review_stp_pct(float): Percent of human accepted model predictions. Present if auto review is disabled.
        auto_review_stp_pct(float): Percent of auto review labels accepted. Present if auto review is enabled.
        date(str): The date these metrics are applicable.
    """
    date: str


class ClassStpMetrics(BaseType):
    """
    STP Metrics per class.

    Attributes:
        class_name(str): Name of the class.
        aggregate(StpMetric): Aggregate level metrics about this class.
        daily(List[DailyStpMetric]): Per-date STP metrics for this class.
    """
    class_name: str
    aggregate: StpMetric
    daily: List[DailyStpMetric]


class ModelStpMetrics(BaseType):
    """
    Model STP metrics.

    Attributes:
        model_group_id(int): Id of the model group.
        name(str): Name of the model.
        aggregate(StpMetric): Aggregate level STP metrics for the model.
        daily(List[DailyStpMetric]): Daily STP metrics for the model.
        class_metrics(List[ClassStpMetrics]): Metrics per model class.
    """
    model_group_id: int
    name: str
    aggregate: StpMetric
    daily: List[DailyStpMetric]
    class_metrics: List[ClassStpMetrics]


class WorkflowStpMetrics(BaseType):
    """
    Daily workflow STP metrics.

    Attributes:
        daily(List[DailyStpMetric]): List of daily metrics.
    """
    daily: List[DailyStpMetric]


class StraightThroughProcessing(BaseType):
    """
    Straight Through Processing (STP) metrics.

    Attributes:
        workflow(WorkflowStpMetrics): Daily aggregate workflow level STP metrics.
        model(List[ModelStpMetrics]): Model STP metrics (including class STP).
    """
    workflow: WorkflowStpMetrics
    model: List[ModelStpMetrics]


class WorkflowMetrics(BaseType):
    """
    Workflow metrics for the requested workflow id and dates.

    Attributes:
        workflow_id(int): The workflow id.
        time_on_task(TimeOnTaskMetrics): Time spent on tasks.
        submissions(SubmissionMetrics): Submission specific metrics.
        queues(QueueMetrics): Review queue metrics.
        predictions(PredictionMetrics): Prediction metrics.
        straight_through_processing(StraightThroughProcessing): Straight through processing (STP) metrics.
        first_submitted_date(str): The earliest date of submission to this workflow.

    """
    workflow_id: int
    time_on_task: TimeOnTaskMetrics
    submissions: SubmissionMetrics
    queues: QueueMetrics
    predictions: PredictionMetrics
    straight_through_processing: StraightThroughProcessing
    first_submitted_date: str
