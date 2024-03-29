# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import TYPE_CHECKING

from indico.errors import IndicoInvalidConfigSetting

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Tuple, Union


class IndicoConfig:
    """
    Configuration for the IndicoClient.

    Args:
        host= (str, optional): Indico Platform hostname (eg mycluster.indico.io )
        api_token_path= (str, optional): Path to the Indico API token file indico_api_token.txt. Defaults to user's home directory. Ignored if api_token is provided.
        api_token= (str, optional): The actual text of the API Token. Takes precedence over api_token_path
        verify_ssl= (bool, optional): Whether to verify the host's SSL certificate. Default=True
        requests_params= (dict, optional): Dictionary of requests. Session parameters to set

    Returns:
        IndicoConfig object

    Raises:
        RuntimeError: If api_token_path does not exist.
    """

    def __init__(self, **kwargs: "Any"):
        self.host: str = os.environ["INDICO_HOST"]
        self.protocol: str = os.getenv("INDICO_PROTOCOL", "https")
        self.serializer: str = os.getenv("INDICO_SERIALIZER", "msgpack")
        self.api_token_path: Union[str, Path] = os.getenv(
            "INDICO_API_TOKEN_PATH", Path.home()
        )
        self.api_token: Optional[str] = os.getenv("INDICO_API_TOKEN")
        self.verify_ssl: bool = True
        self.requests_params: Optional[Dict[str, Any]] = None
        self._disable_cookie_domain: bool = False

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise IndicoInvalidConfigSetting(key)

        if not self.api_token:
            self.api_token_path, self.api_token = self._resolve_api_token()

    def _resolve_api_token(self) -> Tuple[Path, str]:
        path = self.api_token_path

        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            path = Path.home()
        if not path.is_file():
            path = path / "indico_api_token.txt"

        if not path.exists():
            raise RuntimeError(
                "Expected indico_api_token.txt in home directory, "
                "or provided as indicoio.config.api_token_path"
            )

        return path, path.read_text().strip()
