"""
Setup for indico apis
"""

from pathlib import Path

from setuptools import find_packages, setup

import versioneer

setup(
    name="indico-client",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=["tests"]),
    description="""A Python Wrapper for indico app API.""",
    license="MIT License (See LICENSE)",
    long_description=open(Path(__file__).parent.absolute() / "README.rst").read(),
    url="https://github.com/IndicoDataSolutions/indico-client-python",
    author="indico",
    author_email="engineering@indico.io",
    install_requires=[
        "requests>=2.22.0",
        "setuptools>=41.4.0",
        'importlib-metadata ~= 1.0 ; python_version < "3.8"',
        "deprecation>=2.1.0",
        "jsons",
        "aiohttp[speedups]",
    ],
    extras_require={
        "all": [
            "msgpack>=0.5.6",
            "msgpack-numpy==0.4.4.3",
            "numpy>=1.16.0",
            "pandas>=1.0.3",
        ],
        "datasets": [
            "pandas>=1.0.3",
        ],
        "deserialization": [
            "msgpack>=0.5.6",
            "msgpack-numpy==0.4.4.3",
            "numpy>=1.16.0",
        ],
        "exports": [
            "pandas>=1.0.3",
        ],
    }
)
