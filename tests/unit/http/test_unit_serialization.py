import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from indico.errors import IndicoDecodingError
from indico.http.serialization import aio_deserialize, deserialize


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

        response_mock.headers = {"content-type": f"{mime}{charset}"}
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


def test_deserialize_octet(mock_loader):
    response = mock_loader("application/octet-stream", "")
    content = deserialize(response)

    assert isinstance(content, bytes)


def test_deserialize_pdf(mock_loader):
    response = mock_loader("application/pdf", "")
    content = deserialize(response)

    assert isinstance(content, bytes)


def test_deserialize_gzip(mock_loader):
    response = mock_loader("application/gzip", "")
    content = deserialize(response)

    assert isinstance(content, bytes)


def test_deserialize_csv(mock_loader):
    response = mock_loader("text/csv", "")
    content = deserialize(response)

    assert isinstance(content, str)


def test_deserialize_xls(mock_loader):
    response = mock_loader("application/xls", "")
    content = deserialize(response)

    assert isinstance(content, bytes)


def test_deserialize_unknown(mock_loader):
    response = mock_loader("unknown", "")
    try:
        logging.getLogger("indicoio.client.serialization").setLevel(logging.CRITICAL)
        deserialize(response)
    except Exception as e:
        assert isinstance(e, IndicoDecodingError)
    finally:
        logging.getLogger("indicoio.client.serialization").setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_deserialize_same_result_as_deserialize(mock_loader):
    response = mock_loader("application/json", "utf-8")
    sync_result = deserialize(response)
    async_result = await aio_deserialize(response)
    assert sync_result == async_result
