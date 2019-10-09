import os
from pathlib import Path


host = os.getenv("INDICO_HOST", "app.indico.io")
url_protocol = os.getenv("INDICO_PROTOCOL", "https")
serializer = os.getenv("INDICO_SERIALIZER", "msgpack")
api_token_path = os.getenv("INDICO_API_TOKEN_PATH")


def resolve_api_token(path=None):
    path = path or api_token_path
    if not path:
        path = Path(".") / "indico_api_token.txt"
        if not path.exists():
            path = Path.home() / "indico_api_token.txt"

    if not path.exists():
        raise RuntimeError(
            "Expected indico_api_token.txt in current directory, home directory, "
            "or provided as indicoio.config.token_path"
        )

    with path.open("r") as f:
        return f.read()

