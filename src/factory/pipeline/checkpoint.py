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


# --- prepare and resume --------------------------------------------------------

def gate(graph, config: dict) -> dict:
    """The payload a prepared thread stopped with at the leader gate."""
    pending = graph.get_state(config).interrupts
    if not pending:
        raise RuntimeError("le run n'est pas arrêté à la porte du plan")
    return pending[0].value


def prepared_values(path: Path, thread_id: str) -> dict:
    """The final state of a prepared thread, read without write access."""
    from factory.pipeline.graph import build_graph
    with open_saver(path, read_only=True) as saver:
        return dict(build_graph(checkpointer=saver).get_state(thread_config(thread_id)).values)


def seed_resumed(graph, config: dict, values: dict, *, prepared_from: str, live: dict) -> None:
    """Start a NEW thread from a prepared state, as if `leader` had just run:
    `route_after_leader` reads `prepare: False` and the next node is
    `live_preflight`. `live` carries the stage requests (preflight, render,
    voice, artifacts_dir, seed)."""
    graph.update_state(config, {**values, **live, "prepare": False,
                                "prepared_from": prepared_from}, as_node="leader")


def resume_prepared(graph, config: dict, prepared, live: dict) -> dict:
    """Resume a prepared run in the thread of `config`: read its state, refuse
    on a fingerprint difference (before any node runs), seed, run the live
    section."""
    from factory import runs as run_registry
    values = prepared_values(prepared.checkpoints_path, prepared.id)
    run_registry.check_fingerprint(prepared, values)
    seed_resumed(graph, config, values, prepared_from=prepared.id, live=live)
    return graph.invoke(None, config, durability="sync")
