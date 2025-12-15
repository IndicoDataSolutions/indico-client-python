from indico.queries.submission_management import (
    GetSubmissionManagementFields,
    SubmissionManagementFieldsPage,
)


def test_get_submission_management_fields():
    response = {
        "data": {
            "submissionManagementFields": {
                "submissions": [
                    {
                        "id": 1,
                        "status": "COMPLETE",
                        "filesDeleted": False,
                        "retrieved": False,
                        "completedAt": None,
                        "fields": [{"id": 1, "formattedValue": "Value 1"}],
                        "inputFiles": [],
                    }
                ],
                "fieldInfo": [{"id": 1, "name": "Field 1"}],
                "cursor": "cursor",
                "total": 1,
            }
        }
    }

    query = GetSubmissionManagementFields(
        workflow_id=1,
        filters=[
            {"column": "status", "filter": {"value": "COMPLETE"}},
            {"column": "fieldId", "filter": {"value": "foo", "fieldId": 123}},
        ],
    )

    # Process the mock response
    result = query.process_response(response)

    assert isinstance(result, SubmissionManagementFieldsPage)
    assert result.total == 1
    assert result.submissions[0].id == 1

    # Verify variables match expectation
    assert query.variables["filters"] == [
        {"column": "status", "filter": {"value": "COMPLETE"}},
        {"column": "fieldId", "filter": {"value": "foo", "fieldId": 123}},
    ]
    assert query.variables["size"] == 100


def test_get_submission_management_fields_with_size_and_filter_obj():
    from indico.filters import SubmissionFieldFilter

    query = GetSubmissionManagementFields(
        workflow_id=1,
        size=50,
        filters=SubmissionFieldFilter(status="PENDING"),
    )
    assert query.variables["size"] == 50
    assert query.variables["filters"] == [
        {"column": "status", "filter": {"value": "PENDING"}}
    ]
