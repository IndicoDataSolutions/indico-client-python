FROM python:3.9.13

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
