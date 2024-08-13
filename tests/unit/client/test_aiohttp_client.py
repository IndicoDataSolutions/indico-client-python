from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from indico.client import AIOHTTPClient
from indico.config import IndicoConfig


@pytest.fixture
async def aiohttp_client():
    config = IndicoConfig(protocol="https", host="example.com", api_token="dummy_token")
    client = AIOHTTPClient(config=config)
    yield client
    await client.request_session.close()


@pytest.mark.asyncio
async def test_handle_files_correct_filename(aiohttp_client):
    file_path = Path("/tmp/testfile.txt")

    request_kwargs = {"files": [file_path]}

    with patch("pathlib.Path.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value = MagicMock()
        with aiohttp_client._handle_files(request_kwargs) as file_args:
            assert len(file_args) == 1
            for arg in file_args:
                fields = arg._fields
                for field in fields:
                    field_dict = field[0]
                    filename = field_dict.get("filename")
                    assert filename == "testfile.txt"
    await aiohttp_client.request_session.close()
