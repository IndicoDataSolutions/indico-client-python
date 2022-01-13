FROM python:3.10.0b2

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
