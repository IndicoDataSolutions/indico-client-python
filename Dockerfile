FROM python:3.13.2

ENV INDICO_HOST="try.indico.io"

COPY . /indico-client
WORKDIR /indico-client