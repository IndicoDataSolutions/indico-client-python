import logging

from indico.client import *  # noqa: F403
from indico.client.request import *  # noqa: F403

try:
    from importlib.metadata import version as _get_version_stdlib

    __version__ = _get_version_stdlib("indico-client")
except (ImportError, Exception):
    try:
        from importlib_metadata import version as _get_version

        __version__ = _get_version("indico-client")
    except (ImportError, Exception):
        __version__ = "0.0.0"

logging.basicConfig()
Version = version = VERSION = __version__
