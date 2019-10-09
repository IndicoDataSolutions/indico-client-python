FROM indicoio/numpy as numpy-base
FROM indicoio/alpine:3.7.3

ENV INDICO_HOST="app.indico.io"

RUN apk add --no-cache libjpeg jpeg-dev zlib-dev
COPY README.rst README.rst

COPY . /indicoio
WORKDIR /indicoio

RUN python3 setup.py test