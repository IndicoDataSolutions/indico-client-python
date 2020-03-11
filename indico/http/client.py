
import logging
import requests
from collections import defaultdict
from typing import Union
from indico.config import IndicoConfig
from indico.http.serialization import deserialize
from indico.errors import IndicoRequestError
from indico.client.request import HTTPRequest

logger = logging.getLogger(__file__)


class HTTPClient:
    def __init__(self, config: IndicoConfig=None):
        self.config = config
        self.base_url = (
            f"{self.config.protocol}://{self.config.host}"
        )

        self.request_session = requests.Session()
        self.get_short_lived_access_token()

    def post(self, *args, json: Union[dict, list]=None, **kwargs):
        return self._make_request("post", *args, json=json, **kwargs)

    def get(self, *args, params: dict=None, **kwargs):
        return self._make_request("post", *args, params=params, **kwargs)

    def get_short_lived_access_token(self):
        return self.post(
            "/auth/users/refresh_token",
            headers={"Authorization": f"Bearer {self.config.api_token}"},
        )

    def execute_request(self, request: HTTPRequest):
        return request.process_response(self._make_request(method=request.method.value.lower(), path=request.path, json=request.data))

    def _make_request(self, method: str, path: str, headers: dict=None, **request_kwargs):
        logger.debug(
            f"[{method}] {path}\n\t Headers: {headers}\n\tRequest Args:{request_kwargs}"
        )

        response = getattr(self.request_session, method)(
            f"{self.base_url}{path}", headers=headers, **request_kwargs
        )

        # code, api_response =
        content = deserialize(response)

        if response.status_code >= 400:
            if isinstance(content, dict):
                error = (
                    f"{content.pop('error_type', 'Unknown Error')}, "
                    f"{content.pop('message', '')}"
                )
                extras = content
            else:
                error = content
                extras = None

            raise IndicoRequestError(
                error=error, code=response.status_code, extras=extras
            )

        return content