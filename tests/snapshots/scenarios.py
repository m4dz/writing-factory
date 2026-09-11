"""The generation scenarios whose served prompts are frozen as golden files.

Three scenarios cover every writing strategy and both plan paths:

- ``ch7``: chapter 7 exactly as the API generates it (``load_chapter(7).state()``): plan
  imposed by the brief, entry 1 single call with best-of-3, entry 2 in three
  bounded beats with best-of-3, gestures on entry 2 only, drift passage from
  the brief, fall posed by code.
- ``ch2-s7-score``: chapter 2, stage S7 scored run (``factory calibrate --stage S7``,
  run S7-1): single entry, plan short-circuited, three segments with stations,
  accumulation and drift from the bank.
- ``ch2-s7-chapter``: same stage, the full chapter (run S7-C): three entries,
  plan node with fact derivation and plan check, coherence on three scenes.

Both states come from ``chapters/NN-slug/spec.yaml`` through the loader
(step 5); the golden files were produced by the former Python constructions
and did not move.
"""

from __future__ import annotations

from dataclasses import dataclass

from factory.chapter_spec import load_chapter


@dataclass(frozen=True)
class Scenario:
    name: str
    state: dict
    assembly: dict          # kwargs for assembly.assemble

    @property
    def seed(self) -> int:
        return self.state["seed"]


SEED = 424242


def all_scenarios() -> list[Scenario]:
    """Both chapters through the spec loader; the states are those the API
    (chapter 7) and the calibration stage S7 (chapter 2) build."""
    ch7 = load_chapter(7)
    ch2 = load_chapter(2)
    return [
        Scenario("ch7", ch7.state(seed=SEED), dict(ch7.assembly)),
        Scenario("ch2-s7-score",
                 ch2.state(seed=SEED, brief=ch2.entry_brief, entry_count=1), {}),
        Scenario("ch2-s7-chapter", ch2.state(seed=SEED), {}),
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
