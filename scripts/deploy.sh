#!/bin/bash
pip install twine
python setup.py sdist
echo $TWINE_USERNAME
echo $TWINE_PASSWORD
echo $TWINE_REPOSITORY
twine upload --repository testpypi /indico-client/dist/*
