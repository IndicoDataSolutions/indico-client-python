from datetime import datetime

import pytest

from indico.errors import IndicoInputError
from indico.filters import DocumentReportFilter, Filter, SubmissionFilter, and_, or_


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
