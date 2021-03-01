#!/bin/bash
rm -rf /indico-client/dist
pip install twine==3.3.0
python setup.py sdist
echo $TWINE_USERNAME
echo $TWINE_REPOSITORY
twine upload /indico-client/dist/*
