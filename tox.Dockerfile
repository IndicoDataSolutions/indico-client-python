FROM ubuntu:20.04


RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -yqq apt-transport-https

#deadsnakes holds old versions of python for ubuntu
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yqq software-properties-common && add-apt-repository ppa:deadsnakes/ppa

RUN  DEBIAN_FRONTEND=noninteractive apt-get -yqq install  python3.7 python3.8 python3-pip

RUN pip3 install tox==3.22.0

COPY . /indico-client
WORKDIR /indico-client