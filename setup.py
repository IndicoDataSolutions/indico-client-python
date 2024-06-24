"""
Setup for indico apis
"""
import versioneer
from pathlib import Path
from setuptools import setup, find_packages

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
    tests_require=["pytest>=5.2.1", "requests-mock>=1.8.0", "pytest-asyncio"],
    install_requires=[
        "requests>=2.22.0",
        "setuptools>=41.4.0",
        "pandas>=1.0.3",
        'importlib-metadata ~= 1.0 ; python_version < "3.8"',
        "deprecation>=2.1.0",
        "jsons",
        "aiohttp[speedups]"
    ],
    extras_require={
        "deserialization": [
            "msgpack>=0.5.6",
            "msgpack-numpy==0.4.4.3",
            "numpy>=1.16.0",
        ],
    }
)
