FROM python:latest

ENV INDICO_HOST="try.indico.io"

COPY . /indico-client
WORKDIR /indico-client