import pytest
from pathlib import Path

from indico.client import IndicoClient
from indico.errors import IndicoError, IndicoInputError
from indico.queries import (
    JobStatus,
    ListWorkflows,
    RetrieveStorageObject,
    WorkflowSubmission,
    WorkflowSubmissionDetailed,
)
from indico.queries.submission import (
    GetSubmission,
    SubmissionResult,
    UpdateSubmission,
)
from indico.types import ModelGroup
from indico.types.submission import Submission

from ..data.datasets import airlines_dataset, airlines_model_group


def test_list_workflows(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    assert len(wfs) > 0


def test_workflow_job(
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

    assert isinstance(result, dict)


def test_workflow_submission(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    submission_ids = client.call(
        WorkflowSubmission(
            workflow_id=wf.id, files=[dataset_filepath]
        )
    )
    submission_id = submission_ids[0]
    assert submission_id is not None

    with pytest.raises(IndicoInputError):
        client.call(SubmissionResult(submission_id, "FAILED"))

    with pytest.raises(IndicoInputError):
        client.call(SubmissionResult(submission_id, "INVALID_STATUS"))

    result_url = client.call(SubmissionResult(submission_id, "COMPLETE", wait=True))
    result = client.call(RetrieveStorageObject(result_url.result))
    assert isinstance(result, dict)
    assert result["submission_id"] == submission_id
    client.call(UpdateSubmission(submission_id, retrieved=True))
    sub = client.call(GetSubmission(submission_id))
    assert isinstance(sub, Submission)
    assert sub.retrieved is True


def test_workflow_submission_detailed(indico, airlines_dataset):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    submissions = client.call(
        WorkflowSubmissionDetailed(
            workflow_id=wf.id, files=[dataset_filepath]
        )
    )
    assert isinstance(submissions[0], Submission)
    assert submissions[0].input_filename == "mock.pdf"


def test_workflow_submission_error(indico,):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    with pytest.raises(IndicoError):
        client.call(WorkflowSubmission(workflow_id=0, files=[dataset_filepath]))
