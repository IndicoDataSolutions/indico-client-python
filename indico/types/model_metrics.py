from typing import List

from indico.types.base import BaseType


class PerClassSeqMetrics(BaseType):
    """
    Metrics per class

    Attributes:
        span_type (str): Type of span the metric is evaluated on: token, superset, overlap, exact
        f1_score (float): F1 score per class
        precision (float): precision per class
        recall (float): recall per class
        true_positives (int): true positives per class
        false_negatives (int): false negatives per class
        false_positives (int): false_positives
    """

    span_type: str
    f1_score: float
    precision: float
    recall: float
    true_positives: int
    false_negatives: int
    false_positives: int


class AnnotationClassMetrics(BaseType):
    """
    Sequence model metrics per class

    Attributes:
        name (str): class name
        metrics List[PerClassMetrics]: Object containing metrics per class
    """

    name: str
    metrics: List[PerClassSeqMetrics]


class ModelLevelMetrics(BaseType):
    """
    Sequence model metrics at the model level

    Attributes:
        span_type (str): Type of span the metric is evaluated on: token, superset, overlap, exact
        macro_f1 (float): f1-score calculated by taking simple average of class-specific scores
        micro_f1 (float): f1-score calculated by weighting instances across classes
        weighted_f1 (float): f1-score calculated by taking class-specific f1-scores and weighting by available
        positive examples per class
    """

    span_type: str
    macro_f1: float
    micro_f1: float
    weighted_f1: float


class SequenceMetrics(BaseType):
    """
    Model performance metrics calculated for sequence or "annotation" models.

    Attributes:

        class_metrics List[AnnotationClassMetrics]: List of AnnotationClassMetrics objects per class
        model_level_metrics List[ModelLevelMetrics]: List of ModelLevelMetrics objects per span type
        retrain_for_metrics bool: Older annotation models require retraining metrics calculation
    """

    class_metrics: List[AnnotationClassMetrics]
    model_level_metrics: List[ModelLevelMetrics]
    retrain_for_metrics: bool
