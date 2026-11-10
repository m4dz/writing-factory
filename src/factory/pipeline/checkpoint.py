"""Checkpointing of a run's graph: the SQLite saver and its restricted serializer.

Every run started by `factory generate`, `factory prepare` or the API compiles
the graph with a saver on `<run dir>/checkpoints.sqlite`, `thread_id` = run id,
durability `sync`: a checkpoint is on disk before the next node starts. Graphs
built for tests, calibration and `stage_runner` carry none (`build_graph()`).

The serializer deserializes only the chapter-spec dataclasses the state
carries, besides LangGraph's own safe types, and never falls back to pickle:
loading a checkpoint must not be a way to run code. The run directory sits
under the runs root, never indexed; the file holds the material `prompts.md`
and `variants.md` already hold.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from factory.chapter_spec.model import BeatSpec, BestOf, Drift, EntrySpec

# The only project types a chapter state holds (`entry_specs`). The installed
# serializer takes (module, name) pairs or classes, not a module name.
ALLOWED_TYPES = (BeatSpec, BestOf, Drift, EntrySpec)

FILENAME = "checkpoints.sqlite"


def serializer() -> JsonPlusSerializer:
    return JsonPlusSerializer(pickle_fallback=False, allowed_msgpack_modules=ALLOWED_TYPES)


@contextmanager
def open_saver(path: Path, *, read_only: bool = False):
    """A saver on one SQLite file, closed on exit. `read_only` opens the file
    without write access: reading a prepared run never touches it."""
    if read_only:
        conn = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True,
                               check_same_thread=False)
    else:
        conn = sqlite3.connect(str(path), check_same_thread=False)
    try:
        yield SqliteSaver(conn, serde=serializer())
    finally:
        conn.close()


def thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}
