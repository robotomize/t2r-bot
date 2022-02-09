FROM python:3.9.0-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /workdir

RUN apt-get -qq update && apt-get install -y --no-install-recommends

COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade pip
RUN pip install poetry && \
    poetry config virtualenvs.in-project false && \
    poetry install --no-dev --no-interaction --no-ansi

COPY . ./

CMD poetry run python /workdir/app/main.py