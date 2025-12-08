FROM python:3.10.4

ENV INDICO_HOST="try.indico.io"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY . /indico-client
WORKDIR /indico-client

RUN uv sync --locked --extra all && \
    rm -rf /root/.cache/uv