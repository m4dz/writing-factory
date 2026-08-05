#!/usr/bin/env python3
"""Validation du retrieval.

Usage :
  python query_test.py "quelle est la fracture d'Élara ?"
  python query_test.py "la forge" --type lieu
  python query_test.py "sa voix" --doc elara-vance --n 3
"""

import argparse
import os

import httpx
import chromadb

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
COLLECTION = os.environ.get("CHROMA_COLLECTION", "bible")


def main() -> None:
    parser = argparse.ArgumentParser(description="Teste le retrieval sur la bible.")
    parser.add_argument("query", help="Requête en langage naturel")
    parser.add_argument("--n", type=int, default=5, help="Nombre de résultats")
    parser.add_argument("--type", help="Filtre sur le type (character, lieu, prop, scene)")
    parser.add_argument("--doc", help="Filtre sur un doc_id précis")
    args = parser.parse_args()

    resp = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": [args.query]},
        timeout=60.0,
    )
    resp.raise_for_status()
    embedding = resp.json()["embeddings"][0]

    filters = []
    if args.type:
        filters.append({"type": args.type})
    if args.doc:
        filters.append({"doc_id": args.doc})
    where = None
    if len(filters) == 1:
        where = filters[0]
    elif len(filters) > 1:
        where = {"$and": filters}

    chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma.get_collection(COLLECTION)
    results = collection.query(
        query_embeddings=[embedding], n_results=args.n, where=where,
        include=["documents", "metadatas", "distances"],
    )

    print(f"\nRequête : {args.query!r}" + (f"  (filtres : {where})" if where else ""))
    print("=" * 70)
    for rank, (cid, doc, dist) in enumerate(
        zip(results["ids"][0], results["documents"][0], results["distances"][0]), 1
    ):
        similarity = 1 - dist
        preview = doc[:220].replace("\n", " ")
        print(f"\n{rank}. {cid}  (similarité {similarity:.3f})")
        print(f"   {preview}{'…' if len(doc) > 220 else ''}")
    print()


if __name__ == "__main__":
    main()
