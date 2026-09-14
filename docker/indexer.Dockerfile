# Bible indexer, run on demand (podman-compose --profile tools run --rm indexer).
# Installs the factory package with its core dependencies only (no LangGraph,
# no TTS): `factory index`, `factory query` and `factory eval` run here.
FROM docker.io/library/python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

ENV FACTORY_ROOT=/app
# Default: index. Override to test retrieval:
#   podman-compose --profile tools run --rm indexer factory query "ma requête"
CMD ["factory", "index"]
