import pytest
from pathlib import Path
from indico.client import IndicoClient
from indico.queries import RetrieveStorageObject, JobStatus, WorkflowSubmission, ListWorkflowsForDataset
from indico.types import Job, ModelGroup
from ..data.datasets import airlines_dataset, airlines_model_group

def test_list_workflows(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflowsForDataset(airlines_dataset.id))
    assert len(wfs) > 0    

def test_workflow_submission(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflowsForDataset(airlines_dataset.id))
    wf = max(wfs, key=lambda w: w.id)

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"
    
    job = client.call(WorkflowSubmission(workflow_id=wf.id, files=[dataset_filepath]))

    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready == True
    assert isinstance(job.result["url"], str)

    result = client.call(RetrieveStorageObject(
       job.result
    ))

    assert isinstance(result, str)


