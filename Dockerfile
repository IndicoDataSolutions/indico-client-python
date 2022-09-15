FROM python:3.11.0rc2

ENV INDICO_HOST="dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
