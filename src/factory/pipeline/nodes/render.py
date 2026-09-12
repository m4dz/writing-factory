"""Last node: assemble the chapter Markdown and, when asked, write it and
render the read excerpt in the cloned voice.

Assembly (both stage markers) is deterministic and always runs: the chapter
text is the run's deliverable and lives in the state as ``chapter_md``. The
kwargs come from the state field ``assembly`` (chapter knowledge: switch on
the second header, imposed fall) — empty means the sentence rule.

Writing and voice rendering run only when the state field ``render`` is true.
The chapter is written first; the TTS then runs after the QA model is
unloaded (nothing left for Qwen, 4.8 GB better spent on the voice model). A
TTS failure is ordinary: the chapter stays valid on disk, ``audio`` is None
and the operator gets a note — the per-resource fallback the deck relies on.
"""

from __future__ import annotations

from pathlib import Path

from factory.infra import progress
from factory.infra.ollama import unload
from factory.infra.tts import render_chapter
from factory.pipeline.assembly import assemble
from factory.settings import settings

CHAPTER_FILE = "chapitre.md"
AUDIO_FILE = "chapitre.wav"


def chapter_path(directory: Path | None = None) -> Path:
    return (directory or settings.output_dir) / CHAPTER_FILE


def audio_path(directory: Path | None = None) -> Path:
    return (directory or settings.output_dir) / AUDIO_FILE


def render_node(state: dict) -> dict:
    scenes = state.get("repaired") or state.get("scenes") or []
    chapter_md = assemble(scenes, **(state.get("assembly") or {}))
    if not state.get("render"):
        return {"chapter_md": chapter_md}

    # The run's directory when there is a run (ADR-0003), `output/` otherwise.
    target = Path(state["artifacts_dir"]) if state.get("artifacts_dir") else settings.output_dir
    target.mkdir(parents=True, exist_ok=True)
    chapter_path(target).write_text(chapter_md, encoding="utf-8")
    progress.phase("Restitution", "préparation")
    unload(settings.qa_model)
    try:
        audio = render_chapter(chapter_md, audio_path(target))
    except Exception as exc:                        # noqa: BLE001
        progress.note(f"lecture indisponible : {exc} — chapitre servi sans lecture")
        return {"chapter_md": chapter_md, "audio": None}
    progress.note(
        f"lecture prête : {audio['audio_s']:.0f} s restituées en "
        f"{audio['calcul_s']:.0f} s (×{audio['facteur_temps_reel']})"
    )
    return {"chapter_md": chapter_md, "audio": audio}
