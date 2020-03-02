import logging
import pytest

from indicoio.api import Indico

logging.getLogger("indicoio").setLevel(logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption(
        "--host", action="store", default="dev.indico.io", help="indico ipa host"
    )


@pytest.fixture(scope="module")
def indico(request):
    host = request.config.getoption("--host")
    return Indico(config_options={"host": host})
