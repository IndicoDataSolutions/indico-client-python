from datetime import datetime
from indico.queries.workflow import GetWorkflow
import pytest
from pathlib import Path
import time

from indico.client import IndicoClient
from indico.errors import IndicoError, IndicoInputError
from indico.filters import SubmissionFilter
from indico.queries import (
    GetSubmission,
    JobStatus,
    ListSubmissions,
    ListWorkflows,
    RetrieveStorageObject,
    SubmissionResult,
    SubmitReview,
    UpdateSubmission,
    UpdateWorkflowSettings,
    WaitForSubmissions,
    WorkflowSubmission,
    WorkflowSubmissionDetailed,
    AddDataToWorkflow,
    AddFiles,
    ProcessCSV,
    CreateDataset,
)
from indico.queries.questionnaire import CreateQuestionaire, GetQuestionnaire
from indico.types import ModelGroup
from indico.types.submission import Submission

from ..data.datasets import *  # noqa
from ..data.datasets import PUBLIC_URL


def test_list_workflows(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    assert len(wfs) > 0

def test_list_workflows_audit_info(indico, airlines_dataset, airlines_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    assert wfs[0].created_at
    assert isinstance(wfs[0].created_at, datetime)
    assert wfs[0].created_by
    assert isinstance(wfs[0].created_by, int)


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
    assert result["file_version"] == 1
    sub = client.call(GetSubmission(submission_id))
    assert isinstance(sub, Submission)
    assert sub.retrieved is False
    assert sub.deleted is False
    client.call(UpdateSubmission(submission_id, retrieved=True))
    sub = client.call(GetSubmission(submission_id))
    assert sub.retrieved is True

def test_workflow_submission_with_streams(
    indico, airlines_dataset, airlines_model_group: ModelGroup
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    path = Path(str(Path(__file__).parents[1]) + "/data/mock.pdf")
    fd = open(path.absolute(), "rb")
    files = {
        "mock.pdf": fd
    }
    submission_ids = client.call(WorkflowSubmission(workflow_id=wf.id, streams=files))
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
    assert result["file_version"] == 1
    client.call(UpdateSubmission(submission_id, retrieved=True))
    sub = client.call(GetSubmission(submission_id))
    assert isinstance(sub, Submission)
    assert sub.retrieved is True



@pytest.mark.parametrize(
    "_input",
    [
        {"urls": [PUBLIC_URL + "mock.pdf"] * 3},
        {"files": [str(Path(__file__).parents[1]) + "/data/mock.pdf"] * 3},
    ],
)
def test_workflow_submission_versioned(
    indico, airlines_dataset, airlines_model_group: ModelGroup, _input
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    submission_ids = client.call(
        WorkflowSubmission(workflow_id=wf.id, result_version="LATEST", **_input)
    )

    assert len(submission_ids) == len(next(iter(_input.values())))
    submission_id = submission_ids[0]
    assert submission_id is not None

    submissions = client.call(WaitForSubmissions(submission_id))
    result = client.call(RetrieveStorageObject(submissions[0].result_file))

    assert isinstance(result, dict)
    assert result["file_version"] == 2
    assert len(result["submission_results"]) == 1
    assert result["submission_results"][0]["input_filename"] == "mock.pdf"


@pytest.mark.parametrize(
    "_input",
    [
        {"urls": [PUBLIC_URL + "mock.pdf"] * 3},
        {"files": [str(Path(__file__).parents[1]) + "/data/mock.pdf"] * 3},
    ],
)
def test_workflow_submission_bundled(
    indico, airlines_dataset, airlines_model_group: ModelGroup, _input
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    submission_ids = client.call(
        WorkflowSubmission(
            workflow_id=wf.id, bundle=True, result_version="LATEST", **_input
        )
    )

    assert len(submission_ids) == 1
    submission_id = submission_ids[0]
    assert submission_id

    submissions = client.call(WaitForSubmissions(submission_id))
    result = client.call(RetrieveStorageObject(submissions[0].result_file))

    assert isinstance(result, dict)
    assert result["file_version"] == 2
    assert len(result["submission_results"]) == len(next(iter(_input.values())))
    assert result["submission_results"][0]["input_filename"] == "mock.pdf"


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

def test_list_workflow_submission_paginate(
    indico, airlines_dataset, airlines_model_group: ModelGroup
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[airlines_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    dataset_filepath = str(Path(__file__).parents[1]) + "/data/mock.pdf"

    submission_ids = client.call(
        WorkflowSubmission(workflow_id=wf.id, files=[dataset_filepath]*5)
    )
    subs = []

    for sub in client.paginate(ListSubmissions(workflow_ids=[wf.id], limit=3)):
        subs.extend(sub)
    for sub in subs:
        if not submission_ids:
            break
        assert sub.id == submission_ids.pop()  # list is desc by default

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


def test_auto_review_enabled_in_get_workflow_response(
    indico, org_annotate_dataset, org_annotate_model_group
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[org_annotate_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)

    assert not (wf.auto_review_enabled or wf.review_enabled)

    wf = client.call(
        UpdateWorkflowSettings(wf, enable_review=True, enable_auto_review=True)
    )
    assert wf.review_enabled and wf.auto_review_enabled

    wf = client.call(GetWorkflow(workflow_id=wf.id))
    assert wf.review_enabled and wf.auto_review_enabled


@pytest.mark.parametrize("force_complete", [None, True])
def test_workflow_submission_auto_review(
    indico, force_complete, org_annotate_dataset, org_annotate_model_group
):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[org_annotate_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)
    wf = client.call(
        UpdateWorkflowSettings(wf, enable_review=True, enable_auto_review=True)
    )
    assert wf.review_enabled and wf.auto_review_enabled

    _file = str(Path(__file__).parents[1]) + "/data/org-sample.pdf"

    sub_ids = client.call(WorkflowSubmission(workflow_id=wf.id, files=[_file]))
    subs = client.call(WaitForSubmissions(sub_ids, timeout=120))
    sub = subs[0]
    assert sub.status == "PENDING_AUTO_REVIEW"
    raw_result = client.call(RetrieveStorageObject(sub.result_file))
    changes = raw_result["results"]["document"]["results"]
    for model, preds in changes.items():
        if isinstance(preds, dict):
            preds["accepted"] = True
        elif isinstance(preds, list):
            for pred in preds:
                pred["accepted"] = True
    job = client.call(
        SubmitReview(sub.id, changes=changes, force_complete=force_complete)
    )
    job = client.call(JobStatus(job.id))
    submission = client.call(GetSubmission(sub.id))
    assert submission.status == "COMPLETE" if force_complete else "PENDING_REVIEW"


def _new_dataset_for_updating(client):
    # new dataset
    airline_csv = str(Path(__file__).parents[1]) + "/data/AirlineComplaints.csv"
    dataset = client.call(
        CreateDataset(
            name=f"AddDataToWorkflow-test-{int(time.time())}", files=[airline_csv]
        )
    )

    # new teach task
    questionnaire = client.call(
        CreateQuestionaire(
            name=f"AddDataToWorkflowTeach-test-{int(time.time())}",
            dataset_id=dataset.id,
            targets=["positive", "negative"],
        )
    )

    assert questionnaire.num_total_examples > 0

    # add data to dataset and process
    dataset = client.call(AddFiles(dataset_id=dataset.id, files=[airline_csv]))
    datafile_ids = [f.id for f in dataset.files]
    dataset = client.call(
        ProcessCSV(dataset_id=dataset.id, datafile_ids=datafile_ids, wait=True)
    )

    assert dataset.status == "COMPLETE"

    # get workflow
    wfs = client.call(ListWorkflows(dataset_ids=[dataset.id]))
    wf = max(wfs, key=lambda w: w.id)
    return dataset, wf, questionnaire


def test_add_data_to_workflow_wait(indico):
    client = IndicoClient()
    _, wf, q1 = _new_dataset_for_updating(client)

    wf = client.call(AddDataToWorkflow(wf.id, wait=True))
    assert wf.status == "COMPLETE"

    q2 = client.call(GetQuestionnaire(q1.id))
    # the total num avaliable should double, since we re-add the same data
    assert q1.num_total_examples * 2 == q2.num_total_examples


def test_add_data_to_workflow_nowait(indico):
    client = IndicoClient()
    _, wf, _ = _new_dataset_for_updating(client)

    wf = client.call(AddDataToWorkflow(wf.id))
    assert wf.status == "ADDING_DATA"
