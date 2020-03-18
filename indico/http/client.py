
import logging
import requests
import http.cookiejar
from pathlib import Path
from contextlib import contextmanager
from collections import defaultdict
from typing import Union
from indico.config import IndicoConfig
from indico.http.serialization import deserialize
from indico.errors import IndicoRequestError
from indico.client.request import HTTPRequest
from requests import Response

logger = logging.getLogger(__file__)

class CookiePolicyOverride(http.cookiejar.DefaultCookiePolicy):
    def set_ok(self, cookie, request):
        return True

class HTTPClient:
    def __init__(self, config: IndicoConfig=None):
        self.config = config
        self.base_url = (
            f"{self.config.protocol}://{self.config.host}"
        )

        self.request_session = requests.Session()
        self.request_session.cookies.set_policy(CookiePolicyOverride())
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
        return request.process_response(self._make_request(method=request.method.value.lower(), path=request.path, **request.kwargs))

    @contextmanager
    def _handle_files(self, req_kwargs):
        files = []
        file_arg = {}
        if "files" in req_kwargs:
            for filepath in req_kwargs["files"]:
                path = Path(filepath)
                fd = path.open("rb")
                files.append(fd)
                file_arg[path.stem] = fd
            req_kwargs["files"] = file_arg
        yield

        if files:
            [f.close() for f in files]

    def _make_request(self, method: str, path: str, headers: dict=None,  **request_kwargs):
        logger.debug(
            f"[{method}] {path}\n\t Headers: {headers}\n\tRequest Args:{request_kwargs}"
        )
        with self._handle_files(request_kwargs):
            response = getattr(self.request_session, method)(
                f"{self.base_url}{path}", headers=headers, stream=True, verify=self.config.verify_ssl, **request_kwargs
            )   

        # code, api_response =
        url_parts =  path.split(".")
        json = False
        gzip = False
        if len(url_parts) > 1 and (url_parts[-1] == "json" or url_parts[-2] == "json"):
            json = True
        
        if url_parts[-1] == "gz":
            gzip = True

        content = deserialize(response, force_json=json, gzip=gzip)

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