FROM python:3.10.0b4

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
