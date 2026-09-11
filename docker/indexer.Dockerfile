# Bible indexer, run on demand (podman-compose --profile tools run --rm indexer).
# Installs the factory package; only factory.retrieval.indexer is executed.
FROM docker.io/library/python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

ENV FACTORY_ROOT=/app
# Default: index. Override to test retrieval:
#   podman-compose --profile tools run --rm indexer python -m factory.retrieval.query "ma requête"
CMD ["python", "-m", "factory.retrieval.indexer"]
