#!/usr/bin/env python3
"""Chapter rendering in a cloned voice (Qwen3-TTS via MLX), LOCAL (ADR-0012).

Last step of the demo pipeline: the clone picks up the reading where the
human voice stops (see `pipeline/assembly.py` for the switch marker).

Why this module exists while `../TTS/lire_chapitre.py` already renders: that
script is a CLI, not a library. Its render loop lives in `main()`, glued to
`argparse`, and its loader calls `sys.exit()` when the marker is missing.
Inside a server `SystemExit` is a `BaseException`: it passes through `except
Exception`, kills the thread silently and leaves the job in "generating"
forever. So it is not imported.

What the two repositories share is not code but **the voice**
(`voix/ma-voix.wav` and its transcription) and the model id. Their script and
this module are both thin clients of `mlx_audio`, fifteen lines around
`load_model().generate()`. `TTS/RUNBOOK.md` stays the reference for the
parameters (model, short segments, pause, language); when one moves there, it
moves here.

The `mlx_audio` import is LAZY, inside the render function: this module is
imported by a server that lives for hours and synthesises once; it has no
reason to carry `mlx` + `transformers` in memory all that time.
"""

import time
from pathlib import Path

from factory.infra import progress
from factory.pipeline.assembly import audio_excerpt
from factory.settings import settings

# Model, voice reference (asset of the neighbouring TTS repository: the ONLY
# cross-repository dependency, read-only), segment size (short = stable
# prosody, no drift of the clone) and pause: `settings.tts_*`, `settings.voice_dir`.
DEFAULT_SAMPLE_RATE = 24_000


class TTSUnavailable(RuntimeError):
    """Rendering impossible (voice reference missing, mlx-audio not installed…).

    An ORDINARY exception, not a `sys.exit`: the caller is a server, it must
    be able to catch it, log it and let the deck fall back silently.
    """


def split_segments(text: str, *, max_chars: int | None = None) -> list[str]:
    """Split into short segments, never in the middle of a sentence."""
    from factory.text import sentence_ends

    if max_chars is None:
        max_chars = settings.tts_max_chars
    segments: list[str] = []
    for para in text.split("\n\n"):
        para = " ".join(para.split())
        if not para:
            continue
        if len(para) <= max_chars:
            segments.append(para)
            continue
        block, start = "", 0
        for end in sentence_ends(para) + [len(para)]:
            sentence = para[start:end].strip()
            start = end
            if not sentence:
                continue
            if block and len(block) + len(sentence) + 1 > max_chars:
                segments.append(block)
                block = sentence
            else:
                block = f"{block} {sentence}".strip()
        if block:
            segments.append(block)
    return segments


def _reference() -> tuple[str, str]:
    """Path of the reference WAV and its transcription. Raises when absent."""
    voice_dir = settings.voice_dir
    wav, txt = voice_dir / "ma-voix.wav", voice_dir / "ma-voix.txt"
    if not wav.exists() or not txt.exists():
        raise TTSUnavailable(
            f"référence vocale manquante dans {voice_dir} "
            "(ma-voix.wav + ma-voix.txt attendus)"
        )
    return str(wav), txt.read_text(encoding="utf-8").strip()


def render(text: str, output: Path, *, model_id: str | None = None,
           pause_s: float | None = None) -> dict:
    """Synthesise `text` in the reference voice, write a WAV, return the
    metrics (audio duration, compute duration, real-time factor).

    The real-time factor is THE measure that counts: it says whether the
    synthesis fits in the tail of the countdown. The RUNBOOK announces ~1×;
    measured here 1.57× warm, 0.60× cold (ADR-0012).
    """
    model_id = model_id or settings.tts_model
    pause_s = settings.tts_pause_s if pause_s is None else pause_s
    ref_audio, ref_text = _reference()
    segments = split_segments(text)
    if not segments:
        raise TTSUnavailable("aucun texte à lire après la bascule")

    try:
        import numpy as np
        import soundfile as sf
        from mlx_audio.tts.utils import load_model
    except ImportError as exc:
        raise TTSUnavailable(
            f"dépendances TTS absentes du venv ({exc}). "
            "pip install mlx-audio soundfile numpy"
        ) from exc

    progress.phase("Restitution", "préparation")
    model = load_model(model_id)

    sr = DEFAULT_SAMPLE_RATE
    tracks = []
    t0 = time.time()
    for i, segment in enumerate(segments, 1):
        progress.phase("Restitution",
                       f"segment {i}/{len(segments)}", i=i, n=len(segments))
        for result in model.generate(
            text=segment, ref_audio=ref_audio, ref_text=ref_text,
            lang_code="french",
        ):
            tracks.append(np.asarray(result.audio))
            sr = getattr(result, "sample_rate", sr)
        tracks.append(np.zeros(int(sr * pause_s), dtype=np.float32))

    audio = np.concatenate(tracks)
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, audio, sr)

    compute_s = time.time() - t0
    duration = len(audio) / sr
    # Return the GPU memory: this process lives for hours afterwards, and
    # memory pressure is this machine's enemy number one.
    try:
        import mlx.core as mx

        mx.clear_cache()
    except Exception:                                   # noqa: BLE001
        pass

    # The clone's rate (`settings.audio_words_per_minute`) is an ASSUMPTION
    # (190 words/min first, from a 117-word sample; 177 measured since,
    # ADR-0013) that converts the duration the deck wants into a word count.
    # If it is wrong the excerpt comes out too short or too long, and nobody
    # notices before the stage, unless it is said here.
    cible_s = settings.audio_seconds
    gap = duration - cible_s
    if abs(gap) > settings.audio_tolerance_s:
        progress.note(
            f"durée de lecture hors cible : {duration:.0f} s au lieu de "
            f"{cible_s:.0f} s ({gap:+.0f} s). Recalibrer "
            f"AUDIO_WORDS_PER_MINUTE (actuel {settings.audio_words_per_minute:.0f} mots/min, "
            f"réel {len(text.split()) / (duration / 60):.0f})."
        )

    return {
        "segments": len(segments),
        "audio_s": round(duration, 1),
        "cible_s": cible_s,
        "debit_mots_min": round(len(text.split()) / (duration / 60), 1),
        "calcul_s": round(compute_s, 1),
        "facteur_temps_reel": round(duration / compute_s, 2) if compute_s else 0.0,
        "sample_rate": sr,
        "sortie": str(output),
    }


def render_chapter(markdown: str, output: Path, **kwargs) -> dict:
    """Render the post-switch, bounded portion of a Markdown chapter."""
    return render(audio_excerpt(markdown), output, **kwargs)
