FROM python:3.11.0b1

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
