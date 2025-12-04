FROM python:3.14.1

ENV INDICO_HOST="try.indico.io"

COPY . /indico-client
WORKDIR /indico-client