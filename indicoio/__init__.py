import logging
from . import config
from .api import IndicoApi, Indico, ModelGroup

logging.basicConfig()
Version = version = __version__ = VERSION = "2.0.0"

__all__ = ["config", "IndicoApi", "Indico", "ModelGroup"]
