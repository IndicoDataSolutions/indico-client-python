from datetime import datetime
from typing import List
import pandas as pd
from indico import IndicoConfig, IndicoClient
from indico.queries import ListWorkflows
from indico.queries.workflow_metrics import GetWorkflowMetrics
from indico.types.workflow_metrics import WorkflowMetrics, WorkflowMetricsOptions

"""Example 1: Fetch all metrics for a workflow"""
# Use your dataset's id to call it's associated workflow
dataset_id = 6826

my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

# Return a list of workflows for this dataset id or an empty list if there are none
workflows = client.call(ListWorkflows(dataset_ids=[dataset_id]))

# Fetch the metrics for an associated workflow.
if workflows:
    client = IndicoClient(config=my_config)
    workflow_metric: List[WorkflowMetrics] = \
        client.call(GetWorkflowMetrics(start_date=datetime(2021, 6, 28),
                                       end_date=datetime.now(), workflow_ids=[workflows[0].id]))
total_subs = workflow_metric[0].submissions.aggregate

print("There have been " + str(total_subs) + " for the workflow " + str(workflow_metric[0].workflow_id) + "!")

"""Example 2: Load selected metrics into a dataframe"""

df = pd.DataFrame([{"date": x.date, "submitted": x.submitted, "completed": x.completed,
                    "rejected": x.rejected_in_review} for x in workflow_metric[0].submissions.daily])

df["date"] = pd.to_datetime(df["date"])

idx_max = df.iloc[df["submitted"].idxmax()]

print(str(idx_max["date"]) + " was the day with the most submissions: " + str(idx_max["submitted"]))

""" Example 3: Retrieve only specific metrics."""
workflow_metric: List[WorkflowMetrics] = \
    client.call(GetWorkflowMetrics(options=[WorkflowMetricsOptions.STRAIGHT_THROUGH_PROCESSING],
                                   start_date=datetime(2021, 6, 28),
                                   end_date=datetime.now(), workflow_ids=[workflows[0].id]))
# Checking in the debugger shows that only this has straight_through_processing as an attribute.
stp = workflow_metric[0].straight_through_processing
