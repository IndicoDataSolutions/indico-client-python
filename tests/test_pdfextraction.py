import pytest

from pathlib import Path
from indicoio.api.prebuilt import IndicoApi


@pytest.fixture
def indicoapi(request):
    return IndicoApi(config_options={"host": request.config.getoption("--host")})


def test_pdf_extraction_url(indicoapi):
    results = indicoapi.pdf_extraction(["http://www.pdf995.com/samples/pdf.pdf"])
    assert isinstance(results, list)
    assert isinstance(results[0], dict)
    for field in ("metadata", "pages"):
        assert field in results[0]


def test_pdf_extraction_file(indicoapi):
    path = Path(__file__).parent / "data" / "mock.pdf"
    results = indicoapi.pdf_extraction([path])
    assert isinstance(results, list)
    assert isinstance(results[0], dict)
    for field in ("metadata", "pages"):
        assert field in results[0]
