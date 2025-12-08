#!/bin/bash
rm -rf /indico-client/dist
uv pip install --system ".[deploy]"
python setup.py sdist
echo $TWINE_USERNAME
echo $TWINE_REPOSITORY
twine upload /indico-client/dist/*
