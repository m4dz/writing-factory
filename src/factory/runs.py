"""The run registry: one directory per generation under `experiments/runs/`.

A run is (chapter spec, seed, configuration overrides, commit) — ADR-0003,
ADR-0005. Its directory is the registry: `manifest.yaml` (identity, resolved
configuration, model tags, status, timings from both clocks), `chapitre.md`,
`chapitre.wav`, `prompts.md` (every prompt served to the model), `lint.md`
(the lint grid line). The API reads runs from disk and holds no chapter in
memory; `factory generate` writes the same directories.
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

from factory import paths
from factory.settings import settings

RUN_ID = re.compile(r"^\d{8}-\d{6}-ch\d{2}-[a-z0-9-]{1,40}$")

# Configuration keys a payload may override for one run: knobs of the machine,
# never spec fields (ADR-0005). Applied for the run's duration only.
OVERRIDABLE = ("author_model", "qa_model", "gesture_model", "num_ctx", "gesture_temperature",
               "beats_n", "pruning_enabled", "audio_seconds", "switch_after_sentences",
               "stage_budget_min", "write_temperature", "min_p", "top_p", "repeat_penalty")

TERMINAL = ("ready", "error", "cancelled")


class RunError(ValueError):
    """Bad run id, unknown run, or an override outside the whitelist."""


@dataclass
class Run:
    id: str
    dir: Path
    chapter: int
    slug: str
    seed: int
    overrides: dict = field(default_factory=dict)
    created: str = ""
    status: str = "queued"       # queued | generating | ready | error | cancelled
    manifest: dict = field(default_factory=dict)

    @property
    def chapter_path(self) -> Path:
        return self.dir / "chapitre.md"

    @property
    def audio_path(self) -> Path:
        return self.dir / "chapitre.wav"

    @property
    def prompts_path(self) -> Path:
        return self.dir / "prompts.md"


def runs_root(root: Path | None = None) -> Path:
    return root or settings.runs_dir


def validate_overrides(overrides: dict | None) -> dict:
    out = {}
    for key, value in (overrides or {}).items():
        if key not in OVERRIDABLE:
            raise RunError(f"override refusé : « {key} » (autorisés : {', '.join(OVERRIDABLE)})")
        current = getattr(settings, key)
        try:
            if isinstance(current, bool):
                out[key] = bool(value)
            elif current is None or value is None:      # optional float knobs (min_p, top_p…)
                out[key] = None if value is None else float(value)
            else:
                out[key] = type(current)(value)
        except (TypeError, ValueError):
            raise RunError(f"override « {key} » : valeur invalide {value!r}") from None
    return out


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=paths.REPO_ROOT,
                              capture_output=True, text=True, timeout=5,
                              check=False).stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def resolved_config(overrides: dict | None = None) -> dict:
    keys = ("author_model", "qa_model", "embed_model", "num_ctx", "gesture_model",
            "gesture_temperature", "beats_n", "pruning_enabled", "switch_after_sentences",
            "audio_seconds", "audio_words_per_minute", "tts_model", "stage_budget_min",
            "write_temperature", "min_p", "top_p", "repeat_penalty")
    conf = {k: getattr(settings, k) for k in keys}
    conf.update(overrides or {})
    return conf


def create_run(chapter: int, slug: str, *, seed: int, overrides: dict | None = None,
               root: Path | None = None, now: datetime | None = None) -> Run:
    """Make the run directory and its first manifest (status `queued`)."""
    overrides = validate_overrides(overrides)
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    short = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")[:40] or "chapitre"
    run_id = f"{stamp}-ch{chapter:02d}-{short}"
    directory = runs_root(root) / run_id
    n = 1
    while directory.exists():               # two runs the same second
        n += 1
        directory = runs_root(root) / f"{run_id[:-len(short)]}{short[:37]}-{n}"
    run_id = directory.name
    directory.mkdir(parents=True)
    run = Run(id=run_id, dir=directory, chapter=chapter, slug=slug, seed=seed,
              overrides=overrides,
              created=datetime.now(timezone.utc).isoformat(timespec="microseconds"))
    run.manifest = {
        "id": run.id, "kind": "run", "chapter": chapter, "slug": slug, "seed": seed,
        "created": run.created, "commit": git_commit(), "status": "queued",
        "overrides": dict(overrides), "config": resolved_config(overrides),
    }
    write_manifest(run)
    return run


def write_manifest(run: Run, **fields) -> None:
    run.manifest.update(fields)
    if "status" in fields:
        run.status = fields["status"]
    (run.dir / "manifest.yaml").write_text(
        yaml.safe_dump(_plain(run.manifest), allow_unicode=True, sort_keys=False),
        encoding="utf-8")


def _plain(value):
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def load_run(directory: Path) -> Run | None:
    manifest = directory / "manifest.yaml"
    if not RUN_ID.match(directory.name) or not manifest.is_file():
        return None
    data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
    if data.get("kind") != "run":
        return None
    return Run(id=directory.name, dir=directory, chapter=int(data.get("chapter") or 0),
               slug=str(data.get("slug") or ""), seed=int(data.get("seed") or 0),
               overrides=dict(data.get("overrides") or {}), created=str(data.get("created") or ""),
               status=str(data.get("status") or "unknown"), manifest=data)


def list_runs(root: Path | None = None) -> list[Run]:
    """Every run, newest first (creation time, then id)."""
    base = runs_root(root)
    if not base.is_dir():
        return []
    runs = [load_run(d) for d in base.iterdir() if d.is_dir()]
    return sorted((r for r in runs if r), key=lambda r: (r.created, r.id), reverse=True)


def find_run(run_id: str, root: Path | None = None) -> Run | None:
    """The run of that id, or None. The id is whitelisted before any file access."""
    if not RUN_ID.match(run_id or ""):
        return None
    return load_run(runs_root(root) / run_id)


def latest_run(root: Path | None = None) -> Run | None:
    runs = list_runs(root)
    return runs[0] if runs else None


class Clocks:
    """Both clocks of a run (ADR-0016): monotonic stops during sleep, wall does not."""

    def __init__(self):
        self.t_mono, self.t_wall = time.monotonic(), time.time()

    def read(self) -> dict:
        mono = round(time.monotonic() - self.t_mono, 1)
        wall = round(time.time() - self.t_wall, 1)
        return {"monotonic_s": mono, "wall_s": wall, "sleep_s": round(max(0.0, wall - mono), 1)}


def render_prompts(calls: list[dict]) -> str:
    """`prompts.md`: every prompt served to the model, in order."""
    out = [f"# Prompts servis — {len(calls)} appel(s)", ""]
    for n, c in enumerate(calls, 1):
        out.append(f"## appel {n} — model={c.get('model')} num_predict={c.get('num_predict')} "
                   f"temperature={c.get('temperature')} gen_toks={c.get('gen_toks')} "
                   f"wall_s={c.get('wall_s')}\n")
        out.append("### system\n\n```\n" + str(c.get("system", "")).rstrip() + "\n```\n")
        out.append("### user\n\n```\n" + str(c.get("user", "")).rstrip() + "\n```\n")
    return "\n".join(out).rstrip() + "\n"


def record_result(run: Run, final: dict | None, *, clocks: dict, calls: list[dict] | None,
                  collections: list[str], status: str, error: str | None = None) -> None:
    """Close the manifest and write the run's deliverables."""
    fields: dict = {"status": status, "timings": clocks, "collections": sorted(set(collections)),
                    "finished": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if error:
        fields["error"] = error
    if final:
        metrics = final.get("metrics") or []
        fields["metrics"] = {
            "calls": len(metrics),
            "gen_toks": sum(m.get("gen_toks", 0) for m in metrics),
            "ctx_need_max": max((m.get("ctx_need", 0) for m in metrics), default=0),
            "ctx_truncated": sum(1 for m in metrics if m.get("ctx_truncated")),
        }
        fields["scenes"] = len(final.get("repaired") or [])
        fields["warnings"] = list(final.get("warnings") or [])
        fields["plan_report"] = final.get("plan_report") or ""
        fields["coherence"] = final.get("coherence") or ""
        fields["audio"] = final.get("audio")
        fields["preflight_warnings"] = list(final.get("preflight_warnings") or [])
        text = final.get("chapter_md") or ""
        if text:
            from factory.eval.lint import analyze, report
            (run.dir / "lint.md").write_text(report(analyze(text), title=run.id) + "\n",
                                            encoding="utf-8")
    if calls is not None:
        run.prompts_path.write_text(render_prompts(calls), encoding="utf-8")
    write_manifest(run, **fields)
