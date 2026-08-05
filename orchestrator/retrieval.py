#!/usr/bin/env python3
"""Retrieval contextuel dynamique sur la bible (ChromaDB).

Le principe du projet : le contexte n'est PAS statique. À chaque scène on
assemble un prompt système de 2-3k tokens à partir de la vérité stockée hors
du modèle : fiches des personnages présents, lieu, scènes précédentes
pertinentes. Le modèle n'est qu'un lecteur de cette vérité.

Deux stratégies combinées :
  1. DÉTERMINISTE (par id) pour les personnages présents : on connaît le
     patron d'id `{doc_id}::{section}`, donc on va chercher directement les
     chunks qui comptent pour ÉCRIRE un personnage (voix, état courant,
     psychologie) — pas de pari sémantique là où on sait déjà quoi vouloir.
  2. SÉMANTIQUE (top-k) pour l'ambiance : lieu et scènes précédentes
     pertinentes, retrouvés par similarité sur la requête de la scène.
"""

import os

import chromadb

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
COLLECTION = os.environ.get("CHROMA_COLLECTION", "bible")

# Chunks qui comptent pour écrire un personnage, par ordre de priorité.
# On ne charge pas les 7 : histoire/compétences/relations gonflent le prompt
# sans servir la rédaction immédiate d'une scène.
WRITING_SECTIONS = ["voix_et_expression", "etat_narratif_courant", "psychologie"]

_client = None


def _chroma():
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _client


def embed(text: str) -> list[float]:
    """Embedding d'une requête via nomic-embed-text (même modèle que l'index)."""
    import json
    import urllib.request

    payload = json.dumps({"model": EMBED_MODEL, "input": [text]}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    # Timeout large : un premier embed peut attendre le chargement du modèle
    # d'embedding en RAM (surtout si un gros modèle auteur y est déjà chaud).
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())["embeddings"][0]


def character_context(doc_id: str) -> str:
    """Récupère, par id déterministe, les chunks d'écriture d'un personnage.

    Retourne le texte assemblé (déjà préfixé `[doc_id / Titre]` à l'index),
    ou une chaîne vide si le personnage n'est pas encore dans la bible.
    """
    ids = [f"{doc_id}::{section}" for section in WRITING_SECTIONS]
    got = _chroma().get_collection(COLLECTION).get(ids=ids, include=["documents"])
    # Chroma renvoie les ids trouvés dans l'ordre demandé ; on filtre les absents.
    found = {i: d for i, d in zip(got["ids"], got["documents"])}
    blocks = [found[i] for i in ids if i in found]
    return "\n\n".join(blocks)


def semantic_context(query: str, *, doc_type: str, n: int = 3) -> list[str]:
    """Top-k chunks pertinents d'un type donné (lieu, scene) pour la requête."""
    results = (
        _chroma()
        .get_collection(COLLECTION)
        .query(
            query_embeddings=[embed(query)],
            n_results=n,
            where={"type": doc_type},
            include=["documents"],
        )
    )
    docs = results.get("documents") or [[]]
    return docs[0]


def assemble_system_prompt(
    *,
    characters: list[str],
    scene_brief: str,
    place_query: str | None = None,
    n_scenes: int = 2,
) -> str:
    """Construit le prompt système d'une scène à partir de la bible.

    `characters` : doc_ids des personnages présents (contexte déterministe).
    `scene_brief` : sert de requête sémantique pour lieu + scènes précédentes.
    """
    parts: list[str] = [
        "Tu es l'auteur d'un roman de fantasy en français. Prose littéraire "
        "soignée, au passé simple, immersive. Respecte SCRUPULEUSEMENT les "
        "fiches ci-dessous : voix des personnages, faits établis, liens de "
        "cause à effet. Ne contredis jamais un fait de la bible. N'invente "
        "aucun élément non fourni.",
    ]

    for doc_id in characters:
        block = character_context(doc_id)
        if block:
            parts.append(f"=== PERSONNAGE PRÉSENT : {doc_id} ===\n{block}")

    lieux = semantic_context(place_query or scene_brief, doc_type="lieu", n=1)
    if lieux:
        parts.append("=== LIEU ===\n" + "\n\n".join(lieux))

    scenes = semantic_context(scene_brief, doc_type="scene", n=n_scenes)
    if scenes:
        parts.append(
            "=== SCÈNES PRÉCÉDENTES PERTINENTES ===\n" + "\n\n".join(scenes)
        )

    return "\n\n".join(parts)
