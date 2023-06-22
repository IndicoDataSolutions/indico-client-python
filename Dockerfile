FROM python:3.12.0b3

ENV INDICO_HOST="dev-ci.us-east-2.indico-dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
