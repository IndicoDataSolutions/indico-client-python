"""
Setup for indico apis
"""
from setuptools import setup, find_packages

setup(
    name="indico-client",
    version="4.3.0",
    packages=find_packages(),
    description="""A Python Wrapper for indico app API.""",
    license="MIT License (See LICENSE)",
    long_description=open("README.rst").read(),
    url="https://github.com/IndicoDataSolutions/indico-client-python",
    author="indico",
    author_email="engineering@indico.io",
    tests_require=["pytest>=5.2.1", "requests-mock>=1.7.0-7"],
    install_requires=[
        "msgpack==1.0.0",
        "msgpack-numpy==0.4.4.3",
        "numpy>=1.16.0",
        "Pillow>=6.2.0",
        "requests>=2.22.0",
        "setuptools>=41.4.0",
        "pandas>=1.0.3",
        'importlib-metadata ~= 1.0 ; python_version < "3.8"',
    ],
)
