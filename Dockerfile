ARG REGISTRY_PATH='harbor.devops.indico.io/indico'
ARG BUILD_TAG=latest

FROM ${REGISTRY_PATH}/ubuntu-2204-build:${BUILD_TAG} as poetry-installer
ARG POETRY_INSTALL_ARGS

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -yqq apt-transport-https

#deadsnakes holds old versions of python for ubuntu
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yqq software-properties-common && add-apt-repository ppa:deadsnakes/ppa

RUN  DEBIAN_FRONTEND=noninteractive apt-get -yqq install  python3.8 python3.9 python3.10 python3.11 python3.12 python3.13 python3-pip

RUN pip3 install tox==4.11.3

COPY . /indico-client
WORKDIR /indico-client