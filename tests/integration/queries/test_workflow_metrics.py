import json
from pathlib import Path
from typing import List

import pytest

from build.lib.indico.queries.questionnaire import AddLabels
from indico import IndicoConfig
from indico.client import IndicoClient
from indico.queries import JobStatus, RetrieveStorageObject, CreateDataset, GetDataset, ListWorkflows, \
    UpdateWorkflowSettings, WorkflowSubmission, SubmissionResult, UpdateSubmission, GetSubmission, WaitForSubmissions, \
    SubmitReview
from indico.queries.questionnaire import CreateQuestionaire, GetQuestionnaireExamples, GetQuestionnaire
from indico.types.workflow_metrics import WorkflowMetrics, WorkflowMetricsOptions
from indico.queries.workflow_metrics import GetWorkflowMetrics
from datetime import datetime
from ..data.datasets import *  # noqa
from ..data.datasets import PUBLIC_URL
import time

@pytest.fixture
def workflow(indico, org_annotate_dataset, org_annotate_model_group: ModelGroup):
    client = IndicoClient()
    wfs = client.call(ListWorkflows(dataset_ids=[org_annotate_dataset.id]))
    wf = max(wfs, key=lambda w: w.id)
    wf = client.call(
        UpdateWorkflowSettings(wf, enable_review=True, enable_auto_review=True)
    )
    assert wf.review_enabled and wf.auto_review_enabled

    _file = str(Path(__file__).parents[1]) + "/data/org-sample.pdf"

    sub_ids = client.call(WorkflowSubmission(workflow_id=wf.id, files=[_file]))
    subs = client.call(WaitForSubmissions(sub_ids, timeout=900))
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
        SubmitReview(sub.id, changes=changes, force_complete=True)
    )
    job = client.call(JobStatus(job.id, timeout=900))
    submission = client.call(GetSubmission(sub.id))
    assert submission.status == "COMPLETE"

    return wf

def test_fetch_metrics(indico, org_annotate_dataset, workflow):
    client = IndicoClient()
    #time.sleep(300)
    workflow_metric: List[WorkflowMetrics] = \
        client.call(GetWorkflowMetrics(options=[WorkflowMetricsOptions.SUBMISSIONS], start_date=datetime.now(),
                                       end_date=datetime.now(), workflow_ids=[workflow.id]))
    assert workflow_metric is not None
    assert workflow_metric[0].submissions is not None
    assert workflow_metric[0].submissions.aggregate.submitted is 1
