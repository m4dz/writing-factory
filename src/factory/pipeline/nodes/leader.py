"""The leader gate: where the prep section ends and the live section begins.

    … → plan → leader ─┬─(prepare)──→ END
                       ├─(prepare, approved, prepared entry)→ write → prep_pick → … → END
                       └─(otherwise)→ live_preflight → write → …

With ``prepare`` in the state the node calls ``interrupt()`` with the plan and
its check report; the owner's answer (``{"approved", "by", "at"}``) is resumed
into ``leader``. Refused, the thread ENDS. Approved, it ends too, unless the
spec's first entry is ``prepared``: the prep then writes that entry, the owner
picks its draft, and it is reviewed before the thread ends (prepared-entry1).
Without ``prepare`` it passes through, so an unsplit run serves today's
prompts.

``interrupt()`` re-executes its node from the top on resume, so the node holds
nothing but the interrupt: a model call here would run twice.
"""

from __future__ import annotations

from langgraph.graph import END
from langgraph.types import interrupt


def leader_node(state: dict) -> dict:
    if not state.get("prepare"):
        return {}
    decision = interrupt({"plan": list(state.get("plan") or []),
                          "plan_report": state.get("plan_report") or ""})
    return {"leader": decision}


def route_after_leader(state: dict) -> str:
    if not state.get("prepare"):
        return "live_preflight"
    specs = state.get("entry_specs") or []
    if (state.get("leader") or {}).get("approved") and specs and specs[0].prepared:
        return "write"
    return END
