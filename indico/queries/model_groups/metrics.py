from indico.client.request import GraphQLRequest, RequestChain
from indico.types.model_metrics import SequenceMetrics
from indico.queries.model_groups import GetModelGroup
from indico.errors import IndicoRequestError
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
                                retrainForMetrics
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
        try:
            return json.loads(
                super().process_response(response)["modelGroups"]["modelGroups"][0][
                    "selectedModel"
                ]["evaluation"]["metrics"]
            )
        except IndexError:
            raise IndicoRequestError(
                (
                    "No results found. Please check that you have used the correct Model Group ID "
                    "(*not* the selected model ID) and have permission to access that model."
                ),
                code=400,
            )


task_type_query_mapping = {
    "ANNOTATION": AnnotationModelGroupMetrics,
    "OBJECT_DETECTION": ObjectDetectionMetrics,
}


class GetModelGroupMetrics(RequestChain):
    """
    Args:
        model_group_id (int): ModelGroup id
    
    Returns
        Metrics object depending on task type the model solves
    """

    def __init__(self, model_group_id: int):
        self.model_group_id = model_group_id
        super().__init__()

    def requests(self):
        yield GetModelGroup(id=self.model_group_id)
        if self.previous.task_type not in task_type_query_mapping:
            raise IndicoRequestError(
                "Metrics queries are only supported for annotation and object detection at this time."
            )
        metrics_query_fn = task_type_query_mapping.get(self.previous.task_type)
        yield metrics_query_fn(self.model_group_id)
        return self.previous
