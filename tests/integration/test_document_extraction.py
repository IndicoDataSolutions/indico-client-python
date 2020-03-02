import pytest

from pathlib import Path
from indicoio.api.prebuilt import IndicoApi


@pytest.fixture
def indicoapi(request):
    return IndicoApi(config_options={"host": request.config.getoption("--host")})

def test_document_extraction_file(indicoapi):
    path = Path(__file__).parent / "data" / "mock.pdf"
    results = indicoapi.document_extraction(data=[path])
    assert isinstance(results, list)
    assert isinstance(results[0], dict)
    for field in ("page_num", "size", "doc_offset", "image", "text"):
        for page in results[0]['pages']:
            assert page[field] is not None
