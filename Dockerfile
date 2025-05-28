FROM python:3.12-slim

ENV POETRY_VERSION=2.1.3

RUN apt-get update && apt-get install -y curl build-essential git && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --only main

COPY ./app ./app
