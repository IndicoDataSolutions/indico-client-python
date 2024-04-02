import json
from typing import Any, Dict, List, Optional, Union

import deprecation

from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.errors import IndicoNotFound
from indico.queries.workflow_components import AddModelGroupComponent
from indico.types.jobs import Job
from indico.types.model import Model, ModelOptions
from indico.types.model_group import ModelGroup
from indico.types.utils import cc_to_snake


class GetModelGroup(RequestChain):
    """
    Get an object describing a model group

    Args:
        id (int): model group id to query
        wait (bool, optional): Wait until the Model Group status is FAILED, COMPLETE, or NOT_ENOUGH_DATA. Defaults to False.
        request_interval (int or float, optional): The maximum time in between retry calls when waiting. Defaults to 5 seconds.

    Returns:
        ModelGroup object
    """

    def __init__(
        self, id: int, wait: bool = False, request_interval: Union[int, float] = 5
    ):
        self.id = id
        self.wait = wait
        self.request_interval = request_interval

    def requests(self):
        if self.wait:
            req = GetModelGroupSelectedModelStatus(id=self.id)
            yield req
            while self.previous not in ["FAILED", "COMPLETE", "NOT_ENOUGH_DATA"]:
                yield Delay(seconds=self.request_interval)
                yield req
        yield _GetModelGroup(id=self.id)


class _GetModelGroup(GraphQLRequest):
    """
    Get an object describing a model group

    Args:
        id (int): model group id to query

    Returns:
        ModelGroup object
    """

    query = """
        query GetModelGroup($id: Int){
            modelGroups(modelGroupIds: [$id]) {
                    modelGroups {
                        id
                        name
                        status
                        taskType
                        selectedModel {
                            id
                            status
                        }
                    }
                }
            }
        """

    def __init__(self, id: int):
        super().__init__(query=self.query, variables={"id": id})

    def process_response(self, response):
        try:
            mg = ModelGroup(
                **super().process_response(response)["modelGroups"]["modelGroups"][0]
            )
        except IndexError:
            raise IndicoNotFound(
                "ModelGroup not found. Please check the ID you are using."
            )
        return mg


class GetTrainingModelWithProgress(GraphQLRequest):
    """
    Get progress (percent complete) of a training model group

    Args:
        id (int): model group id to query

    Returns:
        Model object with percent_complete field
    """

    query = """
        query ModelGroupProgress($id: Int){
            modelGroups(modelGroupIds: [$id]){
                modelGroups{
                    models {
                        id
                        status
                        trainingProgress {
                            percentComplete
                        }
                    }
                }
            }
        }
    """

    def __init__(self, id: int):
        super().__init__(query=self.query, variables={"id": id})

    def process_response(self, response):
        response = super().process_response(response)
        model_groups = response["modelGroups"]["modelGroups"]
        if len(model_groups) != 1:
            raise IndicoNotFound("Model Group")
        models = model_groups[0]["models"]

        last = max(models, key=lambda m: m["id"])
        if not last:
            raise IndicoNotFound("Training Model")

        return Model(**last)


class GetModelGroupSelectedModelStatus(GraphQLRequest):
    """
    Get the status string of the selected model for the given model group id

    Args:
        id (int): model group id to query

    Returns:
        status (str): CREATED, TRAINING, COMPLETE or FAILED
    """

    query = """
        query GetModelGroup($id: Int) {
                modelGroups(modelGroupIds: [$id]) {
                    modelGroups {
                        id
                        selectedModel {
                            id
                            status
                        }
                    }
                }
            }
        """

    def __init__(self, id: int):
        super().__init__(query=self.query, variables={"id": id})

    def process_response(self, response):
        mg = ModelGroup(
            **super().process_response(response)["modelGroups"]["modelGroups"][0]
        )
        return mg.selected_model.status


class _ModelGroupPredict(GraphQLRequest):
    query = """
        mutation ModelGroupPredict(<QUERY_ARGS>) {
            modelPredict(<MODEL_PREDICT_ARGS>) {
                jobId
            }
        }
        """

    query_args = {"modelId": "Int!", "data": "[String]", "predictOptions": "JSONString"}

    def _args_strings(self, **kwargs):
        args = [k for k in self.query_args.keys() if kwargs.get(cc_to_snake(k))]

        query_args_string = ",".join(f"${k}: {self.query_args[k]}" for k in args)
        model_predict_args = ",".join(f"{k}: ${k}" for k in args)

        query = self.query.replace("<QUERY_ARGS>", query_args_string)
        query = query.replace("<MODEL_PREDICT_ARGS>", model_predict_args)

        return query

    def __init__(self, model_id: int, data: List[str], predict_options: Dict = None):
        if predict_options:
            predict_options = json.dumps(predict_options)

        query = self._args_strings(
            model_id=model_id, data=data, predict_options=predict_options
        )

        super().__init__(
            query=query,
            variables={
                "modelId": model_id,
                "data": data,
                "predictOptions": predict_options,
            },
        )

    def process_response(self, response):
        return Job(**super().process_response(response)["modelPredict"])


class ModelGroupPredict(RequestChain):
    """
    Generate predictions from a model group on new data

    Args:
        model_id (int): selected model id use for predictions
        data (List[str]): list of samples to predict
        predict_options (JSONString): arguments for predictions

    Returns:
        Job associated with this model group predict task
    """

    def __init__(
        self,
        model_id: int,
        data: List[str],
        load: bool = True,
        predict_options: Dict = None,
    ):
        self.model_id = model_id
        self.data = data
        self.predict_options = predict_options

    def requests(self):

        yield _ModelGroupPredict(
            model_id=self.model_id, data=self.data, predict_options=self.predict_options
        )


class UpdateModelGroupSettings(GraphQLRequest):
    """
    Updates an existing model group component in the platform.

    Args:
        model_group_id (int): the id of the model group to update settings
        model_training_options (dict, optional): model training options to use when training model. Defaults to None
        predict_options (dict, optional): predict options to use on model. Defaults to None
        domain (str, optional): feature domain to use.
            Valid values include STANDARD, STANDARD_V2, TOPICS, SENTIMENT, FINANCE, EMOTION, ENSEMBLE, FASTTEXT, UNSUPERVISEDSENTIMENT, IMAGE_V2, IMAGE_V3, IMAGE_V4, IMAGE_ENSEMBLE
            Defaults to None
        finetune (bool, optional): flag to use finetune or not in model training. Defaults to None
        interlabeler_resolution (str, optional): denotes label resolution strategy.
            Valid values include MAJORITY_VOTE_WITH_TIES, MAJORITY_VOTE_WITHOUT_TIES, UNANIMOUS, ALL
            Defaults to None
        make_predictions (bool, optional): flag to make predictions or not. Defaults to None
        roc_auc_averaging (str, optional): roc auc averaging.
            Valid values include SIMPLE, WEIGHTED
            Defaults to None
        sampling_strategy (str, optional): denote sampling strategy to use.
            Valid values include NO_SAMPLING, RANDOM_OVERSAMPLE
            Defaults to None
        task_type (str, optional): denotes task type.
            Valid values include CLASSIFICATION, CLASSIFICATION_MULTIPLE, RATIONALIZED_CLASSIFICATION, REGRESSION, ANNOTATION, OBJECT_DETECTION, FORM_EXTRACTION, CLASSIFICATION_UNBUNDLING
            Defaults to None
        test_split (float, optional): denotes test split. Defaults to None
        word_predictor_strength (str, optional): denotes word predictor strength
            Valid values include STRONG, MODERATE, WEAK
            Defaults to None
    """

    query = """
        mutation updateModelGroup($modelGroupId: Int!, $modelTrainingOptions: JSONString) {
            updateModelGroupSettings(
                modelGroupId: $modelGroupId
                modelTrainingOptions: $modelTrainingOptions
            ) {
                modelOptions {
                    id
                    domain
                    highQuality
                    interlabelerResolution
                    samplingStrategy
                    seed
                    testSplit
                    weightByClassFrequency
                    wordPredictorStrength
                    modelTrainingOptions
                    predictOptions
                }
            }
        }
    """

    def __init__(
        self,
        model_group_id: int,
        model_training_options: Optional[Dict[str, Any]] = None,
        predict_options: Optional[Dict[str, Any]] = None,
        domain: str = None,
        finetune: bool = None,
        interlabeler_resolution: str = None,
        make_predictions: bool = None,
        roc_auc_averaging: str = None,
        sampling_strategy: str = None,
        task_type: str = None,
        test_split: float = None,
        word_predictor_strength: str = None,
    ):
        if model_training_options:
            model_training_options = json.dumps(model_training_options)

        super().__init__(
            self.query,
            variables={
                "modelGroupId": model_group_id,
                "modelTrainingOptions": model_training_options,
                "predictOptions": predict_options,
                "domain": domain,
                "finetune": finetune,
                "interlabelerResolution": interlabeler_resolution,
                "makePredictions": make_predictions,
                "rocAucAveraging": roc_auc_averaging,
                "samplingStrategy": sampling_strategy,
                "taskType": task_type,
                "testSplit": test_split,
                "wordPredictorStrength": word_predictor_strength,
            },
        )

    def process_response(self, response):
        return ModelOptions(
            **super().process_response(response)["updateModelGroupSettings"][
                "modelOptions"
            ]
        )
