"""The leader gate: where the prep section ends and the live section begins.

    … → plan → leader ─┬─(prepare)──→ END
                       └─(otherwise)→ live_preflight → write → …

With ``prepare`` in the state the node calls ``interrupt()`` with the plan and
its check report; the owner's answer (``{"approved", "by", "at"}``) is resumed
into ``leader`` and the thread ENDS: a prepared thread never writes. Without
``prepare`` it passes through, so an unsplit run serves today's prompts.

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
    return END if state.get("prepare") else "live_preflight"
