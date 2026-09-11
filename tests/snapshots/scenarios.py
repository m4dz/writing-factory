"""The generation scenarios whose served prompts are frozen as golden files.

Three scenarios cover every writing strategy and both plan paths:

- ``ch7``: chapter 7 exactly as the API generates it (``ch7.etat_ch7``): plan
  imposed by the brief, entry 1 single call with best-of-3, entry 2 in three
  bounded beats with best-of-3, gestures on entry 2 only, drift passage from
  the brief, fall posed by code.
- ``ch2-s7-score``: chapter 2, stage S7 scored run (``stage_runner.py --etage S7``,
  run S7-1): single entry, plan short-circuited, three segments with stations,
  accumulation and drift from the bank.
- ``ch2-s7-chapter``: same stage, the full chapter (run S7-C): three entries,
  plan node with fact derivation and plan check, coherence on three scenes.

The chapter 2 state reproduces the dict built in ``outillage/stage_runner.py``
(``main``). Step 5 replaces both constructions with the chapter spec loader
and must reproduce these golden files byte for byte.
"""

from __future__ import annotations

from dataclasses import dataclass

from factory.chapter_spec import chapter7 as ch7
from factory.tooling import stage_runner


@dataclass(frozen=True)
class Scenario:
    name: str
    state: dict
    assembly: dict          # kwargs for chapitre.assembler

    @property
    def seed(self) -> int:
        return self.state["seed"]


SEED = 424242


def _etat_s7(brief: str, *, mono: bool) -> dict:
    """The ``graph.invoke`` state of ``stage_runner.py`` for stage S7."""
    return {
        "brief": brief,
        "characters": ch7.NARRATOR, "rag": True,
        "expected_entries": 1 if mono else 3,
        "entry_specs": [],
        "imposed_plan": [],
        "prefix": stage_runner.ANCHOR_CH2,
        "micro_nodes": True,
        "segments": True,
        "seed": SEED,
        "chapter": 2,
        "drawn_approaches": [],
        "start_day": stage_runner.START_DAY,
        "start_number": stage_runner.START_NUMBER,
        "verdict": stage_runner.VERDICT_CH2,
        "active_objects": stage_runner.OBJECTS_CH2,
        "start_weather": stage_runner.START_WEATHER,
        "accumulation": "",
    }


def all_scenarios() -> list[Scenario]:
    return [
        Scenario("ch7", ch7.ch7_state(seed=SEED), dict(ch7.MARKERS_CH7)),
        Scenario("ch2-s7-score", _etat_s7(stage_runner.BRIEF_V4, mono=True), {}),
        Scenario("ch2-s7-chapter", _etat_s7(stage_runner.CHAPTER_GOAL_V4, mono=False), {}),
    ]


def run(scenario: Scenario, fake_model) -> dict:
    """Invoke the compiled graph on the scenario with the fake model installed."""
    from factory.pipeline.graph import build_graph

    fake_model.calls.clear()
    final = build_graph().invoke(scenario.state, config={"recursion_limit": 50})
    return final


def render_prompts(calls) -> str:
    """Every served prompt, in order, as one Markdown document."""
    out = []
    for n, c in enumerate(calls, 1):
        out.append(f"## call {n} — {c.role} — model={c.model} "
                   f"num_predict={c.num_predict} temperature={c.temperature}\n")
        out.append("### system\n\n```\n" + c.system.rstrip() + "\n```\n")
        out.append("### user\n\n```\n" + c.user.rstrip() + "\n```\n")
    return "\n".join(out).rstrip() + "\n"
