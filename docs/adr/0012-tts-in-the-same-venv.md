# ADR-0012 — TTS in the orchestrator's venv; lazy import; a TTS failure never fails the job

Date: 2026-08-07. Status: accepted.

## Context

The cloned voice (Qwen3-TTS via `mlx-audio`) existed as a CLI in a
neighbouring repository (`../TTS/lire_chapitre.py`). Its render loop lives in
`main()` and its text loader calls `sys.exit()`. Inside a server, `SystemExit`
is a `BaseException`: it passes through `except Exception`, kills the thread
silently and leaves the job in "generating" forever.

## Decision

- TTS lives in `orchestrator/tts.py`, in the SAME venv as the orchestrator
  (`mlx-audio` declares `Requires-Python >= 3.10` and imports fine on our
  3.10.9). One venv to recreate on the day. Cost: +542 MB, no torch.
- The two repositories share the VOICE (`TTS/voix/`) and the model id, not
  code; both are thin clients of `mlx_audio`. `TTS/RUNBOOK.md` stays the
  reference for parameters.
- The import is LAZY, inside the render function: the server lives for hours
  and synthesises once.
- A TTS failure does NOT fail the job: the chapter is valid and served, only
  `/audio` stays at `204`. The contract freezes a fallback PER RESOURCE.
- Segments are short (≤ 400 characters, never cutting a sentence) with a
  0.6 s pause; the rendered duration is compared to the target and a note is
  emitted beyond 15 s of gap, with the measured rate.

## Consequences

- Measured on this machine: 1.57× real time warm, 0.60× cold. Preheat before
  the stage.
- The Qwen QA model is unloaded before rendering: 4.8 GB returned to the
  voice model beats a swap.
