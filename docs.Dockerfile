FROM python:3.9.15

COPY . /indico-client
WORKDIR /indico-client
RUN python3 setup.py install
RUN apt-get update && apt-get install python3-sphinx -y 
RUN pip install sphinx-markdown-builder==0.6.5 sphinx-autodoc-typehints==1.24.0
# docs are outputted to ./markdown
RUN sphinx-build -M markdown ./docsrc .
