FROM docker.io/library/python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY index.py query_test.py ./

# Par défaut : indexation. Surcharger pour tester le retrieval :
#   podman-compose run --rm indexer python query_test.py "ma requête"
CMD ["python", "index.py"]
