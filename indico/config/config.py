from os import getenv
from pathlib import Path
from indico.errors import IndicoInvalidConfigSetting

class IndicoConfig():
    """
    Configuration for indico client 

    Support setting configuration using environment variables or directly as keywords argument of this class
    """
    host: str = getenv("INDICO_HOST", "app.indico.io")
    url_protocol: str = getenv("INDICO_PROTOCOL", "https")
    serializer: str = getenv("INDICO_SERIALIZER", "msgpack")
    api_token_path: str = getenv("INDICO_API_TOKEN_PATH", Path.home()) 

    def __init__(self, **kwargs):
        for key,value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise IndicoInvalidConfigSetting(key)
        self.api_token_path, self.api_token = self._resolve_api_token()

    def _resolve_api_token(self):
        path = self.api_token_path
        if path is None:
            path = "."
        if not isinstance(path, Path):
            path = Path(path)
        if not path.exists():
            path = Path.home()
        if not path.is_file():
            path = path / "indico_api_token.txt"

        if not path.exists():
            raise RuntimeError(
                "Expected indico_api_token.txt in current directory, home directory, "
                "or provided as indicoio.config.token_path"
            )

        with path.open("r") as f:
            return path, f.read().strip()


class RequestConfigMixin(object):
    def __init__(self, config: IndicoConfig=None):
        if not config:
            config = IndicoConfig()
        self.config_options = config
