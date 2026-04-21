import pytest

from indico.errors import IndicoInputError
from indico.queries import CancelSubmissions
from indico.types import SubmissionCancellationResult


def test_cancel_submissions_requires_ids() -> None:
    with pytest.raises(IndicoInputError, match="must specify submission ids"):
        CancelSubmissions([])


def test_cancel_submissions_rejects_duplicate_ids() -> None:
    with pytest.raises(IndicoInputError, match="duplicate submission ids"):
        CancelSubmissions([1, 1])


def test_cancel_submissions_process_response() -> None:
    request = CancelSubmissions([1, 2])
    result = request.process_response(
        {
            "data": {
                "cancelSubmissions": {
                    "cancelled": [1],
                    "skipped": [{"submissionId": 2, "reason": "already terminal"}],
                }
            }
        }
    )

    assert isinstance(result, SubmissionCancellationResult)
    assert result.cancelled == [1]
    assert len(result.skipped) == 1
    assert result.skipped[0].submission_id == 2
    assert result.skipped[0].reason == "already terminal"
