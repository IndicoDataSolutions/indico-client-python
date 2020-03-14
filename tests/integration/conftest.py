import logging
import pytest
import os

from indico.config import IndicoConfig

logging.getLogger("indico").setLevel(logging.DEBUG)

def pytest_addoption(parser):
    parser.addoption(
        "--host", action="store", default="dev.indico.io", help="indico ipa host"
    )


@pytest.fixture(scope="module")
def indico(request):
    host = request.config.getoption("--host")
    os.environ["INDICO_HOST"] = host

