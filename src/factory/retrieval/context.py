#!/usr/bin/env python3
"""Dynamic retrieval over the bible (ChromaDB).

Context is never static: for each scene a 2-3k-token system prompt is
assembled from the truth stored outside the model (present characters'
sheets, place, relevant previous scenes). The model only reads that truth.

Two strategies, combined (ADR-0011):
  1. DETERMINISTIC by id for present characters: the id pattern
     `{doc_id}::{section}` is known, so the chunks that matter for WRITING a
     character (voice, current state, psychology) are fetched directly.
  2. SEMANTIC top-k for atmosphere: place and relevant previous scenes,
     found by similarity against the scene query.
"""

import os
import re

import chromadb


from factory.settings import settings

# Style sheet: served BY SECTION and read from disk, never indexed (see the
# indexer's EXCLUSIONS). Served whole it weighs ~4 200 of the 8 192-token
# window and pushes `FRENCH_GUARD` out: Ollama then slides the window and
# silently truncates the START of the prompt. Path: `settings.style_path`.

# What each node receives from the sheet (ADR-0011). The reference excerpts
# (« Extraits étalons ») go to NO node: session 3 measured that a model shown
# an excerpt copies it character for character into an unrelated scene.
# *Lexique et registre* joined the writing list in the session 5 fix batch:
# hours, exact quantities, physiological notation, rare adjectives and the
# opening register live there, and eight runs out of eight missed them
# because the section was never SERVED, not because it was unwritten.
WRITING_STYLE = ("Narration", "Lexique et registre", "Interdits")
REVIEW_STYLE = ("Interdits", "Phrase et rythme")

# The novel's epistemic rule, served at writing time. Not a style-sheet
# section: it is the line that decides who is right when memory and text
# diverge, and the whole fantastic register follows from it.
EPISTEMIC_LINE = (
    "Le texte fait foi : l'entrée relue a toujours raison contre la mémoire."
)

# Chunks that matter for writing a character, by priority. Not all 7 are
# loaded: history/skills/relations inflate the prompt without helping the
# immediate drafting of an entry. Slugs follow the sheet's numbered sections,
# minus the rank the indexer strips.
WRITING_SECTIONS = ["voix", "etat_narratif_courant", "psychologie"]

# WORLD chunks, for fact derivation (session 5 fix batch, item 3).
# `derive_facts` used to read the writing chunks, narrative state included,
# which carried the pilot table: the derived facts spoke of imposed verdict,
# grade and ratio, production vocabulary then served to the planner as if it
# were world. Facts now derive from what describes the world, not from what
# pilots its making.
WORLD_SECTIONS = ["psychologie", "histoire", "relations"]


def world_context(doc_id: str) -> str:
    """A character's world chunks: the base of the invariant facts."""
    ids = [f"{doc_id}::{s}" for s in WORLD_SECTIONS]
    got = _collection().get(ids=ids, include=["documents"])
    found_item = {i: d for i, d in zip(got["ids"], got["documents"])}
    return "\n\n".join(found_item[i] for i in ids if i in found_item)

# Chunks that matter for PLAYING a character (actor mode). Wider than the
# writing list by design: writing a scene needs no biography, whereas an
# interlocutor will ask about the character's past and relatives. Answering
# « je ne sais pas » about one's own history IS an out-of-role slip.
ACTING_SECTIONS = [
    "voix", "psychologie", "etat_narratif_courant",
    "histoire", "relations", "comportement",
]

# Actor-mode conversation memory lives in a collection SEPARATE from `bible`:
# the bible is derived from canonical Markdown and the indexer purges its
# orphan chunks, which would erase session memory at the first reindex. Same
# flow direction as everywhere (ADR-0007): Markdown first (sessions/), index
# second.

_client = None

# ROUTING journal (seal test §5). Every collection access records its name:
# at the end of a stage B run exactly one value must appear. A firewall that
# rests upon "only the right collection is queried" is a guarantee only if it
# can be PROVEN afterwards.
_ROUTING: list[str] = []


def routing() -> list[str]:
    """Collections actually queried since the last `clear_routing`."""
    return list(_ROUTING)


def clear_routing() -> None:
    _ROUTING.clear()


def _collection(name: str | None = None):
    """The SINGLE gateway to a collection, hence the one place to instrument.
    Scattered `get_collection` calls would leave the routing journal
    incomplete with nothing to signal it."""
    name = name or settings.author_collection
    _ROUTING.append(name)
    return _chroma().get_collection(name)


def _chroma():
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return _client


def embed(text: str) -> list[float]:
    """Embed a query with nomic-embed-text (the index's own model)."""
    import json
    import urllib.request

    payload = json.dumps({"model": settings.embed_model, "input": [text]}).encode()
    req = urllib.request.Request(
        f"{settings.ollama_url}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    # Generous timeout: a first embed may wait for the embedding model to load
    # into RAM (all the more when a large author model is already warm there).
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())["embeddings"][0]


_STYLE_CACHE: dict[str, str] | None = None


def style_sections(names: tuple[str, ...]) -> str:
    """The named sections of the style sheet, read from disk.

    From DISK, not from Chroma (ADR-0011): the style sheet is not narrative
    matter found by similarity but an instruction served whole or not at
    all. Retrieving it would bet an embedding against a rule already known.
    """
    global _STYLE_CACHE
    if _STYLE_CACHE is None:
        _STYLE_CACHE = {}
        path = str(settings.style_path)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            # Frontmatter and HTML comments are editing notes.
            if text.startswith("---"):
                text = text.split("---", 2)[-1]
            text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
            title, body = None, []
            for line in text.splitlines():
                if line.startswith("## "):
                    if title:
                        _STYLE_CACHE[title] = "\n".join(body).strip()
                    title, body = line[3:].strip(), []
                elif title:
                    body.append(line)
            if title:
                _STYLE_CACHE[title] = "\n".join(body).strip()

    blocks = [f"## {n}\n{_without_examples(_STYLE_CACHE[n])}"
             for n in names if _STYLE_CACHE.get(n)]
    return "\n\n".join(blocks)


# The « Écrire / Ne pas écrire » examples are REMOVED FROM SERVICE, not from
# the sheet, which stays intact for human review (ADR-0011). Run B′2 wrote
# « perplexe », the VERBATIM counter-example of *Lexique et registre*: the
# third measurement of the same fact, a shown example gets recited whatever
# sign stands in front of it. The prescriptive rule survives; only the
# illustration goes.
_SERVED_EXAMPLE = re.compile(
    r"^\s*\*\*(?:Écrire|Ne pas écrire)\s*:?\*\*.*?(?=^\s*[-*]\s|^\s*\*\*|\Z)",
    re.MULTILINE | re.DOTALL)


def _without_examples(section: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", _SERVED_EXAMPLE.sub("", section)).strip()


STATE_SECTION = "etat_narratif_courant"


def character_context(doc_id: str, chapter: int | None = None) -> str:
    """The writing chunks of a character, fetched by deterministic id.

    Returns the assembled text (already prefixed `[doc_id / Title]` at index
    time), or an empty string when the character is not yet in the bible.

    `chapter`: narrative state is PER CHAPTER (revamp step 6). The chunk
    `{doc_id}::etat_narratif_courant::chNN`, generated by the narrative-state
    node, is served when it exists; otherwise section 7 of the sheet, as
    before. A chapter whose state was never generated is not an error.
    """
    ids = [f"{doc_id}::{section}" for section in WRITING_SECTIONS]
    scoped = f"{doc_id}::{STATE_SECTION}::ch{chapter:02d}" if chapter else None
    asked = ids + ([scoped] if scoped else [])
    got = _collection().get(ids=asked, include=["documents"])
    # Chroma returns found ids in the requested order; missing ones are dropped.
    found = {i: d for i, d in zip(got["ids"], got["documents"])}
    if scoped and scoped in found:
        found[f"{doc_id}::{STATE_SECTION}"] = found[scoped]
    blocks = [found[i] for i in ids if i in found]
    return "\n\n".join(blocks)


def list_characters() -> list[dict]:
    """Characters available in the bible, to populate an interface.

    Read by METADATA, no embedding: the exhaustive list is wanted, not the
    nearest neighbours of a query.
    """
    try:
        got = _collection().get(
            where={"type": "character"}, include=["metadatas"]
        )
    except Exception:                      # no collection: bible not indexed
        return []
    seen_map: dict[str, dict] = {}
    for meta in got.get("metadatas") or []:
        doc_id = (meta or {}).get("doc_id")
        if doc_id and doc_id not in seen_map:
            seen_map[doc_id] = {
                "id": doc_id,
                "rank": (meta or {}).get("rank", ""),
                "nom": doc_id.split("-")[0].capitalize(),
            }
    return sorted(seen_map.values(), key=lambda c: c["id"])


def acting_context(doc_id: str) -> str:
    """Chunks needed to PLAY a character (see ACTING_SECTIONS)."""
    ids = [f"{doc_id}::{section}" for section in ACTING_SECTIONS]
    got = _collection().get(ids=ids, include=["documents"])
    found = {i: d for i, d in zip(got["ids"], got["documents"])}
    return "\n\n".join(found[i] for i in ids if i in found)


def sessions_collection():
    """The conversation-memory collection, created when first needed.

    `get_or_create`, not `get`: a character's first session cannot require an
    indexer to have run before it.
    """
    return _chroma().get_or_create_collection(
        settings.sessions_collection, metadata={"hnsw:space": "cosine"}
    )


def session_memories(doc_id: str, *, n: int = 3) -> list[str]:
    """Summaries of a character's latest roleplay sessions.

    Fetched by METADATA (doc_id) then sorted by descending timestamp, not by
    similarity: at session start the topic is unknown, so "most recent" beats
    "nearest to a query" nobody has yet. Semantic retrieval takes over during
    the session.
    """
    try:
        got = sessions_collection().get(
            where={"doc_id": doc_id}, include=["documents", "metadatas"]
        )
    except Exception:      # no collection or Chroma silent: no memory
        return []
    pairs = sorted(
        zip(got.get("metadatas") or [], got.get("documents") or []),
        key=lambda p: (p[0] or {}).get("horodatage", ""),
        reverse=True,
    )
    return [doc for _, doc in pairs[:n]]


def semantic_context(query: str, *, doc_type: str, n: int = 3) -> list[str]:
    """Top-k relevant chunks of one type (lieu, scene) for the query."""
    results = (
        _collection()
        .query(
            query_embeddings=[embed(query)],
            n_results=n,
            where={"type": doc_type},
            include=["documents"],
        )
    )
    docs = results.get("documents") or [[]]
    return docs[0]


# Preamble of L'Involontaire. It replaced that of a fantasy novel in the passé
# simple, which contradicted the style sheet outright (the sheet lists the passé
# simple among its blocking interdicts). Two opposed instructions in one
# system prompt raise no error: they produce average text.
PREAMBLE = (
    "Tu écris le carnet de relecture d'une correctrice, à la première "
    "personne. Fantastique psychologique contemporain, passé composé et "
    "présent. Une maison, une voix, aucun dialogue. Elle écrit pour "
    "comprendre, pas pour raconter."
)


def assemble_system_prompt(
    *,
    characters: list[str],
    scene_brief: str,
    n_scenes: int = 2,
    include_scenes: bool = True,
    rag: bool = True,
    style: tuple[str, ...] = WRITING_STYLE,
    epistemic: bool = True,
    chapter: int | None = None,
) -> str:
    """Build the system prompt of an entry.

    `rag`: the ONE variable separating stage A from stage B of session 4. At
        False, no call reaches Chroma or the embedding model; narrative
        context is the brief alone. A parameter rather than an environment
        variable to unplug: that is what guarantees the two stages differ by
        it alone.
    `style`: style-sheet sections to serve (writing or review).
    `include_scenes`: inject the retrieved previous entries. OFF for drafting
        (ADR-0011): the model COPIES an entry present in its context instead
        of using it as backdrop. Continuity comes from the explicit threading
        in `write_node`.

    The "place by similarity" call is gone: there is one house and no scene
    outside its walls.
    """
    parts: list[str] = [PREAMBLE]

    style_block = style_sections(style)
    if style_block:
        parts.append("=== CONTRAT DE STYLE (à respecter sans exception) ===\n"
                     + style_block)
    if epistemic:
        parts.append("=== RÈGLE DU RÉCIT ===\n" + EPISTEMIC_LINE)

    if not rag:
        return "\n\n".join(parts)

    for doc_id in characters:
        block = character_context(doc_id, chapter)
        if block:
            parts.append(f"=== NARRATRICE : {doc_id} ===\n{block}")

    if include_scenes and n_scenes > 0:
        scenes = semantic_context(scene_brief, doc_type="scene", n=n_scenes)
        if scenes:
            parts.append(
                "=== ENTRÉES PRÉCÉDENTES (contexte de continuité — NE PAS "
                "RECOPIER, seulement pour la cohérence) ===\n" + "\n\n".join(scenes)
            )

    return "\n\n".join(parts)
