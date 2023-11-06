#!/bin/bash

pip install sphinx-markdown-builder==0.6.5 sphinx-autodoc-typehints==1.24.0
# docs are outputted to ./markdown
sphinx-build -M markdown ./docsrc .