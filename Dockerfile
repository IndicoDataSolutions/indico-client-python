FROM python:3.10.11

ENV INDICO_HOST="dev-ci.us-east-2.indico-dev.indico.io"

COPY . /indico-client
WORKDIR /indico-client
