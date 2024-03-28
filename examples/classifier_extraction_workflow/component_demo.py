"""
Example for building a classifier -> extraction model workflow

Note the dataset in this example was built from data/swaps_with_class.csv
"""

from datetime import datetime

from component_links import get_component_link_id
from config import CLASSIFIER_CLASSES, DATASET_ID, INDICO_CLIENT
from queries import get_user_ids

from indico import IndicoClient, IndicoConfig
from indico.queries import (
    AddLinkClassificationComponent,
    AddModelGroupComponent,
    CreateWorkflow,
    GetDataset,
)
from indico.types import ModelTaskType, NewLabelsetArguments, NewQuestionnaireArguments

HOST = "indico.host"
API_TOKEN_PATH = "/path/to/indico_api_token.txt"

INDICO_CONFIG = IndicoConfig(host=HOST, api_token_path=API_TOKEN_PATH)
INDICO_CLIENT = IndicoClient(config=INDICO_CONFIG)
DATASET_ID = int("<your dataset id>")

CLASSIFIER_CLASSES = ["class A", "class B"]

timestamp = datetime.now()

dataset = INDICO_CLIENT.call(GetDataset(DATASET_ID))
user_ids = get_user_ids(DATASET_ID)
source_col_id = dataset.datacolumn_by_name("text").id

workflow_name = f"Test Classification -> Extraction {timestamp}"

# Create workflow canvas
workflow = INDICO_CLIENT.call(CreateWorkflow(DATASET_ID, workflow_name))

# save node_id to attach classifier to
head_node_id = workflow.component_by_type("INPUT_OCR_EXTRACTION").id

# Create classifier model and attach to OCR EXTRACTION
classifier_name = f"Classifier {timestamp}"
new_labelset_args = {
    "datacolumn_id": source_col_id,
    "name": classifier_name,
    "num_labelers_required": 1,
    "task_type": ModelTaskType.CLASSIFICATION,
    "target_names": CLASSIFIER_CLASSES,
}
questionnaire_args = {
    "instructions": "Click things",
    "show_predictions": True,
    "users": user_ids,
}

classifier_wf = INDICO_CLIENT.call(
    AddModelGroupComponent(
        dataset_id=DATASET_ID,
        workflow_id=workflow.id,
        name=classifier_name,
        new_labelset_args=NewLabelsetArguments(**new_labelset_args),
        new_questionnaire_args=NewQuestionnaireArguments(**questionnaire_args),
        source_column_id=source_col_id,
        after_component_id=head_node_id,
    )
)

# Get classifier node to attach filter to
classifier_component = classifier_wf.model_group_by_name(classifier_name)

filtered_classes = [[c] for c in CLASSIFIER_CLASSES]
# set up label filter for extraction models
extraction_filter_wf = INDICO_CLIENT.call(
    AddLinkClassificationComponent(
        workflow_id=workflow.id,
        model_group_id=classifier_component.model_group.id,
        after_component_id=classifier_component.id,
        filtered_classes=filtered_classes,
        labels=None,
    )
)

# Note that connecting the extraction models to the linked classifeier filter
# requires a component link id as opposed to a stndard component id
# class_a_link_id = extraction_filter_wf.component_link_by_filter_classes(["class A"]).id
# class_b_link_id = extraction_filter_wf.component_link_by_filter_classes(["class B"]).id
class_a_link_id = get_component_link_id(workflow.id, ["class A"])
class_b_link_id = get_component_link_id(workflow.id, ["class B"])

# create extraction model 1
extraction_model_1_name = f"Extraction 1 {timestamp}"
new_labelset_args = {
    "datacolumn_id": source_col_id,
    "name": extraction_model_1_name,
    "num_labelers_required": 1,
    "task_type": ModelTaskType.ANNOTATION,
    "target_names": ["extraction class 1"],
}
extraction_model_1 = INDICO_CLIENT.call(
    AddModelGroupComponent(
        dataset_id=DATASET_ID,
        workflow_id=workflow.id,
        name=extraction_model_1_name,
        source_column_id=source_col_id,
        after_link_id=class_a_link_id,
        new_labelset_args=NewLabelsetArguments(**new_labelset_args),
        new_questionnaire_args=NewQuestionnaireArguments(**questionnaire_args),
    )
)

# create extraction model 2
extraction_model_2_name = f"Extraction 2 {timestamp}"
new_labelset_args = {
    "datacolumn_id": source_col_id,
    "name": extraction_model_2_name,
    "num_labelers_required": 1,
    "task_type": ModelTaskType.ANNOTATION,
    "target_names": ["extraction class 2"],
}
extraction_model_2 = INDICO_CLIENT.call(
    AddModelGroupComponent(
        dataset_id=DATASET_ID,
        workflow_id=workflow.id,
        name=extraction_model_2_name,
        source_column_id=source_col_id,
        after_link_id=class_b_link_id,
        new_labelset_args=NewLabelsetArguments(**new_labelset_args),
        new_questionnaire_args=NewQuestionnaireArguments(**questionnaire_args),
    )
)
