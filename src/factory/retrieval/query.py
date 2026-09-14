#!/usr/bin/env python3
"""Retrieval smoke test.

Usage:
  factory query "que relit la narratrice le soir ?"
  factory query "les deux couverts" --type prop
  factory query "sa voix" --doc judith --n 3
"""

import argparse

import httpx
import chromadb

from factory.settings import settings


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="factory query",
                                     description="Teste le retrieval sur la bible.")
    parser.add_argument("query", help="Requête en langage naturel")
    parser.add_argument("--n", type=int, default=5, help="Nombre de résultats")
    parser.add_argument("--type", help="Filtre sur le type (character, lieu, prop, scene)")
    parser.add_argument("--doc", help="Filtre sur un doc_id précis")
    args = parser.parse_args(argv)

    resp = httpx.post(
        f"{settings.ollama_url}/api/embed",
        json={"model": settings.embed_model, "input": [args.query]},
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

    chroma = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    collection = chroma.get_collection(settings.author_collection)
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
