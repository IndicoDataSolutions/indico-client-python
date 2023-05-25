from datetime import datetime
from typing import List

from indico import IndicoClient
from indico.queries.document_report import GetDocumentReport
from indico.types.document_report import DocumentReport
from indico.filters import DocumentReportFilter


def test_fetch_docs(indico):
    client = IndicoClient()

    document_report: List[DocumentReport] = client.call(GetDocumentReport())
    assert document_report is not None
    assert len(document_report) > 0
    input_files = [f for dr in document_report for f in dr.input_files]
    num_pages_check = [isinstance(f.num_pages, int) for f in input_files if f.num_pages]
    if num_pages_check:
        assert all(num_pages_check)
    file_size_check = [isinstance(f.file_size, int) for f in input_files if f.file_size]
    if file_size_check:
        assert all(file_size_check)
    assert all([isinstance(f.id, int) for f in input_files])
    assert all([isinstance(f.submission_id, int) for f in input_files])
    assert [f.filename for f in input_files]


def test_fetch_docs_limit(indico):
    client = IndicoClient()
    filter_opts = DocumentReportFilter(
        created_at_start_date=datetime(2021, 7, 1), created_at_end_date=datetime.now()
    )
    document_report: List[DocumentReport] = client.call(
        GetDocumentReport(filters=filter_opts, limit=5)
    )
    assert document_report is not None
    assert len(document_report) > 0
    assert len(document_report) <= 5


def test_pagination(indico):
    client = IndicoClient()
    document_report: List[DocumentReport] = []
    num_pages_to_check = 5
    for i, page in enumerate(client.paginate(GetDocumentReport(limit=10))):
        document_report.extend(page)
        if i > num_pages_to_check:
            break
    assert document_report is not None
    assert len(document_report) > 0


def test_all_submissions(indico):
    """
    This test is expected to fail unless user has ALL_SUBMISSION_LOGs scope
    """
    client = IndicoClient()
    page = next(client.paginate(GetDocumentReport(limit=1000, all_submissions=True)))
    assert page is not None
