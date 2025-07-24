FROM python:3.14.0rc1

COPY . /indico-client
WORKDIR /indico-client
RUN python3 setup.py install
RUN apt-get update && apt-get install python3-sphinx jq vim -y
CMD ["sleep", "infinity"]
