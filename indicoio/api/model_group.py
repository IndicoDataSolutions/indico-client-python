"""
TODO: Move predict to selected_model.predict. Create Model and auto fetch selected_model on ModelGroup to get Model

"""
import time
import json

from .base import ObjectProxy
from .job_result import JobResult
from indicoio.errors import IndicoInputError


class ModelGroup(ObjectProxy):
    """
    Model Group

    Example::

        mg = ModelGroup(id=<model group id>)
        mg.load()
        mg.predict(["some text"])

    :param config_options: configureation options for the model group
    """

    def predict(self, data=None, job_results=False, model_id=None, **predict_kwargs):
        """
        Gets the model predictions for a list of inputs

        :param data: List of inputs for predictions.
        :param model_id: Specify the specific model to use for predition. If empty, the currently selected model within this group will be used
        :param job_results: True to return the id of the prediction job rather than the prediction results directly.
        """
        if not isinstance(data, list):
            raise IndicoInputError(
                "This function expects a list input. If you have a single piece of data, please wrap it in a list"
            )

        data = json.dumps(data)

        if not model_id:
            model_id = self.get_selected_model()["id"]

        response = self.graphql.query(
            f"""mutation {{
            modelPredict(modelId: {model_id}, data: {data}) {{
                jobId
            }}
        }}"""
        )
        job_id = response["data"]["modelPredict"]["jobId"]
        job = self.build_object(JobResult, id=job_id)
        if job_results:
            return job
        else:
            job.wait()
            return job.result()

    def load(self, model_id=None):
        """
        Loads the requested model into memory for predictions

        :param model_id: Specify the specific model to use for predition. If empty, the most recently trained model will be used.
        """
        if self.info().get("load_status") == "ready":
            return "ready"

        if not model_id:
            model_id = self.get_selected_model()["id"]

        response = self.graphql.query(
            f"""mutation {{
            modelLoad(modelId: {model_id}) {{
                status
            }}
        }}"""
        )

        status = response["data"]["modelLoad"]["status"]

        while status == "loading":
            status = self.info().get("load_status", "loading")
            time.sleep(1)

        return status

    def info(self):
        """
        Returns information about this model group.
        """
        response = self.graphql.query(
            f"""query {{
                modelGroups(modelGroupIds: [{self["id"]}]) {{
                    modelGroups {{
                        id
                        selectedModel {{
                            id
                            modelInfo
                        }}
                }}
            }}
        }}"""
        )

        model = response["data"]["modelGroups"]["modelGroups"][0]["selectedModel"]
        if model:
            return json.loads(model.get("modelInfo"))
        return {}

    def get_selected_model(self):
        """
        Returns the ID of the currently selected model within this group
        """
        response = self.graphql.query(
            f"""query {{
                modelGroups(modelGroupIds: [{self["id"]}]) {{
                    modelGroups {{
                        selectedModel {{
                            id
                            modelInfo
                        }}
                }}
            }}
        }}"""
        )
        mg = response["data"]["modelGroups"]["modelGroups"][0]
        self.update(mg)
        return self["selectedModel"]

    def refresh(self):
        """
        Refreshes something... unclear
        """
        response = self.graphql.query(
            f"""query {{
                modelGroups(modelGroupIds: [{self["id"]}]) {{
                    modelGroups {{
                        id
                        name
                        status
                        taskType
                        dataType
                        retrainRequired
                        labelset {{
                            id
                        }}
                        sourceColumn {{
                            id
                        }}
                        selectedModel {{
                            id
                            modelInfo
                        }}
                }}
            }}
        }}"""
        )
        mg = response["data"]["modelGroups"]["modelGroups"][0]
        self.update(mg)
