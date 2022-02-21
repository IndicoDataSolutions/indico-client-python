FROM python:3.10.0b3

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
