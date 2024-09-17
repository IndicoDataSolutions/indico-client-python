import logging
import os

import pytest

from indico.client import IndicoClient
from indico.queries.datasets import GetAvailableOcrEngines

from .data.async_datasets import *
from .data.datasets import *

logging.getLogger("indico").setLevel(logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption(
        "--host",
        action="store",
        default="dev-ci.us-east-2.indico-dev.indico.io",
        help="indico ipa host",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "ocr(ocr_engine): skip test if this OCR engine isn't available on the cluster",
    )


@pytest.fixture(scope="module")
def indico(request):
    host = request.config.getoption("--host")
    os.environ["INDICO_HOST"] = host


@pytest.fixture(autouse=True)
def skip_by_ocr(request):
    client = IndicoClient()
    ocr_engines = [e.name for e in client.call(GetAvailableOcrEngines())]
    if request.node.get_closest_marker("ocr"):
        ocr_engine = request.node.get_closest_marker("ocr").args[0].upper()
        if ocr_engine not in ocr_engines:
            pytest.skip(
                "skipped because cluster does not support OCR engine {}".format(
                    ocr_engine
                )
            )
