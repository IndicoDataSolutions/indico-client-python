FROM python:3.12.0a5

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
