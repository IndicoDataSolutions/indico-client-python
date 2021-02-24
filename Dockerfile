FROM python:3

ENV INDICO_HOST="app.indico.io"

COPY . /indico-client
WORKDIR /indico-client

RUN python3 setup.py install