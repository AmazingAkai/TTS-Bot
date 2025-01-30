FROM python:3.11-slim

WORKDIR /app

RUN pip install pdm

COPY pyproject.toml pdm.lock ./

RUN pdm install

COPY src src

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080
ENTRYPOINT ["python", "-OO", "src"]
