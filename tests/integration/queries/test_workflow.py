import pytest
from pathlib import Path

from indico.client import IndicoClient
from indico.errors import IndicoError, IndicoInputError
from indico.filters import SubmissionFilter
from indico.queries import (
    JobStatus,
    ListWorkflows,
    RetrieveStorageObject,
    WorkflowSubmission,
    WorkflowSubmissionDetailed,
)
from indico.queries.submission import (
    GetSubmission,
    ListSubmissions,
    SubmissionResult,
    UpdateSubmission,
)
from indico.types import ModelGroup
from indico.types.submission import Submission

from ..data.datasets import *  # noqa
from ..data.datasets import PUBLIC_URL


def test_list_workflows(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    assert len(wfs) > 0


def test_workflow_job(indico, airlines_dataset, airlines_model_group: ModelGroup):
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


@pytest.mark.parametrize(
    "_input",
    [
        {"urls": [PUBLIC_URL + "mock.pdf"]},
        {"files": [str(Path(__file__).parents[1]) + "/data/mock.pdf"]},
    ],
)
def test_workflow_submission(
    indico, airlines_dataset, airlines_model_group: ModelGroup, _input
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    submission_ids = client.call(WorkflowSubmission(workflow_id=wf.id, **_input))
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


@pytest.mark.parametrize(
    "_input,_output",
    [
        ({"urls": [PUBLIC_URL + "mock.pdf"]}, PUBLIC_URL + "mock.pdf"),
        ({"files": [str(Path(__file__).parents[1]) + "/data/mock.pdf"]}, "mock.pdf"),
    ],
)
def test_workflow_submission_detailed(
    indico, airlines_dataset, airlines_model_group: ModelGroup, _input, _output
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    submissions = client.call(WorkflowSubmissionDetailed(workflow_id=wf.id, **_input))
    assert isinstance(submissions[0], Submission)
    assert submissions[0].input_filename == _output


def test_list_workflow_submission_retrieved(
    indico, airlines_dataset, airlines_model_group: ModelGroup
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    submission_ids = client.call(
        WorkflowSubmission(workflow_id=wf.id, files=[dataset_filepath])
    )
    submission_id = submission_ids[0]
    assert submission_id is not None
    client.call(SubmissionResult(submission_id, "COMPLETE", wait=True))
    client.call(UpdateSubmission(submission_id, retrieved=True))

    submissions = client.call(
        ListSubmissions(filters=SubmissionFilter(retrieved=True, status="COMPLETE"))
    )
    assert all([s.retrieved for s in submissions])
    assert submission_id in [s.id for s in submissions]

    submissions = client.call(
        ListSubmissions(filters=SubmissionFilter(retrieved=False))
    )
    assert all([not s.retrieved for s in submissions])
    assert submission_id not in [s.id for s in submissions]


def test_workflow_submission_missing_workflow(indico):
    client = IndicoClient()
    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    with pytest.raises(IndicoError):
        client.call(WorkflowSubmission(workflow_id=0, files=[dataset_filepath]))


def test_workflow_submission_mixed_args(indico, airlines_dataset):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    _file = str(Path(__file__).parents[1]) + "/data/mock.pdf"
    url = PUBLIC_URL + "mock.pdf"

    with pytest.raises(IndicoInputError):
        client.call(WorkflowSubmission(workflow_id=wf.id, files=[_file], urls=[url]))
