"""In-memory stand-in for the Chroma HTTP client, built from the indexer.

``retrieval`` fetches character chunks by deterministic id. The indexer's
chunker (``indexer/index.py``) is a pure function of the bible files, so the
fake runs it over ``bible/`` and serves exactly the documents a real index
would hold, firewall included. No embedding is computed: ``query`` answers
from ``embeddings`` when a test stored some, otherwise returns nothing, which
matches the pipeline's use (semantic retrieval is disabled during writing).
"""

from __future__ import annotations

from pathlib import Path


class FakeCollection:
    def __init__(self, name: str):
        self.name = name
        self.docs: dict[str, str] = {}
        self.metas: dict[str, dict] = {}

    # --- Chroma API subset ----------------------------------------------------

    def upsert(self, ids, documents, metadatas=None, embeddings=None):
        for k, i in enumerate(ids):
            self.docs[i] = documents[k]
            self.metas[i] = dict((metadatas or [{}] * len(ids))[k] or {})

    def delete(self, ids):
        for i in ids:
            self.docs.pop(i, None)
            self.metas.pop(i, None)

    def get(self, ids=None, where=None, include=None):
        keys = list(ids) if ids is not None else list(self.docs)
        keys = [k for k in keys if k in self.docs and self._match(self.metas[k], where)]
        out = {"ids": keys}
        include = include or []
        if "documents" in include:
            out["documents"] = [self.docs[k] for k in keys]
        if "metadatas" in include:
            out["metadatas"] = [self.metas[k] for k in keys]
        return out

    def query(self, query_embeddings=None, n_results=3, where=None, include=None):
        keys = [k for k in self.docs if self._match(self.metas[k], where)][:n_results]
        return {"ids": [keys], "documents": [[self.docs[k] for k in keys]]}

    @staticmethod
    def _match(meta: dict, where: dict | None) -> bool:
        return all(meta.get(k) == v for k, v in (where or {}).items())


class FakeChromaClient:
    def __init__(self):
        self.collections: dict[str, FakeCollection] = {}

    def get_collection(self, name: str) -> FakeCollection:
        if name not in self.collections:
            raise ValueError(f"Collection {name} does not exist.")
        return self.collections[name]

    def get_or_create_collection(self, name: str, metadata=None) -> FakeCollection:
        return self.collections.setdefault(name, FakeCollection(name))

    def reset_sessions(self) -> None:
        self.collections.pop("sessions", None)

    @classmethod
    def from_bible(cls, bible_dir: Path, collection: str = "auteur") -> "FakeChromaClient":
        """Index ``bible/`` with the real chunker, firewall rules included."""
        import index  # indexer/index.py, on sys.path via conftest

        client = cls()
        col = client.get_or_create_collection(collection)
        for path in sorted(bible_dir.rglob("*.md")):
            if path.name.startswith("_") or index.exclu(path):
                continue
            ids, docs, metas = index.index_file(path, None)
            if ids:
                col.upsert(ids=ids, documents=docs, metadatas=metas)
        return client
