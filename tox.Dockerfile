FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -yqq apt-transport-https

#deadsnakes holds old versions of python for ubuntu
RUN apt-get install -yqq software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && \
    apt-get -yqq install \
        python3.8 \
        python3.8-distutils \
        python3.9 \
        python3.9-distutils \
        python3.10 \
        python3.11 \
        python3.12 \
        python3.13 \
        curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY . /indico-client
WORKDIR /indico-client

RUN uv pip install --system ".[test]" && \
    rm -rf /root/.cache/uv
