from typing import Tuple
from indico.client import IndicoClient
from indico.queries import DeleteWorkflowComponent, GetWorkflow, workflow
from indico.types import ModelGroup, WorkflowComponent

from ..data.datasets import *  # noqa

def test_delete_workflow_component(indico, airlines_dataset, airlines_workflow, airlines_model_group: ModelGroup):
    client = IndicoClient()
    # get workflow that includes mg component
    wf = client.call(GetWorkflow(workflow_id=airlines_workflow.id))
    num_components = len(wf.components)
    num_links = len(wf.component_links)
    mg_comp_id = next(c.id for c in wf.components if c.component_type == 'MODEL_GROUP')
    wf = client.call(DeleteWorkflowComponent(workflow_id=airlines_workflow.id, component_id=mg_comp_id))
    assert len(wf.components) == num_components - 1
    assert mg_comp_id not in {c.id for c in wf.components}
    assert len(wf.component_links) == num_links - 1
