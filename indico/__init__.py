import logging

from indico._version import get_versions  # type: ignore

logging.basicConfig()
Version = version = __version__ = VERSION = get_versions()["version"]

from indico.client import *
from indico.client.request import *

from ._version import get_versions  # type: ignore

__version__ = get_versions()["version"]
del get_versions
