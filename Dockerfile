FROM python:3.12-slim-bookworm as base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update

FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


WORKDIR /app

RUN pip install --upgrade pip
# Install Poetry
RUN pip install poetry==1.8.2

# Install the app
# COPY pyproject.toml poetry.lock ./
COPY pyproject.toml  ./
RUN if [ $DEV ]; then \
      poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    else \
      poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    fi


FROM base as runtime

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
COPY speech2text ./speech2text
COPY main.py ./main.py
COPY html ./html
RUN ls

ENTRYPOINT ["python", "main.py" ]