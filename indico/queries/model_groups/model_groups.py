import json
from time import sleep
from typing import List, Dict

from indico.client.request import GraphQLRequest, RequestChain
from indico.types.model_group import ModelGroup
from indico.types.model import Model
from indico.types.jobs import Job
from indico.types.utils import cc_to_snake

from indico.errors import IndicoNotFound, IndicoError


class GetModelGroup(RequestChain):
    """
    Get an object describing a model group

    Args:
        id (int): model group id to query

    Returns:
        ModelGroup object

    Raises:

    """

    def __init__(self, id: int, wait: bool = False):
        self.id = id
        self.wait = wait

    def requests(self):
        if self.wait:
            req = GetModelGroupSelectedModelStatus(id=self.id)
            yield req
            while self.previous not in ["FAILED", "COMPLETE", "NOT_ENOUGH_DATA"]:
                sleep(1)
                yield req
            yield _GetModelGroup(id=self.id)


class _GetModelGroup(GraphQLRequest):
    """
    Get an object describing a model group

    Args:
        id (int): model group id to query

    Returns:
        ModelGroup object

    Raises:

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

    Raises:

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


class _CreateModelGroup(GraphQLRequest):
    query = """
        mutation CreateModelGroup(
            $datasetId: Int!,
            $sourceColumnId: Int!,
            $labelsetColumnId: Int,
            $name: String!,
            $modelTrainingOptions: JSONString,
            $modelType: ModelType,
        ) {
                createModelGroup(
                    datasetId: $datasetId,
                    sourceColumnId: $sourceColumnId,
                    labelsetColumnId: $labelsetColumnId,
                    modelTrainingOptions: $modelTrainingOptions,
                    name: $name,
                    modelType: $modelType
                ) {
                    id
                    status
                    name
                }
            }
    """

    def __init__(
            self,
            name: str,
            dataset_id: int,
            source_column_id: int,
            labelset_id: int,
            model_training_options: dict = None,
            model_type: str = None,
    ):
        if model_training_options:
            model_training_options = json.dumps(model_training_options)
        super().__init__(
            query=self.query,
            variables={
                "name": name,
                "datasetId": dataset_id,
                "sourceColumnId": source_column_id,
                "labelsetColumnId": labelset_id,
                "modelTrainingOptions": model_training_options,
                "modelType": model_type,
            },
        )

    def process_response(self, response):
        return ModelGroup(**super().process_response(response)["createModelGroup"])


class GetModelGroupSelectedModelStatus(GraphQLRequest):
    """
    Get the status string of the selected model for the given model group id

    Args:
        id (int): model group id to query

    Returns:
        status (str): CREATED, TRAINING, COMPLETE or FAILED

    Raises:

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


class CreateModelGroup(RequestChain):
    """
    Create a new model group and train a model

    Args:
        name (str): Name of the new model group
        dataset_id (int): id of the dataset that this model group is based upon
        source_column_id (int): id of the source column to use in training this model group. Usually the id of source text or images.
        labelset_id (int): id of the labelset (labeled data) to use in training this model group
        wait (bool): Wait for this model group to finish training. Default is False
        model_training_options (dict): Additional options for training. If the model_type is FINETUNE, this can include the base_model, which should be one of "default", "roberta", "small", "multilingual", "fast", "textcnn", or "fasttextcnn".
        model_type (str): The model type to use, defaults to the default model type for the dataset type. Valid options are "ENSEMBLE", "TFIDF_LR", "TFIDF_GBT", "STANDARD", "FINETUNE", "OBJECT_DETECTION", "RATIONALIZED", "FORM_EXTRACTION", and "DOCUMENT".

    Returns:
        ModelGroup object

    Raises:

    """

    def __init__(
            self,
            name: str,
            dataset_id: int,
            source_column_id: int,
            labelset_id: int,
            wait: bool = False,
            model_training_options: dict = None,
            model_type: str = None,
    ):
        self.name = name
        self.dataset_id = dataset_id
        self.source_column_id = source_column_id
        self.labelset_id = labelset_id
        self.wait = wait
        self.model_training_options = model_training_options
        self.model_type = model_type

    def requests(self):
        yield _CreateModelGroup(
            name=self.name,
            dataset_id=self.dataset_id,
            source_column_id=self.source_column_id,
            labelset_id=self.labelset_id,
            model_training_options=self.model_training_options,
            model_type=self.model_type,
        )
        model_group_id = self.previous.id
        if self.wait:
            req = GetModelGroupSelectedModelStatus(id=model_group_id)
            yield req
            while self.previous not in ["FAILED", "COMPLETE", "NOT_ENOUGH_DATA"]:
                sleep(1)
                yield req

            yield _GetModelGroup(id=model_group_id)


class LoadModel(GraphQLRequest):
    """
    Load model into system cache (implicit in ModelGroupPredict unless load=False)

    Args:
        model_id= (int): selected model id use for predictions

    Returns:
        Status "ready" if loaded
    Raises:
        IndicoError if model fails to load after retries
    """

    query = """
        mutation ModelLoad($modelId: Int!) {
            modelLoad(modelId: $modelId) {
                status
            }
        }
    """

    def __init__(self, model_id: int):
        super().__init__(self.query, variables={"modelId": model_id})

    def process_response(self, response):
        return super().process_response(response)["modelLoad"]["status"]


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
        model_id= (int): selected model id use for predictions
        data= (List[str]): list of samples to predict
        predict_options= (JSONString): arguments for predictions

    Returns:
        Job associated with this model group predict task

    Raises:

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
        self.load = load
        self.predict_options = predict_options

    def requests(self):
        retries = 0
        if self.load:
            while retries < 3 and self.previous != "ready":
                retries += 1
                yield LoadModel(self.model_id)
                if retries > 0:
                    sleep(1)
            if self.previous != "ready":
                raise IndicoError(
                    f"Model {self.model_id} failed to load status {self.previous}"
                )

        yield _ModelGroupPredict(
            model_id=self.model_id, data=self.data, predict_options=self.predict_options
        )
