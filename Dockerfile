FROM python:3.14.0a1

ENV INDICO_HOST="try.indico.io"

COPY . /indico-client
WORKDIR /indico-client