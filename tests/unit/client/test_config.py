import os
from unittest import mock
from indico.config import IndicoConfig


@mock.patch.dict(os.environ, {"INDICO_API_TOKEN": "ENV_TOKEN_YAY"})
def test_api_token_env_variable():
    config = IndicoConfig()
    assert config.api_token == "ENV_TOKEN_YAY"
