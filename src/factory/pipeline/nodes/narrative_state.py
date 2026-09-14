"""Second node: the narrative state of the chapter being written, generated
from the author's table and indexed for retrieval.

Runs when the state field `narrative_state` is true (the API and
`factory generate` ask; calibration and tests do not). Idempotent: the file is
rewritten only when its content changes, and the upsert replaces the chunk of
the same id. The writing prompt then serves `judith::etat_narratif_courant::chNN`
instead of the sheet's section 7 — the only prompt change this node makes.
"""

from __future__ import annotations

from factory.chapter_spec import narrative_state as ns
from factory.infra import progress
from factory.retrieval import context as retrieval
from factory.retrieval import indexer


def index_state_file(path) -> list[str]:
    """Chunk the generated file with the indexer's own chunker and upsert it."""
    ids, docs, metas = indexer.index_file(path, None)
    if not ids:
        return []
    retrieval._collection().upsert(
        ids=ids, documents=docs, metadatas=metas,
        embeddings=[retrieval.embed(d) for d in docs])
    return ids


def narrative_state_node(state: dict) -> dict:
    chapter = state.get("chapter")
    if not state.get("narrative_state") or not chapter:
        return {}
    progress.phase("État narratif", f"chapitre {chapter}")
    try:
        path, changed = ns.write_state_file(int(chapter))
    except LookupError as exc:
        progress.note(f"état narratif : {exc} — le chapitre s'écrit avec la fiche seule")
        return {"narrative_state_path": ""}
    ids = index_state_file(path)
    progress.note(f"état narratif du chapitre {chapter} "
                  f"{'régénéré' if changed else 'inchangé'}, chunk {', '.join(ids) or 'aucun'}")
    return {"narrative_state_path": str(path)}
