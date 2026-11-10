"""The prep/live split in the graph: the leader gate and the live preflight.

A prepared thread stops at the gate and never writes; an unsplit run passes
through both new nodes (the snapshots hold it byte for byte) and probes the
machine once; a resumed run probes it again, strict and timed, before the
first `write` call.
"""

from __future__ import annotations

import pytest
from langgraph.types import Command

from factory.chapter_spec import load_chapter
from factory.pipeline import checkpoint
from factory.pipeline.graph import build_graph
from factory.pipeline.nodes import preflight as preflight_node


@pytest.fixture
def probes(monkeypatch):
    """Every machine gate the graph runs, with what it was asked."""
    asked: list[dict] = []
    monkeypatch.setattr(preflight_node, "preflight",
                        lambda **k: asked.append(k) or [])
    return asked


def _writes(model) -> list:
    return [c for c in model.calls if c.role.startswith("write")]


@pytest.mark.parametrize("chapter", [7, 2])
def test_a_prepared_thread_stops_at_the_gate_and_never_writes(chapter, tmp_path, fake_model,
                                                              fake_chroma, quiet_progress):
    state = {**load_chapter(chapter).state(seed=1), "prepare": True}
    config = checkpoint.thread_config("prep")
    with checkpoint.open_saver(tmp_path / checkpoint.FILENAME) as saver:
        graph = build_graph(checkpointer=saver)
        graph.invoke(state, config, durability="sync")
        snap = graph.get_state(config)
        assert snap.next == ("leader",)
        (gate,) = snap.interrupts
        assert gate.value["plan"] == snap.values["plan"] and "plan_report" in gate.value
        final = graph.invoke(Command(resume={"approved": True, "by": "owner", "at": "t"}),
                             config, durability="sync")
        assert graph.get_state(config).next == ()
    assert final["leader"]["approved"] is True and final["plan"]
    assert not final.get("scenes") and not final.get("repaired")
    assert _writes(fake_model) == []
    if chapter == 2:                       # the plan node did call the model
        assert fake_model.calls


def test_a_refusal_ends_the_thread_the_same_way(tmp_path, fake_model, fake_chroma,
                                                quiet_progress):
    state = {**load_chapter(2).state(seed=1), "prepare": True}
    config = checkpoint.thread_config("prep")
    with checkpoint.open_saver(tmp_path / checkpoint.FILENAME) as saver:
        graph = build_graph(checkpointer=saver)
        graph.invoke(state, config, durability="sync")
        final = graph.invoke(Command(resume={"approved": False}), config, durability="sync")
    assert final["leader"] == {"approved": False} and _writes(fake_model) == []


def test_no_second_probe_on_an_unsplit_run(fake_model, fake_chroma, quiet_progress, probes):
    state = {**load_chapter(7).state(seed=1), "preflight": True}
    final = build_graph().invoke(state, config={"recursion_limit": 50})
    assert probes == [{"strict": True, "timer": True}]
    assert final["repaired"] and "leader" not in final


def test_a_resumed_run_probes_the_stage_machine_before_writing(fake_model, fake_chroma,
                                                               quiet_progress, monkeypatch):
    order: list[str] = []
    monkeypatch.setattr(preflight_node, "preflight",
                        lambda **k: order.append(f"probe {k}") or [])
    real_chat = fake_model.chat

    def chat(*a, **k):
        order.append("model")
        return real_chat(*a, **k)

    from factory.infra import ollama
    monkeypatch.setattr(ollama.client, "chat", chat)
    state = {**load_chapter(7).state(seed=1), "prepared_from": "x",
             "preflight": {"strict": True, "timer": True}}
    # A resumed run enters at `live_preflight`; the plain graph, entered from
    # START, shows the first gate and the live one both acting.
    build_graph().invoke(state, config={"recursion_limit": 50})
    probes = [o for o in order if o.startswith("probe")]
    assert len(probes) == 2 and order.index("model") > order.index(probes[1])
