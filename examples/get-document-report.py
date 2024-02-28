from datetime import datetime
from typing import List
from indico import IndicoConfig, IndicoClient
from indico.queries.document_report import GetDocumentReport
from indico.types.document_report import DocumentReport
from indico.filters import DocumentReportFilter


"""Example 1: Document Report for a date range and page through the results"""

my_config = IndicoConfig(
    host="try.indico.io", api_token_path="./path/to/indico_api_token.txt"
)

client = IndicoClient(config=my_config)

filter_opts = DocumentReportFilter(
    created_at_start_date=datetime(2021, 7, 1), created_at_end_date=datetime.now()
)

document_report: List[DocumentReport] = []
for page in client.paginate(GetDocumentReport(filters=filter_opts, limit=1000)):
    document_report.extend(page)
