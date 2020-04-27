from typing import List
from indico.types.base import BaseType


class PerClassSeqMetrics(BaseType):
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
    """

    name: str
    metrics: List[PerClassSeqMetrics]


class ModelLevelMetrics(BaseType):
    """
    Sequence model metrics at the model level
    """

    span_type: str
    macro_f1: float
    micro_f1: float
    weighted_f1: float


class SequenceMetrics(BaseType):
    """
    Model performance metrics calculated for sequence or "annotation" models.
    """

    class_metrics: List[AnnotationClassMetrics]
    model_level_metrics: List[ModelLevelMetrics]
