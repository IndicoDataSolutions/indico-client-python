FROM python:3

ENV INDICO_HOST="app.indico.io"

RUN apk add --no-cache libjpeg jpeg-dev zlib-dev
COPY README.rst README.rst

COPY . /incido-client
WORKDIR /indico-client

RUN python3 setup.py install