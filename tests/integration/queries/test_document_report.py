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
    assert isinstance(document_report[0].input_files[0].num_pages, int)
    assert isinstance(document_report[0].input_files[0].file_size, int)
    assert isinstance(document_report[0].input_files[0].id, int)
    assert isinstance(document_report[0].input_files[0].submission_id, int)
    assert document_report[0].input_files[0].filename


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
    for page in client.paginate(GetDocumentReport(limit=10)):
        document_report.extend(page)
    assert document_report is not None
    assert len(document_report) > 0

def test_all_submissions(indico):
    client = IndicoClient()
    document_report: List[DocumentReport] = []
    page = next(client.paginate(GetDocumentReport(limit=1000, all_submissions=True)))
    assert page is not None
