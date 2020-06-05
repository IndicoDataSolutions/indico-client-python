from pathlib import Path

from indico.client import IndicoClient
from indico.queries import (
    JobStatus,
    ListSubmissions,
    ListWorkflowsForDataset,
    WorkflowSubmission,
)
from indico.types import Job, ModelGroup
from ..data.datasets import airlines_dataset, airlines_model_group


def test_list_submissions(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflowsForDataset(airlines_dataset.id))

    wf = wfs[0]
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    job = client.call(WorkflowSubmission(workflow_id=wf.id, files=[dataset_filepath]))
    assert job.id != None
    job = client.call(JobStatus(id=job.id, wait=True))

    submissions = client.call(ListSubmissions(workflow_ids=[wf.id]))
    assert len(submissions) > 0
