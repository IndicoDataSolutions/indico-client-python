FROM python:3.14.2

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY . /indico-client
WORKDIR /indico-client

RUN uv sync --locked --active --extra all && \
    rm -rf /root/.cache/uv
RUN apt-get update && apt-get install python3-sphinx jq vim -y && \
    rm -rf /var/lib/apt/lists/*
CMD ["sleep", "infinity"]
