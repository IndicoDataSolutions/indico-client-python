from typing import Any, Dict, List

import requests_mock as requests_mock_lib

GRAPHQL_URL = "mock://mock/graph/api/graphql"
JSON_HEADERS = {"Content-Type": "application/json"}
HTML_HEADERS = {"Content-Type": "text/html"}
RAINBOW_LIST: List[Dict[str, Any]] = [
    {"path": "/static_uploads/x.indico", "name": "m.indico", "size": 3}
]


def graphql_responses(
    requests_mock: requests_mock_lib.Mocker, *bodies: Dict[str, Any]
) -> Any:
    return requests_mock.post(
        GRAPHQL_URL, [{"json": body, "headers": JSON_HEADERS} for body in bodies]
    )
