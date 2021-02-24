FROM python:3.8

ENV INDICO_HOST="app.indico.io"

COPY . /indico-client
WORKDIR /indico-client

RUN pip3 install requests-mock pytest
RUN python3 setup.py install