from indico.client.request import GraphQLRequest
from indico.types.metrics import SequenceMetrics
import json


class AnnotationModelGroupMetrics(GraphQLRequest):
    """
    Get metrics for annotation or "sequence" models. Metrics for the
    most recently succesfully trained model of the model group are returned.

    Args:
        id (int): model group id to query

    Returns:
        SequenceMetrics object
    """

    query = """
    query modelGroupMetrics($modelGroupId: Int!){
            modelGroups(
                modelGroupIds: [$modelGroupId]
            ) {
                modelGroups {
                    selectedModel {
                        evaluation {
                        ... on AnnotationEvaluation {
                            metrics {
                                classMetrics {
                                    name
                                    metrics {
                                        spanType
                                        precision
                                        recall
                                        f1Score
                                        falsePositives
                                        falseNegatives
                                        truePositives
                                    }
                                }
                                modelLevelMetrics {
                                    spanType
                                    microF1
                                    macroF1
                                    weightedF1
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    def __init__(self, model_group_id: int):
        super().__init__(self.query, variables={"modelGroupId": model_group_id})

    def process_response(self, response):
        return SequenceMetrics(
            **super().process_response(response)["modelGroups"]["modelGroups"][0][
                "selectedModel"
            ]["evaluation"]["metrics"]
        )


class ObjectDetectionMetrics(GraphQLRequest):
    """
    Get metrics for a trained object detection model. Metrics for the
    most recently succesfully trained model of the model group are returned.

    Args:
        id (int): model group id to query
    
    Returns:
        Dict of object detection metrics
    """

    query = """
    query modelGroupMetrics($modelGroupId: Int!) {
    modelGroups(modelGroupIds: [$modelGroupId]) {
        modelGroups {
        selectedModel {
            evaluation {
            ... on ObjectDetectionEvaluation {
                metrics
              }
            }
          }
        }
      }
    }
    """

    def __init__(self, model_group_id: int):
        super().__init__(self.query, variables={"modelGroupId": model_group_id})

    def process_response(self, response):
        return json.loads(
            super().process_response(response)["modelGroups"]["modelGroups"][0][
                "selectedModel"
            ]["evaluation"]["metrics"]
        )
