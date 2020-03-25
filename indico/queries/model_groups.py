from time import sleep
from typing import List

from indico.client.request import GraphQLRequest, RequestChain
from indico.types.model_group import ModelGroup
from indico.types.model import Model
from indico.types.jobs import Job
from indico.errors import IndicoNotFound, IndicoError


class GetModelGroup(GraphQLRequest):
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
        ) {
                createModelGroup(
                    datasetId: $datasetId,
                    sourceColumnId: $sourceColumnId,
                    labelsetColumnId: $labelsetColumnId,
                    name: $name,
                ) {
                    id
                    status
                    name
                }
            }
    """

    def __init__(
        self, name: str, dataset_id: int, source_column_id: int, labelset_id: int,
    ):
        super().__init__(
            query=self.query,
            variables={
                "name": name,
                "datasetId": dataset_id,
                "sourceColumnId": source_column_id,
                "labelsetColumnId": labelset_id,
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
    ):
        self.name = name
        self.dataset_id = dataset_id
        self.source_column_id = source_column_id
        self.labelset_id = labelset_id
        self.wait = wait

    def requests(self):
        yield _CreateModelGroup(
            name=self.name,
            dataset_id=self.dataset_id,
            source_column_id=self.source_column_id,
            labelset_id=self.labelset_id,
        )
        model_group_id = self.previous.id
        if self.wait:
            req = GetModelGroupSelectedModelStatus(id=model_group_id)
            yield req
            while self.previous not in ["FAILED", "COMPLETE"]:
                sleep(1)
                yield req

            yield GetModelGroup(id=model_group_id)


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
        mutation ModelGroupPredict($modelId: Int!, $data: [String]) {
            modelPredict(modelId: $modelId, data: $data) {
                jobId
            }
        }
        """

    def __init__(self, model_id: int, data: List[str]):
        super().__init__(
            query=self.query, variables={"modelId": model_id, "data": data}
        )

    def process_response(self, response):
        return Job(**super().process_response(response)["modelPredict"])


class ModelGroupPredict(RequestChain):
    """
    Generate predictions from a model group on new data

    Args:
        model_id= (int): selected model id use for predictions
        data= (List[str]): list of samples to predict

    Returns:
        Job associated with this model group predict task

    Raises:

    """

    def __init__(self, model_id: int, data: List[str], load: bool = True):
        self.model_id = model_id
        self.data = data
        self.load = load

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

        yield _ModelGroupPredict(model_id=self.model_id, data=self.data)
