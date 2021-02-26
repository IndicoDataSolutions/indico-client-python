import logging
from indico._version import get_versions

logging.basicConfig()
Version = version = __version__ = VERSION = get_versions()['version']

from indico.client import *
from indico.client.request import *
