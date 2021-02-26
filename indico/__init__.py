import logging
from ._version import get_version

logging.basicConfig()
Version = version = __version__ = VERSION = get_version()

from indico.client import *
from indico.client.request import *


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
