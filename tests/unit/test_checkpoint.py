"""The checkpoint serializer: the chapter state survives it, nothing else is built.

A checkpoint is read back when a prepared plan is resumed; what it gives back
must be the state that was approved, and loading it must never construct a
type outside the chapter-spec dataclasses (no pickle, no foreign class).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from factory.chapter_spec import load_chapter
from factory.chapter_spec.model import EntrySpec
from factory.pipeline import checkpoint


@dataclass(frozen=True)
class Foreign:
    payload: str


def test_chapter_7_state_round_trips_with_its_entry_specs():
    state = load_chapter(7).state(seed=424242)
    serde = checkpoint.serializer()
    back = serde.loads_typed(serde.dumps_typed(state))
    assert back == state
    specs = back["entry_specs"]
    assert specs and all(type(e) is EntrySpec for e in specs)
    # Declared tuples come back as tuples, not as msgpack's lists.
    beats = next(e for e in specs if e.beats)
    assert isinstance(beats.beats, tuple) and isinstance(beats.words, tuple)


def test_a_foreign_type_is_not_constructed_and_pickle_is_off(caplog):
    serde = checkpoint.serializer()
    assert serde.pickle_fallback is False
    with caplog.at_level(logging.WARNING):
        back = serde.loads_typed(serde.dumps_typed({"x": Foreign("rm -rf")}))
    assert not isinstance(back["x"], Foreign)
    assert "Blocked deserialization" in caplog.text


def test_saver_on_disk_keeps_the_state_and_read_only_never_writes(tmp_path):
    from factory.pipeline.graph import build_graph

    path = tmp_path / checkpoint.FILENAME
    state = load_chapter(7).state(seed=1)
    config = checkpoint.thread_config("t")
    with checkpoint.open_saver(path) as saver:
        graph = build_graph(checkpointer=saver)
        graph.update_state(config, state, as_node="plan")
    before = path.read_bytes()
    with checkpoint.open_saver(path, read_only=True) as saver:
        values = build_graph(checkpointer=saver).get_state(config).values
    assert {k: values[k] for k in state} == state
    assert path.read_bytes() == before
