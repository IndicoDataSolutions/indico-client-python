import requests
import logging

from indicoio import config
from indicoio.errors import IndicoRequestError
from indicoio.client.serialization import deserialize

logger = logging.getLogger(__file__)


class RequestProxy(object):
    default_config_options = dict(
        host=config.host,
        protocol=config.url_protocol,
        serializer=config.serializer,
        short_lived_access_token=None,
        request_session=None,
        token_path=None,
    )

    def __init__(self, config_options=None):
        config_options = {**self.default_config_options, **(config_options or {})}

        self.base_url = f"{config_options['protocol']}://{config_options['host']}"
        self.serializer = config_options["serializer"]
        self.api_token = config.resolve_api_token(path=config_options["token_path"])
        self.request_session = config_options["request_session"] or requests.Session()

    def post(self, *args, json=None, **kwargs):
        return self._make_request("post", *args, json=json, **kwargs)

    def get(self, *args, params=None, **kwargs):
        return self._make_request("post", *args, params=params, **kwargs)

    def get_short_lived_access_token(self):
        return self.post(
            "/auth/users/refresh_token",
            headers={"Authorization": f"Bearer {self.api_token}"},
        )

    def _make_request(self, method, path, headers=None, **request_kwargs):
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

