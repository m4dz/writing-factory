#!/usr/bin/env python3
"""Progress display and countdown for the stage demo.

Not cosmetic: a chapter takes about seventeen minutes to generate, during
which the CLI used to show NOTHING, the output arriving at the end. In front
of a room a frozen screen reads as a crashed machine, the exact opposite of
what the demo must show.

Two design principles:

1. **Graph nodes know nothing of the display.** They call `phase()`, `note()`,
   `tokens()` against a global event sink, which decides whether to draw an
   ANSI panel, write flat lines, or stay silent. An inactive `Progress` (the
   default) makes every call free, so the graph is instrumented without a
   conditional anywhere.

2. **Show the WORK, not only the time.** A countdown running while a 1 min 45
   call blocks proves that time passes, not that the machine computes. Tokens
   arriving one by one do; hence the hook into Ollama's streaming
   (`OllamaClient.chat_turns(on_token=…)`).
"""

import shutil
import sys
import time

from factory.settings import settings

# Stage budget, in minutes: `settings.stage_budget_min`. The keynote harvests
# the chapter ~25 min after launching it (lowered from 35' to 25' the 2026-08-06).

_ANSI_CLEAR_LINE = "\x1b[2K"
_ANSI_LINE_START = "\r"

# Progress bands per phase, as a fraction of the total work. The bounds are
# coarse by design: they move a bar for the room, they do not predict an end.
# They live HERE, not in the graph nodes, so a rehearsal can recalibrate them
# without touching the pipeline. Reference run (17.0 min, 4 scenes): the plan
# weighs ~2 min, writing ~7, review ~5, QA ~3.
BANDS = {
    "Préflight": (0.00, 0.01),
    "État narratif": (0.01, 0.01),
    "Invariants de la bible": (0.01, 0.03),
    # Plan and « Plan d'entrées » are two PATHS of the same node (imposed vs
    # generated brief): same band, only one is emitted per run.
    "Plan": (0.03, 0.08),
    "Plan d'entrées": (0.03, 0.08),
    "Contrôle du plan contre la bible": (0.08, 0.12),
    "Écriture": (0.12, 0.50),
    # Accumulation / Glissement: SUB-STEPS of one writing entry, inside the
    # write→accumulate→drift loop. DELIBERATELY without a band: they keep the
    # value reached by « Écriture » (whose i/n drives the bar). A band of their
    # own would jump out of step with the loop, then the monotonic guard would
    # freeze the writing of the following entries.
    "Relecture": (0.50, 0.72),
    "Bascule des modèles": (0.72, 0.73),
    "Réparation linguistique": (0.73, 0.85),
    "Assemblage": (0.85, 0.90),
    "Pose des gestes": (0.90, 0.94),
    "Cohérence par faits": (0.94, 0.97),
    "Restitution": (0.97, 1.00),
}

# Phases as the deck knows them (the deck's GenStatus contract). Our internal
# granularity is finer; it is projected.
DECK_PHASES = {
    "Restitution": "tts",
}


class Cancelled(RuntimeError):
    """The current job was cancelled by the operator.

    Raised from `phase()`, that is at the graph's NODE BOUNDARIES: a Python
    thread cannot be killed cleanly, but it can refuse to move to the next
    step. The worst delay is one model call (~2 min for a scene), not
    forever.
    """


def _mmss(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:d}:{seconds % 60:02d}"


class Progress:
    """Progress event sink.

    Three modes, chosen at construction:
      * `active=False`: silent, zero cost. The default, so tests and
        programmatic calls keep their behaviour.
      * interactive terminal: a one-line panel redrawn in place.
      * redirected output: flat timestamped lines, one per event. A bar
        redrawn in place would put thousands of `\\r` in a log file,
        unreadable; and `> run.log` is exactly the use case.
    """

    def __init__(self, *, active: bool = False, budget_min: float | None = None,
                 stream=None):
        self.active = active
        if budget_min is None:
            budget_min = settings.stage_budget_min
        self.budget = budget_min * 60
        self.stream = stream or sys.stdout
        self.interactive = active and self.stream.isatty()
        self.t0 = time.time()
        self.current_phase = ""
        self.detail = ""
        self.deck_phase = "generating"   # projection onto the deck's contract
        self.advancement = 0.0            # fraction 0..1, monotonic
        self.gen_toks = 0          # tokens of the whole chapter
        self.cancelled = False              # operator stop request
        # Called at each phase change with the sink as argument. Serves the
        # phone notifications without this module knowing the network.
        self.observer = None
        self.notes: list[str] = []       # notable events, for the status payload
        self._call_toks = 0       # tokens of the current call
        self._last_draw = 0.0
        self._call_t = 0.0

    # --- API called by the graph ---------------------------------------------

    def phase(self, title: str, detail: str = "", *,
              i: int | None = None, n: int | None = None) -> None:
        """Change phase (plan, writing scene 2/4, review, QA…).

        `i`/`n` place the step within its band (scene 2 of 4). Nodes give
        them when they know them; without them the phase is worth the start
        of its band.

        This runs EVEN when the display is inactive: the status payload must
        report progress when the HTTP server writes nothing to a terminal.
        """
        if self.cancelled:
            raise Cancelled("génération annulée par l'opérateur")
        start, end = BANDS.get(title, (self.advancement, self.advancement))
        part = (i / n) if (i is not None and n) else 0.0
        # Monotonic: a progress that recedes (replanning, unknown phase) reads
        # as a bug from the room.
        self.advancement = max(self.advancement, start + (end - start) * part)
        self.current_phase = title
        self.detail = detail
        self.deck_phase = DECK_PHASES.get(title, "generating")
        if self.observer:
            try:
                self.observer(self)
            except Exception:                          # noqa: BLE001
                pass    # a failing observer never stops a generation
        if not self.active:
            return
        self._call_toks = 0
        self._call_t = time.time()
        if self.interactive:
            self._draw(force=True)
        else:
            self._line(f"{title}" + (f" — {detail}" if detail else ""))

    def note(self, message: str) -> None:
        """One-off event worth seeing (replanning, repair…)."""
        # Kept even when inactive: these are what the status payload and the
        # phone notifications relay, and the HTTP server has no terminal.
        # Bounded, or a long run accumulates them without end.
        self.notes.append(message)
        del self.notes[:-20]
        if not self.active:
            return
        if self.interactive:
            self.stream.write(_ANSI_CLEAR_LINE + _ANSI_LINE_START)
            self.stream.write(f"  · {message}\n")
            self._draw(force=True)
        else:
            self._line(f"  · {message}")

    def on_token(self, fragment: str, cumulative: int) -> None:
        """Streaming callback: a fragment just arrived."""
        if not self.active:
            return
        self._call_toks = cumulative
        self.gen_toks += 1
        if self.interactive:
            self._draw()

    def end(self) -> None:
        """Give the line back to the terminal (the panel must not stick)."""
        if self.active and self.interactive:
            self.stream.write(_ANSI_CLEAR_LINE + _ANSI_LINE_START)
            self.stream.flush()

    def snapshot(self) -> dict:
        """Current state, for `GET /runs/<id>/status` and the notifications.

        `phase` is the value of the deck's GenStatus contract (`generating` |
        `tts` | `ready`); everything else is additive and the deck can ignore
        it without losing anything, which is the condition for enriching the
        display without breaking the contract.
        """
        return {
            "phase": self.deck_phase,
            "ready": False,
            "progress": round(self.advancement, 3),
            "label": self.current_phase,
            "detail": self.detail,
            "elapsed_s": int(time.time() - self.t0),
            "budget_s": int(self.budget),
            "gen_toks": self.gen_toks,
            "notes": list(self.notes[-5:]),
        }

    # --- rendering -----------------------------------------------------------

    def _line(self, text: str) -> None:
        elapsed = time.time() - self.t0
        self.stream.write(f"[{_mmss(elapsed)} / {_mmss(self.budget)}] {text}\n")
        self.stream.flush()

    def _draw(self, *, force: bool = False) -> None:
        # Ten tokens per second would redraw ten times a second, invisible and
        # costly in writes: capped at 5 Hz.
        now = time.time()
        if not force and now - self._last_draw < 0.2:
            return
        self._last_draw = now

        elapsed = now - self.t0
        remaining = self.budget - elapsed
        speed = self._call_toks / max(0.1, now - self._call_t)
        # Overrun is shown plainly rather than stuck at zero: onstage, better
        # to know we are at +2:30 than to believe 0:00 remains.
        clock = (f"reste {_mmss(remaining)}" if remaining >= 0
                   else f"DÉPASSÉ de {_mmss(-remaining)}")
        line = (
            f"⏱ {_mmss(elapsed)} / {_mmss(self.budget)} ({clock})  "
            f"│ {self.current_phase}"
            + (f" {self.detail}" if self.detail else "")
            + f"  │ {self._call_toks} tok à {speed:.1f} tok/s"
            + f"  │ total {self.gen_toks}"
        )
        width = shutil.get_terminal_size((100, 24)).columns
        self.stream.write(_ANSI_CLEAR_LINE + _ANSI_LINE_START + line[:width - 1])
        self.stream.flush()


# Global sink. The graph uses it without knowing it: inactive by default, so
# importing the graph from a test displays nothing.
SINK = Progress(active=False)


def install(sink: Progress) -> None:
    """Replace the global sink (called by `factory generate` and the API)."""
    global SINK
    SINK = sink


def phase(title: str, detail: str = "", *,
          i: int | None = None, n: int | None = None) -> None:
    SINK.phase(title, detail, i=i, n=n)


def note(message: str) -> None:
    SINK.note(message)


def on_token(fragment: str, cumulative: int) -> None:
    SINK.on_token(fragment, cumulative)


def token_sink():
    """Streaming callback to hand to the Ollama client, or None when the display
    is inactive, so the non-streamed mode stays the default path."""
    return on_token if SINK.active else None
