"""The chapter specification: what a chapter IS, typed.

A chapter's content — calendar, verdict, active objects, stations, the fall of
the accumulation, the drift bank, assembly parameters, one spec per entry —
is data in ``chapters/NN-slug/spec.yaml`` (ADR-0002). This module is the
model the loader fills and the pipeline reads; nothing here knows a chapter
number, and no chapter's text lives here.

Absent fields leave the default pipeline behaviour unchanged: an entry with
no strategy follows the state's ``segments`` flag, an entry with no
``citation`` takes the chapter prefix, a chapter with no drift bank draws no
drift.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BeatSpec:
    name: str
    num_predict: int
    sentences_max: int
    instruction: str


@dataclass(frozen=True)
class BestOf:
    n: int
    criterion: str = ""           # scorer name in ``factory.pipeline.scorers``
    names: tuple[str, ...] = ()   # terms the served text must name (keyword scorer)
    drift: tuple[str, ...] = ()   # terms that mark a drift away from the entry


@dataclass(frozen=True)
class Drift:
    text: str
    position: str                 # the frontier, in French ("à la frontière ... les couverts")


@dataclass(frozen=True)
class EntrySpec:
    weekday: str | None = None
    number: int | None = None
    weather: str | None = None
    words: tuple[int, int] | None = None
    sentences_max: int | None = None
    citation: str | None = None   # None: the chapter prefix; "": no anchor at all
    gestures: bool = True
    strategy: str | None = None   # single | segments | beats | None (state default)
    beats: tuple[BeatSpec, ...] = ()
    best_of: BestOf | None = None
    movement: str = ""
    trajectory: tuple[str, ...] = ()
    material: tuple[str, ...] = ()
    vetos: str = ""
    form: dict = field(default_factory=dict)   # {"accumulation": absent|allowed, "verdict": absent|...}
    fall: str = ""
    drift: Drift | None = None

    def uses_segments(self, default: bool) -> bool:
        return self.strategy == "segments" if self.strategy else bool(default)


EMPTY_ENTRY = EntrySpec()


@dataclass(frozen=True)
class Calendar:
    weekday: str = "Mardi"
    number: int = 12
    weather: str = ""


@dataclass(frozen=True)
class DriftBank:
    approaches: tuple[str, ...] = ()
    facts: tuple[str, ...] = ()


@dataclass(frozen=True)
class Defaults:
    rag: bool = True
    micro_nodes: bool = True
    segments: bool = True


@dataclass(frozen=True)
class ChapterSpec:
    chapter: int
    slug: str
    narrator: tuple[str, ...]
    brief: str                          # the served chapter brief
    entry_count: int
    calendar: Calendar = Calendar()
    verdict: str = ""
    active_objects: str = ""
    prefix: str = ""                    # anchor quotation prefixed to every entry
    stations: tuple[str, ...] = ()
    accumulation_fall: str = ""
    drift_bank: DriftBank = DriftBank()
    drift_anchors: dict = field(default_factory=dict)   # {key: [phrases]}, see gestures
    assembly: dict = field(default_factory=dict)
    defaults: Defaults = Defaults()
    entries: tuple[EntrySpec, ...] = ()
    imposed_plan: tuple[str, ...] = ()  # one beat per entry, cut from the brief
    entry_brief: str = ""               # single-entry brief for scored calibration runs
    workshop_terms: tuple[str, ...] = ()  # workshop vocabulary found in a file brief (owner's call)

    def state(self, *, seed: int | None = None, brief: str | None = None,
              entry_count: int | None = None, rag: bool | None = None,
              micro_nodes: bool | None = None, segments: bool | None = None,
              prefix: str | None = None) -> dict:
        """The ``graph.invoke`` state of this chapter.

        Keyword overrides are run options (a calibration stage without RAG, a
        scored single-entry run), never chapter content. The seed is random by
        default for live runs and recorded in the run's frontmatter.
        """
        served = self.brief if brief is None else brief
        count = self.entry_count if entry_count is None else entry_count
        plan = list(self.imposed_plan) if brief is None else []
        return {
            "brief": served,
            "characters": list(self.narrator),
            "rag": self.defaults.rag if rag is None else rag,
            "expected_entries": count,
            "entry_specs": list(self.entries),
            "imposed_plan": plan,
            "prefix": self.prefix if prefix is None else prefix,
            "micro_nodes": self.defaults.micro_nodes if micro_nodes is None else micro_nodes,
            "segments": self.defaults.segments if segments is None else segments,
            "seed": seed if seed is not None else random.randrange(1, 10**6),
            "chapter": self.chapter,
            "drawn_approaches": [],
            "start_day": self.calendar.weekday,
            "start_number": self.calendar.number,
            "verdict": self.verdict,
            "active_objects": self.active_objects,
            "start_weather": self.calendar.weather,
            "accumulation": "",
            "assembly": dict(self.assembly),
            "stations": list(self.stations),
            "accumulation_fall": self.accumulation_fall,
            "drift_bank": {"approaches": list(self.drift_bank.approaches),
                           "facts": list(self.drift_bank.facts)},
            "drift_anchors": {k: list(v) for k, v in self.drift_anchors.items()},
        }
