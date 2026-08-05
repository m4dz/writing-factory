#!/usr/bin/env python3
"""Indexeur de la bible monde.

Lit les fichiers Markdown de la bible, découpe chaque fiche en chunks
(un chunk par section `## `), génère les embeddings via nomic-embed-text
sur Ollama, et pousse le tout dans ChromaDB.

Idempotent : les IDs de chunks sont déterministes ({id}::{section}),
un re-run met à jour les chunks modifiés et purge les chunks disparus.
"""

import os
import re
import sys
import unicodedata
from pathlib import Path

import frontmatter
import httpx
import chromadb

# --- Configuration (surchargée par l'environnement) -------------------------

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
BIBLE_DIR = Path(os.environ.get("BIBLE_DIR", "./bible"))
COLLECTION = os.environ.get("CHROMA_COLLECTION", "bible")

# --- Utilitaires -------------------------------------------------------------

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def slugify(text: str) -> str:
    """`## Voix et expression` -> `voix_et_expression`"""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return text.strip("_")


def split_sections(body: str) -> list[tuple[str, str]]:
    """Découpe le corps Markdown en (titre_de_section, contenu).

    Tout ce qui précède le premier `## ` est rattaché à une section
    `_preambule` (le titre `# Nom` de la fiche, typiquement).
    """
    sections: list[tuple[str, str]] = []
    current_title = "_preambule"
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_lines and "".join(current_lines).strip():
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines and "".join(current_lines).strip():
        sections.append((current_title, "\n".join(current_lines).strip()))
    return sections


def clean_for_embedding(text: str) -> str:
    """Retire les commentaires HTML (instructions pour l'humain,
    pas pour le retrieval) et compacte les lignes vides."""
    text = HTML_COMMENT.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def embed(client: httpx.Client, texts: list[str]) -> list[list[float]]:
    """Embeddings par lot via l'API Ollama /api/embed."""
    resp = client.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": texts},
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"]


def scalar_metadata(meta: dict) -> dict:
    """ChromaDB n'accepte que des métadonnées scalaires :
    les listes (tags, relations) sont sérialisées en CSV."""
    out = {}
    for key, value in meta.items():
        if isinstance(value, list):
            out[key] = ",".join(str(v) for v in value)
        elif isinstance(value, (str, int, float, bool)):
            out[key] = value
        elif value is not None:
            out[key] = str(value)
    return out


# --- Indexation ---------------------------------------------------------------

def index_file(path: Path, ollama: httpx.Client) -> tuple[list[str], list[str], list[dict]]:
    """Retourne (ids, documents, metadatas) pour un fichier de la bible."""
    post = frontmatter.load(path)
    doc_id = post.get("id") or slugify(path.stem)
    doc_meta = scalar_metadata(dict(post.metadata))
    doc_meta["doc_id"] = doc_id
    doc_meta["source_file"] = str(path.relative_to(BIBLE_DIR))

    ids, documents, metadatas = [], [], []
    for title, content in split_sections(post.content):
        cleaned = clean_for_embedding(content)
        if title == "_preambule":
            # Ne garder le préambule que s'il contient autre chose
            # que le titre `# Nom` de la fiche (sinon : bruit).
            without_heading = re.sub(r"^#\s+.*$", "", cleaned, flags=re.MULTILINE).strip()
            if not without_heading:
                continue
        if not cleaned:
            continue  # section vide du template, pas encore remplie
        section = slugify(title)
        # Préfixer le chunk avec son identité améliore nettement le retrieval :
        # l'embedding "sait" de qui et de quoi il parle.
        document = f"[{doc_id} / {title}]\n{cleaned}"
        ids.append(f"{doc_id}::{section}")
        documents.append(document)
        metadatas.append({**doc_meta, "section": section})
    return ids, documents, metadatas


def main() -> int:
    if not BIBLE_DIR.is_dir():
        print(f"ERREUR : répertoire bible introuvable : {BIBLE_DIR}", file=sys.stderr)
        return 1

    files = sorted(
        p for p in BIBLE_DIR.rglob("*.md")
        if not p.name.startswith("_")  # _template.md et consorts sont ignorés
    )
    if not files:
        print(f"Aucune fiche à indexer dans {BIBLE_DIR} (les _template.md sont ignorés).")
        # On ne s'arrête PAS ici : il faut quand même purger d'éventuels
        # chunks orphelins (cas où l'on vient de supprimer la dernière fiche).

    chroma = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    collection = chroma.get_or_create_collection(
        COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    all_ids: list[str] = []
    with httpx.Client() as ollama:
        for path in files:
            ids, documents, metadatas = index_file(path, ollama)
            if not ids:
                print(f"  ~ {path.name} : aucune section remplie, ignoré")
                continue
            embeddings = embed(ollama, documents)
            collection.upsert(
                ids=ids, documents=documents,
                metadatas=metadatas, embeddings=embeddings,
            )
            all_ids.extend(ids)
            print(f"  + {path.relative_to(BIBLE_DIR)} : {len(ids)} chunks")

    # Purge des chunks orphelins (sections ou fiches supprimées)
    existing = collection.get(include=[])["ids"]
    stale = [i for i in existing if i not in set(all_ids)]
    if stale:
        collection.delete(ids=stale)
        print(f"  - {len(stale)} chunks orphelins purgés")

    print(f"\nIndexation terminée : {len(all_ids)} chunks dans '{COLLECTION}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
