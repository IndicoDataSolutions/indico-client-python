FROM python:3.12.7

ENV INDICO_HOST="try.indico.io"

COPY . /indico-client
WORKDIR /indico-client