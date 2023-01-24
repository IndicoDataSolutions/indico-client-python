import logging
import pytest
import os

logging.getLogger("indico").setLevel(logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption(
        "--host", action="store", default="dev-ci.us-east-2.indico-dev.indico.io", help="indico ipa host"
    )


@pytest.fixture(scope="module")
def indico(request):
    host = request.config.getoption("--host")
    os.environ["INDICO_HOST"] = host
