import pytest

from indico.errors import IndicoInputError
from indico.filters import Filter, SubmissionFilter, and_, or_


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
