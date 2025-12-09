#!/bin/bash
rm -rf /indico-client/dist
uv pip install --system ".[deploy]"
uv build --sdist
echo $TWINE_USERNAME
echo $TWINE_REPOSITORY
twine upload /indico-client/dist/*
