import pytest
from pathlib import Path

from ..data.datasets import airlines_dataset, airlines_model_group
from indico.client import IndicoClient
from indico.errors import IndicoError
from indico.queries import (
    JobStatus,
    ListWorkflows,
    RetrieveStorageObject,
    WorkflowSubmission,
)
from indico.types import ModelGroup


def test_list_workflows(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    assert len(wfs) > 0


def test_workflow_submission(
    indico, airlines_dataset, airlines_model_group: ModelGroup
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    jobs = client.call(
        WorkflowSubmission(
            workflow_id=wf.id, files=[dataset_filepath], submission=False
        )
    )
    job = jobs[0]

    assert job.id is not None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready is True
    assert isinstance(job.result["url"], str)

    result = client.call(RetrieveStorageObject(job.result))

    assert isinstance(result, str)


def test_workflow_submission_error(indico,):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    with pytest.raises(IndicoError):
        client.call(WorkflowSubmission(workflow_id=0, files=[dataset_filepath]))
