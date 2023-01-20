import http.cookiejar
import logging
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import Union

import requests
from indico.client.request import HTTPRequest
from indico.config import IndicoConfig
from indico.errors import IndicoAuthenticationFailed, IndicoRequestError, IndicoHibernationError
from indico.http.serialization import deserialize
from requests import Response

logger = logging.getLogger(__file__)


class CookiePolicyOverride(http.cookiejar.DefaultCookiePolicy):
    def set_ok(self, cookie, request):
        return True

    def return_ok(self, cookie, request):
        return True

    def path_return_ok(self, path, request):
        return True

    def domain_return_ok(self, domain, request):
        return True


class HTTPClient:
    def __init__(self, config: IndicoConfig = None):
        self.config = config
        self.base_url = f"{self.config.protocol}://{self.config.host}"

        self.request_session = requests.Session()
        if config and isinstance(config.requests_params, dict):
            for param in config.requests_params.keys():
                setattr(self.request_session, param, config.requests_params[param])
        self.request_session.cookies.set_policy(CookiePolicyOverride())
        self.get_short_lived_access_token()

    def post(self, *args, json: Union[dict, list] = None, **kwargs):
        return self._make_request("post", *args, json=json, **kwargs)

    def get(self, *args, params: dict = None, **kwargs):
        return self._make_request("post", *args, params=params, **kwargs)

    def get_short_lived_access_token(self):
        # If the cookie here is already due to _disable_cookie_domain set and we try to pop it later
        # it will error out because we have two cookies with the same name. We just remove the old one
        # here as we are about to refresh it.
        if "auth_token" in self.request_session.cookies:
            self.request_session.cookies.pop("auth_token")

        r = self.post(
            "/auth/users/refresh_token",
            headers={"Authorization": f"Bearer {self.config.api_token}"},
            _refreshed=True,
        )

        # Disable cookie domain in cases where the domain won't match due to using short name domains
        if self.config._disable_cookie_domain:
            value = self.request_session.cookies.get("auth_token", None)
            if not value:
                raise IndicoAuthenticationFailed()
            self.request_session.cookies.pop("auth_token")
            self.request_session.cookies.set_cookie(
                requests.cookies.create_cookie(name="auth_token", value=value)
            )

        return r

    def execute_request(self, request: HTTPRequest):
        return request.process_response(
            self._make_request(
                method=request.method.value.lower(), path=request.path, **request.kwargs
            )
        )

    @contextmanager
    def _handle_files(self, req_kwargs):

        streams = None
        # deepcopying buffers is not supported
        # so, remove "streams" before the deepcopy.
        if "streams" in req_kwargs:
            if req_kwargs["streams"] is not None:
                streams = req_kwargs["streams"].copy()
            del req_kwargs["streams"]

        new_kwargs = deepcopy(req_kwargs)

        files = []
        file_arg = {}
        dup_counts = {}
        if "files" in new_kwargs and new_kwargs["files"] is not None:
            for filepath in new_kwargs["files"]:
                path = Path(filepath)
                fd = path.open("rb")
                files.append(fd)
                # follow the convention of adding (n) after a duplicate filename
                if path.stem in dup_counts:
                    file_arg[path.stem + f"({dup_counts[path.stem]})"] = fd
                    dup_counts[path.stem] += 1
                else:
                    file_arg[path.stem] = fd
                    dup_counts[path.stem] = 1

        if streams is not None and len(streams) > 0:
            for filename in streams:
                # similar operation as above.
                stream = streams[filename]
                files.append(stream)
                if filename in dup_counts:
                    file_arg[filename + f"({dup_counts[filename]})"] = stream
                    dup_counts[filename] += 1
                else:
                    file_arg[filename] = stream
                    dup_counts[filename] = 1

        new_kwargs["files"] = file_arg

        yield new_kwargs

        if files:
            [f.close() for f in files]

    def _make_request(
            self,
            method: str,
            path: str,
            headers: dict = None,
            _refreshed=False,
            **request_kwargs,
    ):
        logger.debug(
            f"[{method}] {path}\n\t Headers: {headers}\n\tRequest Args:{request_kwargs}"
        )

        with self._handle_files(request_kwargs) as new_kwargs:
            response = getattr(self.request_session, method)(
                f"{self.base_url}{path}",
                headers=headers,
                stream=True,
                verify=self.config.verify_ssl,
                **new_kwargs,
            )

        # code, api_response =
        url_parts = path.split(".")
        json = False
        if len(url_parts) > 1 and (url_parts[-1] == "json" or url_parts[-2] == "json"):
            json = True

        decompress = False
        if len(url_parts) > 1 and (url_parts[-1] == "gz"):
            decompress = True

        # If auth expired refresh
        if response.status_code == 401 and not _refreshed:
            self.get_short_lived_access_token()
            return self._make_request(
                method, path, headers, _refreshed=True, **request_kwargs
            )
        elif response.status_code == 401 and _refreshed:
            raise IndicoAuthenticationFailed()

        if response.status_code == 503 and 'Retry-After' in response.headers:
            raise IndicoHibernationError(after=response.headers.get('Retry-After'))

        if response.status_code >= 500:
            raise IndicoRequestError(
                code=response.status_code
            )

        content = deserialize(response, force_json=json, force_decompress=decompress)

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
