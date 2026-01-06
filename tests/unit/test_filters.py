from datetime import datetime

import pytest

from indico.errors import IndicoInputError
from indico.filters import (
    DocumentReportFilter,
    FieldBlueprintFilter,
    Filter,
    SubmissionFieldFilter,
    SubmissionFilter,
    and_,
    or_,
)


def test_filter():
    with pytest.raises(IndicoInputError):
        Filter()
    f = Filter(key="value")
    assert dict(f) == {"key": "value"}
    f = Filter(key="value", key2="value2")
    assert dict(f) == {"AND": [{"key": "value", "key2": "value2"}]}


@pytest.mark.parametrize("fn,key", [(and_, "AND"), (or_, "OR")])
def test_builder(fn, key):
    f = Filter(key="value")
    f2 = Filter(key2="value2")
    assert fn(f) == {key: [f]}
    assert fn(f, f2) == {key: [f, f2]}


def test_submission_filter():
    f = SubmissionFilter(status="complete")
    assert dict(f) == {"status": "COMPLETE"}


def test_doc_report_filter():
    todays_date = datetime.now().strftime("%Y-%m-%d")

    filter_opts = DocumentReportFilter(created_at_start_date=datetime(2021, 7, 1))
    assert filter_opts["createdAt"]["to"] == todays_date
    with pytest.raises(IndicoInputError):
        DocumentReportFilter(created_at_end_date=datetime.now())

    filter_opts = DocumentReportFilter(updated_at_start_date=datetime(2021, 8, 1))
    assert filter_opts["updatedAt"]["to"] == todays_date
    with pytest.raises(IndicoInputError):
        DocumentReportFilter(updated_at_end_date=datetime.now())


def test_field_blueprint_filter():
    f = FieldBlueprintFilter(field="uid", op="eq", value="123")
    # Verify it acts as a dict
    assert isinstance(f, dict)
    # Verify content
    assert f == {"field": "uid", "op": "eq", "value": "123"}

    # Test invalid option
    with pytest.raises(TypeError):
        FieldBlueprintFilter(invalid_opt="something")


def test_submission_field_filter():
    # Test standard initialization
    f = SubmissionFieldFilter(field_id=123)
    assert isinstance(f, list)
    assert len(f) == 1
    assert {"column": "fieldId", "filter": {"fieldId": 123}} in f

    # Test standard columns
    f = SubmissionFieldFilter(status="COMPLETE", created_at="2023-01-01")
    assert len(f) == 2
    assert {"column": "status", "filter": {"value": "COMPLETE"}} in f
    assert {"column": "createdAt", "filter": {"value": "2023-01-01"}} in f

    # Test custom fields initialization
    f = SubmissionFieldFilter(custom_fields={456: "some_value", 789: "other_value"})
    assert len(f) == 2
    assert {
        "column": "fieldId",
        "filter": {"fieldId": 456, "value": "some_value"},
    } in f
    assert {
        "column": "fieldId",
        "filter": {"fieldId": 789, "value": "other_value"},
    } in f

    # Test combined
    f = SubmissionFieldFilter(field_id=123, custom_fields={456: "val"})
    assert len(f) == 2
    assert {"column": "fieldId", "filter": {"fieldId": 123}} in f
    assert {
        "column": "fieldId",
        "filter": {"fieldId": 456, "value": "val"},
    } in f


def test_field_blueprint_filter_nested():
    # Test nested filters
    f1 = FieldBlueprintFilter(field="field_blueprint.tags", op="in", value=["fixture"])
    f_outer = FieldBlueprintFilter(op="and", filters=[f1])

    assert f_outer == {
        "op": "and",
        "filters": [
            {"field": "field_blueprint.tags", "op": "in", "value": ["fixture"]}
        ],
    }
