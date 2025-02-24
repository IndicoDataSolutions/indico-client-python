import time
from datetime import datetime
from pathlib import Path
from typing import List

import pytest

from indico.client import IndicoClient
from indico.queries import (
    JobStatus,
    RetrieveStorageObject,
    SubmitReview,
    UpdateWorkflowSettings,
    WaitForSubmissions,
    WorkflowSubmission,
)
from indico.queries.workflow_metrics import GetWorkflowMetrics
from indico.types.workflow_metrics import WorkflowMetrics, WorkflowMetricsOptions

from ..data.datasets import *  # noqa
from ..data.datasets import PUBLIC_URL


@pytest.fixture
def workflow(
    indico, org_annotate_dataset, org_annotate_workflow, org_annotate_model_group
):
    client = IndicoClient()

    wf = client.call(
        UpdateWorkflowSettings(
            org_annotate_workflow.id, enable_review=True, enable_auto_review=True
        )
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
    job = client.call(SubmitReview(sub.id, changes=changes, force_complete=True))
    job = client.call(JobStatus(job.id))
    submission = client.call(WaitForSubmissions([sub.id]))[0]
    assert submission.status == "COMPLETE"

    # metrics in the cluster are updated every 5 minutes
    time.sleep(300)
    return wf


def test_fetch_metrics(indico, workflow):
    client = IndicoClient()
    workflow_metric: List[WorkflowMetrics] = client.call(
        GetWorkflowMetrics(
            options=[WorkflowMetricsOptions.SUBMISSIONS],
            start_date=datetime.now(),
            end_date=datetime.now(),
            workflow_ids=[workflow.id],
        )
    )
    assert workflow_metric is not None
    assert workflow_metric[0].submissions is not None
    assert workflow_metric[0].submissions.aggregate.submitted > 0


def test_fetch_metrics_queue(indico, workflow):
    client = IndicoClient()
    workflow_metric: List[WorkflowMetrics] = client.call(
        GetWorkflowMetrics(
            options=[WorkflowMetricsOptions.REVIEW],
            start_date=datetime.now(),
            end_date=datetime.now(),
            workflow_ids=[workflow.id],
        )
    )
    assert workflow_metric is not None
    assert workflow_metric[0].queues is not None
    assert len(workflow_metric[0].queues.daily_cumulative) > 0
