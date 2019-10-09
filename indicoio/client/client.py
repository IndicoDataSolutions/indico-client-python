import requests

from indicoio import config
from indicoio.errors import IndicoIPARequestError
from indicoio.client.serialization import deserialize


class IndicoClient(object):
    def __init__(
        self,
        host=config.host,
        protocol=config.url_protocol,
        serializer=config.serializer,
        token_path=None,
    ):
        self.base_url = f"{protocol}://{host}"
        self.serializer = serializer
        self.api_token = config.resolve_api_token(path=token_path)
        self.short_lived_access_token = None
        self.request_session = requests.Session()
        self.get_short_lived_access_token()

    def get_short_lived_access_token(self):
        return self.post(
            "/auth/users/refresh_token",
            headers={f"Authorization": "Bearer {self.api_token}"},
        )

    def post(self, *args, payload=None, **kwargs):
        return self._make_request("post", *args, payload=payload, **kwargs)

    def get(self, *args, params=None, **kwargs):
        return self._make_request("post", *args, params=params, **kwargs)

    def _make_request(self, method, path, headers=None, **request_kwargs):
        response = getattr(self.request_session, method)(
            f"{self.base_url}{path}", **request_kwargs
        )

        # code, api_response =
        content = deserialize(response)

        if response.status_code >= 400:
            if isinstance(content, dict):
                error = content.pop("message", content.pop("error"))
                extras = content
            else:
                error = content
                extras = None

            raise IndicoIPARequestError(
                error=error, code=response.status_code, extras=extras
            )

        return content
