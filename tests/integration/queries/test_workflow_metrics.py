import json

import pytest
from indico.client import IndicoClient
from indico.queries import JobStatus, RetrieveStorageObject
from indico.types.workflow_metrics import WorkflowMetric, WorkflowMetricsOptions
from indico.queries.workflow_metrics import GetWorkflowMetrics
from datetime import datetime


def test_fetch_metrics(indico):
    client = IndicoClient()
    workflow_metric: WorkflowMetric = client.call(GetWorkflowMetrics([WorkflowMetricsOptions.ITEMS_SUBMITTED],
                                                                  datetime.now(), [11602]))
    assert workflow_metric is not None
    #assert len(user_summary.app_roles) > 0


