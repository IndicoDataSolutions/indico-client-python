import json
from typing import Dict, List, Union

import deprecation

from indico.client.request import Delay, GraphQLRequest, RequestChain
from indico.errors import IndicoNotFound
from indico.queries.workflow_components import AddModelGroupComponent
from indico.types.jobs import Job
from indico.types.model import Model
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
