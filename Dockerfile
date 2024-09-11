FROM python:3.12.5

ENV INDICO_HOST="try.indico.io"

COPY . /indico-client
WORKDIR /indico-client