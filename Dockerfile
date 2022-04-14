FROM python:3.11.0a6

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
