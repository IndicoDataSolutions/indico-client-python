from unittest.mock import MagicMock
from pathlib import Path
import logging

import pytest

from indicoio.client.serialization import deserialize
from indicoio.errors import IndicoDecodingError


@pytest.fixture(scope="function")
def mock_loader():
    def _mock_loader(mime, charset):
        path = (
            Path(__file__).parent
            / "mocked_data"
            / f"{mime.replace('/', '_')}_{charset}"
        )

        response_mock = MagicMock()

        if charset:
            charset = f"; charset={charset}"

        response_mock.headers = {"Content-Type": f"{mime}{charset}"}
        with open(path, "rb") as f:
            content = f.read()
        response_mock.content = content
        return response_mock

    return _mock_loader


def test_deserialize_text(mock_loader):
    response = mock_loader("text/html", "ISO-8859-1")
    content = deserialize(response)

    assert isinstance(content, str)


def test_deserialize_json(mock_loader):
    response = mock_loader("application/json", "utf-8")
    content = deserialize(response)

    assert isinstance(content, dict)


def test_deserialize_msgpack(mock_loader):
    response = mock_loader("application/msgpack", "")
    content = deserialize(response)

    assert isinstance(content, dict)


def test_deserialize_unknown(mock_loader):
    response = mock_loader("unknown", "")
    try:
        logging.getLogger("indicoio.client.serialization").setLevel(logging.CRITICAL)
        deserialize(response)
    except Exception as e:
        assert isinstance(e, IndicoDecodingError)
    finally:
        logging.getLogger("indicoio.client.serialization").setLevel(logging.DEBUG)
