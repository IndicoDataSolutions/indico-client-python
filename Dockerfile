FROM python:3.8

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
