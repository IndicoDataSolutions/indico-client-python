import pytest
from indico.filters import FieldBlueprintFilter
from indico.queries.field_blueprints import (
    CreateFieldBlueprint,
    ExportFieldBlueprints,
    GetFieldBlueprints,
    ImportFieldBlueprints,
    ListFieldBlueprints,
)
from indico.types.field_blueprint import FieldBlueprint
from indico.types.jobs import Job


@pytest.fixture
def mock_field_blueprint_data():
    return {
        "id": 1,
        "uid": "test_uid",
        "name": "Test Field",
        "version": "1.0",
        "taskType": "GENAI_ANNOTATION",
        "description": "A test blueprint",
        "enabled": True,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "createdBy": 1,
        "updatedBy": 1,
        "tags": ["test"],
        "fieldConfig": {"some": "config"},
        "promptConfig": {"localization": "SEARCH"},
    }


def test_create_field_blueprint(mock_field_blueprint_data):
    blueprints = [mock_field_blueprint_data]
    query = CreateFieldBlueprint(blueprints)

    mock_response = {
        "data": {"createFieldBlueprint": {"blueprints": [mock_field_blueprint_data]}}
    }

    result = query.process_response(mock_response)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FieldBlueprint)
    assert result[0].uid == "test_uid"
    assert result[0].field_config["some"] == "config"
    assert result[0].prompt_config["localization"] == "SEARCH"


def test_get_field_blueprints(mock_field_blueprint_data):
    query = GetFieldBlueprints(ids=[1])

    mock_response = {
        "data": {
            "gallery": {"fieldBlueprint": {"blueprints": [mock_field_blueprint_data]}}
        }
    }

    result = query.process_response(mock_response)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FieldBlueprint)
    assert result[0].id == 1


def test_list_field_blueprints(mock_field_blueprint_data):
    query = ListFieldBlueprints(
        filters=FieldBlueprintFilter(
            field="field_blueprint.uid", op="eq", value="test_uid"
        )
    )

    mock_response = {
        "data": {
            "gallery": {
                "fieldBlueprint": {
                    "blueprintsPage": {
                        "fieldBlueprints": [mock_field_blueprint_data],
                        "cursor": "next",
                        "total": 1,
                    }
                }
            }
        }
    }

    result = query.process_response(mock_response)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], FieldBlueprint)
    # Ensure variables were set correctly
    assert query.variables["filters"] == {
        "field": "field_blueprint.uid",
        "op": "eq",
        "value": "test_uid",
    }


def test_export_field_blueprints_no_wait():
    query = ExportFieldBlueprints(wait=False)

    # Simulate the iterator for the request chain
    requests = query.requests()
    req = next(requests)

    mock_response = {"data": {"exportFieldBlueprints": {"jobId": "job_123"}}}

    job = req.process_response(mock_response)
    assert isinstance(job, Job)
    assert job.id == "job_123"


def test_import_field_blueprints_no_wait():
    query = ImportFieldBlueprints(storage_uri="blob://test", wait=False)

    requests = query.requests()
    req = next(requests)

    mock_response = {"data": {"importFieldBlueprints": {"jobId": "job_456"}}}

    job = req.process_response(mock_response)
    assert job.id == "job_456"


def test_nested_field_blueprints_filter():
    f1 = FieldBlueprintFilter(field="field_blueprint.uid", op="eq", value="1")
    f2 = FieldBlueprintFilter(op="eq", field="field_blueprint.uid", value="2")
    outer = FieldBlueprintFilter(op="or", filters=[f1, f2])

    query = ListFieldBlueprints(filters=outer)

    expected = {
        "op": "or",
        "filters": [
            {"field": "field_blueprint.uid", "op": "eq", "value": "1"},
            {"field": "field_blueprint.uid", "op": "eq", "value": "2"},
        ],
    }
    assert query.variables["filters"] == expected


def test_explicit_field_blueprints_filter():
    # Test fog-style explicit construction
    f1 = FieldBlueprintFilter(field="field_blueprint.uid", op="eq", value="1")
    f2 = FieldBlueprintFilter(field="field_blueprint.uid", op="eq", value="2")
    outer = FieldBlueprintFilter(op="or", filters=[f1, f2])

    query = ListFieldBlueprints(filters=outer)

    expected = {
        "op": "or",
        "filters": [
            {"field": "field_blueprint.uid", "op": "eq", "value": "1"},
            {"field": "field_blueprint.uid", "op": "eq", "value": "2"},
        ],
    }
    assert query.variables["filters"] == expected
