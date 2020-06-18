import pytest

from indico.filters import *


def test_submission_filter_and():
    filter = SubmissionFilter({"status": "COMPLETE"})
    filter.and_("status", "TRAINING")
    assert filter == {"AND": [{"status": "COMPLETE"}, {"status": "TRAINING"}]}


def test_submission_filter_or():
    filter = SubmissionFilter({"status": "COMPLETE"}, mode=FilterMode.OR)
    filter.or_("status", "TRAINING")
    assert filter == {"OR": [{"status": "COMPLETE"}, {"status": "TRAINING"}]}


def test_invalid_filter_column():
    with pytest.raises(ValueError):
        SubmissionFilter({"name": "test"})

    filter = SubmissionFilter({"status": "COMPLETE"})
    with pytest.raises(ValueError):
        filter.and_("name", "thing")

