"""
Minimal setup.py for versioneer support.
All project metadata is now in pyproject.toml.
"""

from setuptools import setup

import versioneer

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
