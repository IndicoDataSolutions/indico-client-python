#!/bin/bash

#install additional test reqs and run smoke tests
pip install requests-mock pytest
python setup.py install
pytest -sv ./tests