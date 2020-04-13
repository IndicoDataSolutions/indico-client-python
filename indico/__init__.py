import logging
from indico._version import get_version

logging.basicConfig()
Version = version = __version__ = VERSION = get_version()

from indico.client import *
from indico.client.request import *

