FROM ubuntu:20.04


RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y apt-transport-https

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa

# ensure the base image has what we need
#RUN DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential software-properties-common
# install legacy python versions
RUN  DEBIAN_FRONTEND=noninteractive apt-get -yqq install  python3.7 python3.8 python3-pip

RUN pip3 install tox


COPY . /indico-client
WORKDIR /indico-client