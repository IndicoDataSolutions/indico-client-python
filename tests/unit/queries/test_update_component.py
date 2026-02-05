import json

import pytest

from indico.errors import IndicoInputError
from indico.queries.workflow_components import (
    UpdateComponent,
    ValidateComponentUpdate,
    _UpdateComponent,
)
from indico.types.workflow import (
    ComponentToDeleteInfo,
    ComponentValidationResult,
    LinkToAddInfo,
    LinkToRemoveInfo,
    LinkToUpdateInfo,
)


class TestComponentValidationResultType:
    def test_component_validation_result_from_dict(self):
        data = {
            "valid": True,
            "componentsToDelete": [
                {
                    "id": 7,
                    "name": "Downstream Component",
                    "componentType": "MODEL_GROUP",
                    "modelGroupName": "Downstream Model Group",
                    "reason": "Downstream of removed filter link",
                }
            ],
            "linksToRemove": [
                {
                    "id": 3,
                    "headId": 5,
                    "tailId": 6,
                    "config": '{"filters": {"field": {"id": 100}}}',
                }
            ],
            "linksToUpdate": [
                {
                    "id": 4,
                    "headId": 5,
                    "tailId": 7,
                    "config": '{"filters": {"field": {"id": 101}}}',
                }
            ],
            "linksToAdd": [
                {
                    "headId": 5,
                    "tailId": 8,
                    "config": '{"filters": {"field": {"id": 102}}}',
                }
            ],
        }

        result = ComponentValidationResult(**data)

        assert result.valid is True
        assert len(result.components_to_delete) == 1
        assert len(result.links_to_remove) == 1
        assert len(result.links_to_update) == 1
        assert len(result.links_to_add) == 1

    def test_component_to_delete_info(self):
        data = {
            "id": 7,
            "name": "Test Component",
            "componentType": "MODEL_GROUP",
            "modelGroupName": "Test Model Group",
            "reason": "Test reason",
        }

        info = ComponentToDeleteInfo(**data)

        assert info.id == 7
        assert info.name == "Test Component"
        assert info.component_type == "MODEL_GROUP"
        assert info.model_group_name == "Test Model Group"
        assert info.reason == "Test reason"

    def test_link_to_remove_info(self):
        data = {
            "id": 3,
            "headId": 5,
            "tailId": 6,
            "config": '{"filters": {"field": {"id": 100}}}',
        }

        info = LinkToRemoveInfo(**data)

        assert info.id == 3
        assert info.head_id == 5
        assert info.tail_id == 6
        assert info.config == {"filters": {"field": {"id": 100}}}

    def test_link_to_update_info(self):
        data = {
            "id": 4,
            "headId": 5,
            "tailId": 7,
            "config": '{"filters": {}}',
        }

        info = LinkToUpdateInfo(**data)

        assert info.id == 4
        assert info.head_id == 5
        assert info.tail_id == 7

    def test_link_to_add_info(self):
        data = {
            "headId": 5,
            "tailId": 8,
            "config": '{"filters": {"passed": true}}',
        }

        info = LinkToAddInfo(**data)

        assert info.head_id == 5
        assert info.tail_id == 8
        assert info.config == {"filters": {"passed": True}}

    def test_empty_lists(self):
        data = {
            "valid": True,
            "componentsToDelete": [],
            "linksToRemove": [],
            "linksToUpdate": [],
            "linksToAdd": [],
        }

        result = ComponentValidationResult(**data)

        assert result.valid is True
        assert len(result.components_to_delete) == 0
        assert len(result.links_to_remove) == 0
        assert len(result.links_to_update) == 0
        assert len(result.links_to_add) == 0


class TestValidateComponentUpdateQuery:
    def test_query_variables(self):
        component_data = {"config": {"model_group_id": 1}}
        query = ValidateComponentUpdate(
            component_id=5,
            workflow_id=10,
            component=component_data,
        )

        variables = query.kwargs["json"]["variables"]

        assert variables["componentId"] == 5
        assert variables["workflowId"] == 10
        assert json.loads(variables["component"]) == component_data

    def test_process_response(self):
        query = ValidateComponentUpdate(
            component_id=5,
            workflow_id=10,
            component={"config": {}},
        )
        response = {
            "data": {
                "validateComponentUpdate": {
                    "valid": True,
                    "componentsToDelete": [],
                    "linksToRemove": [],
                    "linksToUpdate": [],
                    "linksToAdd": [],
                }
            }
        }

        result = query.process_response(response)

        assert isinstance(result, ComponentValidationResult)
        assert result.valid is True


class TestUpdateComponentMutation:
    def test_internal_mutation_variables(self):
        component_data = {"config": {"model_group_id": 1}}
        mutation = _UpdateComponent(
            component_id=5,
            workflow_id=10,
            component=component_data,
        )

        variables = mutation.kwargs["json"]["variables"]

        assert variables["componentId"] == 5
        assert variables["workflowId"] == 10
        assert json.loads(variables["component"]) == component_data

    def test_request_chain_without_auto_validate(self):
        component_data = {"config": {"model_group_id": 1}}
        chain = UpdateComponent(
            component_id=5,
            workflow_id=10,
            component=component_data,
            auto_validate=False,
        )

        requests = list(chain.requests())

        assert len(requests) == 1
        assert isinstance(requests[0], _UpdateComponent)

    def test_request_chain_with_auto_validate_valid(self):
        component_data = {"config": {"model_group_id": 1}}
        chain = UpdateComponent(
            component_id=5,
            workflow_id=10,
            component=component_data,
            auto_validate=True,
        )

        requests_iter = chain.requests()
        first_request = next(requests_iter)

        assert isinstance(first_request, ValidateComponentUpdate)

        chain.previous = ComponentValidationResult(
            valid=True,
            components_to_delete=[],
            links_to_remove=[],
            links_to_update=[],
            links_to_add=[],
        )

        second_request = next(requests_iter)

        assert isinstance(second_request, _UpdateComponent)

    def test_request_chain_with_auto_validate_invalid(self):
        component_data = {"config": {"model_group_id": 1}}
        chain = UpdateComponent(
            component_id=5,
            workflow_id=10,
            component=component_data,
            auto_validate=True,
        )

        requests_iter = chain.requests()
        next(requests_iter)

        chain.previous = ComponentValidationResult(
            valid=False,
            components_to_delete=[
                ComponentToDeleteInfo(
                    id=7,
                    name="Test",
                    component_type="MODEL_GROUP",
                    model_group_name="Test MG",
                    reason="Test reason",
                )
            ],
            links_to_remove=[],
            links_to_update=[],
            links_to_add=[],
        )

        with pytest.raises(IndicoInputError) as exc_info:
            next(requests_iter)

        assert "Component update validation failed" in str(exc_info.value)
        assert "Components to delete: 1" in str(exc_info.value)
