from datetime import datetime

import pytest

from indico.client import IndicoClient
from indico.filters import DateRangeFilter, SubmissionFilter, SubmissionReviewFilter
from indico.queries import GetReviews, ListSubmissions
from indico.types import SubmissionReviewFull


def test_list_submissions(indico):
    client = IndicoClient()

    subs = client.call(ListSubmissions(limit=10))
    assert len(subs) == 10


def test_list_submissions_filter_filetype(indico):
    client = IndicoClient()

    subs = client.call(
        ListSubmissions(filters=SubmissionFilter(file_type=["PDF"]), limit=10)
    )
    assert len(subs) > 0
    for sub in subs:
        sub_filetype = sub.input_filename.split(".")[-1].upper()
        assert sub_filetype == "PDF" or sub_filetype.lower() == sub.input_filename


@pytest.mark.parametrize(
    "_input_filename, _should_contain",
    [("pdf", True), ("randomstring", False)],
)
def test_list_submissions_filter_filename(indico, _input_filename, _should_contain):
    client = IndicoClient()

    subs = client.call(
        ListSubmissions(
            filters=SubmissionFilter(input_filename=_input_filename), limit=10
        )
    )
    for sub in subs:
        assert (_input_filename in sub.input_filename) == _should_contain


def test_list_submissions_filter_reviews(indico):
    client = IndicoClient()

    review_filter = SubmissionReviewFilter(rejected=False)

    subs = client.call(
        ListSubmissions(filters=SubmissionFilter(reviews=review_filter), limit=10)
    )
    assert len(subs) >= 0


def test_list_submissions_filter_reviews_in_progress(indico):
    client = IndicoClient()

    subs = client.call(
        ListSubmissions(filters=SubmissionFilter(review_in_progress=False), limit=10)
    )
    assert len(subs) > 0


def test_list_submissions_filter_created_at(indico):
    client = IndicoClient()

    date_filter = DateRangeFilter(
        filter_from=datetime(year=2020, month=2, day=2).strftime("%Y-%m-%d"),
        filter_to=datetime.now().strftime("%Y-%m-%d"),
    )
    subs = client.call(
        ListSubmissions(filters=SubmissionFilter(created_at=date_filter), limit=10)
    )
    assert len(subs) > 0
    subs = client.call(
        ListSubmissions(filters=SubmissionFilter(updated_at=date_filter), limit=10)
    )
    assert len(subs) > 0


def test_get_reviews(indico):
    client = IndicoClient()

    subs = client.call(ListSubmissions(limit=10))
    assert len(subs) > 0
    for sub in subs:
        reviews = client.call(GetReviews(sub.id))
        for review in reviews:
            assert isinstance(review, SubmissionReviewFull)
            if not review.rejected:
                assert isinstance(review.changes, (list, dict))
