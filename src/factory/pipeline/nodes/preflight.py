"""First node: refuse a throttled machine before any model call.

The check itself is ``factory.infra.preflight.preflight``; this node decides
when it runs and records what it said. The state field ``preflight`` carries
the request:

- absent or falsy: the node does nothing (calibration runs and tests);
- ``True``: strict, timing mode (the stage path);
- a dict ``{"strict": bool, "timer": bool}``: explicit.

``live_preflight_node`` runs the same gate again after the leader gate, on a
run resumed from a prepared plan only (``prepared_from`` in the state): the
machine that matters is the one on stage, not the one on prep day. On any
other run the first node already checked the machine, and the generation
probe (up to 120 s) never runs twice.

A refusal raises ``PreflightError`` out of ``graph.invoke``; the caller (API,
CLI) turns it into an error state or an exit code. Non-blocking warnings are
returned in ``preflight_warnings`` and noted for the operator, exactly as the
API did around the graph before step 4.
"""

from __future__ import annotations

from factory.infra import progress
from factory.infra.preflight import PreflightError, preflight  # noqa: F401  (re-exported)


def request_of(state: dict) -> dict | None:
    """Normalise the ``preflight`` state field into ``{"strict", "timer"}``."""
    asked = state.get("preflight")
    if not asked:
        return None
    if asked is True:
        return {"strict": True, "timer": True}
    return {"strict": bool(asked.get("strict", True)),
            "timer": bool(asked.get("timer", True))}


def preflight_node(state: dict) -> dict:
    asked = request_of(state)
    if asked is None:
        return {}
    progress.phase("Préflight")
    warnings = preflight(strict=asked["strict"], timer=asked["timer"])
    for w in warnings:
        progress.note(f"préflight : {w}")
    return {"preflight_warnings": list(warnings)}


def live_preflight_node(state: dict) -> dict:
    if not state.get("prepared_from"):
        return {}
    return preflight_node(state)
