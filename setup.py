"""
Setup for indico apis
"""
from setuptools import setup, find_packages

setup(
    name="indico-ipa",
    version="1.0.0",
    packages=find_packages(),
    description="""A Python Wrapper for indico app API.""",
    license="MIT License (See LICENSE)",
    long_description=open("README.rst").read(),
    url="https://github.com/IndicoDataSolutions/indico-ipa",
    author="indico",
    author_email="engineering@indico.io",
    tests_require=["pytest>=5.2.1"],
    install_requires=[
        "msgpack==0.5.6",
        "msgpack-numpy==0.4.1",
        "numpy==1.15.4",
        "Pillow>=6.2.0",
        "requests>=2.22.0",
        "setuptools>=41.4.0",
    ],
)
