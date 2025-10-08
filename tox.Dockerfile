FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -yqq --no-install-recommends \
        apt-transport-https \
        software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# deadsnakes holds additional Python versions for Ubuntu
RUN add-apt-repository -y 'ppa:deadsnakes/ppa' && \
    apt-get update && \
    apt-get -yqq install --no-install-recommends \
        python3.8 \
        python3.9 \
        python3.10 \
        python3.11 \
        python3.12 \
        python3.13 \
        python3-pip \
        tox && \
    rm -rf /var/lib/apt/lists/*

COPY . /indico-client
WORKDIR /indico-client
