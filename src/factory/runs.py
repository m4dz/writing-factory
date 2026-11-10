"""The run registry: one directory per generation under `experiments/runs/`.

A run is (chapter spec, seed, configuration overrides, commit) — ADR-0003,
ADR-0005. Its directory is the registry: `manifest.yaml` (identity, resolved
configuration, model tags, status, timings from both clocks), `chapitre.md`,
`chapitre.wav`, `prompts.md` (every prompt served to the model), `lint.md`
(the lint grid line), `checkpoints.sqlite` (the graph's checkpoints, thread =
run id). A prepared run (`factory prepare`, manifest `kind: prepared`) stops at
the leader gate and adds `plan.md` (the approved plan, what the stage shows)
and `plan-report.md` (its check report); a run resumed from it records
`prepared_from` and carries a copy of `plan.md`. The API reads runs from disk and holds no chapter in memory;
`factory generate` writes the same directories.
"""

from __future__ import annotations

import hashlib
import os
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
               "beats_n", "pruning_enabled", "accumulation_enabled", "beat_context", "beat_form",
               "audio_seconds", "switch_after_sentences",
               "stage_budget_min")

# Overrides that take one of a closed set of values.
CHOICES = {"beat_context": ("blind", "map", "plan"), "beat_form": ("prose", "nominal")}

# Former override names, still accepted so earlier runs replay: name → (key, value).
ALIASES = {("beats_see_movement", True): ("beat_context", "map"),
           ("beats_see_movement", False): ("beat_context", "blind")}

# Run options a command line may pass to `spec.state()` for one run: the
# keyword overrides the spec already accepts, never spec content.
OPTIONS = ("rag", "micro_nodes", "segments")

# `prepared` is terminal too: a prepared run never moves again, it is resumed
# as new runs.
TERMINAL = ("ready", "error", "cancelled", "prepared")


class RunError(ValueError):
    """Bad run id, unknown run, or an override outside the whitelist."""


class FingerprintError(RuntimeError):
    """A prepared plan's dependencies changed since its approval.

    Raised before any node of the resumed run, handled where `PreflightError`
    is: CLI exit code 1, API `state: error`. `items` names each difference
    (`commit`, `dirty`, `chapter`, `config.<key>`, `models.<name>`,
    `narrative_state`); the message says it in the operator's words.
    """

    def __init__(self, differences: list[tuple[str, str]]):
        self.items = [item for item, _ in differences]
        super().__init__("le plan préparé ne correspond plus à cette machine :\n"
                         + "\n".join(f"  - {line}" for _, line in differences))


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
    #                              | preparing | prepared
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

    @property
    def checkpoints_path(self) -> Path:
        return self.dir / "checkpoints.sqlite"

    @property
    def plan_path(self) -> Path:
        return self.dir / "plan.md"


def runs_root(root: Path | None = None) -> Path:
    return root or settings.runs_dir


def validate_overrides(overrides: dict | None) -> dict:
    out = {}
    for key, value in (overrides or {}).items():
        if key == "beats_see_movement" and value in (True, False) and not isinstance(value, str):
            key, value = ALIASES[(key, bool(value))]
        if key not in OVERRIDABLE:
            raise RunError(f"override refusé : « {key} » (autorisés : {', '.join(OVERRIDABLE)})")
        current = getattr(settings, key)
        # A boolean takes a boolean or 0/1, never a string: bool("false") is True.
        if isinstance(current, bool):
            if value not in (True, False, 0, 1) or isinstance(value, str):
                raise RunError(f"override « {key} » : valeur invalide {value!r} "
                               "(true/false attendu)")
            out[key] = bool(value)
            continue
        if key in CHOICES and value not in CHOICES[key]:
            raise RunError(f"override « {key} » : valeur invalide {value!r} "
                           f"(attendu : {' | '.join(CHOICES[key])})")
        try:
            out[key] = type(current)(value)
        except (TypeError, ValueError):
            raise RunError(f"override « {key} » : valeur invalide {value!r}") from None
    return out


def parse_pairs(pairs: list[str] | None, what: str) -> dict:
    """``["beats_n=1", "pruning_enabled=false"]`` → ``{"beats_n": "1", ...}``;
    booleans spelled true/false are converted, other values are left to the
    validator of their kind."""
    out: dict = {}
    for pair in pairs or []:
        key, sep, value = pair.partition("=")
        if not sep or not key.strip():
            raise RunError(f"{what} « {pair} » : attendu CLÉ=VALEUR")
        value = value.strip()
        out[key.strip()] = {"true": True, "false": False}.get(value.lower(), value)
    return out


def validate_options(options: dict | None) -> dict:
    out = {}
    for key, value in (options or {}).items():
        if key not in OPTIONS:
            raise RunError(f"option refusée : « {key} » (autorisées : {', '.join(OPTIONS)})")
        if not isinstance(value, bool):
            raise RunError(f"option « {key} » : true ou false attendu, reçu {value!r}")
        out[key] = value
    return out


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=paths.REPO_ROOT, capture_output=True,
                             timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.decode("utf-8", "replace") if out.returncode == 0 else None


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=paths.REPO_ROOT,
                              capture_output=True, text=True, timeout=5,
                              check=False).stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def resolved_config(overrides: dict | None = None) -> dict:
    keys = ("author_model", "qa_model", "embed_model", "num_ctx", "gesture_model",
            "gesture_temperature", "beats_n", "pruning_enabled", "accumulation_enabled",
            "beat_context", "beat_form", "switch_after_sentences",
            "audio_seconds", "audio_words_per_minute", "tts_model", "stage_budget_min")
    conf = {k: getattr(settings, k) for k in keys}
    conf.update(overrides or {})
    return conf


# --- prepared-plan fingerprint ------------------------------------------------
#
# What a prepared state depends on and the checkpoint does not hold. A plan
# resumed against changed code, chapter, configuration, models or index would
# report a run that never existed as such (doctrine 5): the resume recomputes
# the fingerprint and refuses on any difference, naming it.

CODE_DIR = "src/factory"


def code_dirty() -> str:
    """sha256 of the uncommitted changes to the package: tracked diffs and
    untracked files. A rehearsal-day fix not yet committed changes it."""
    digest = hashlib.sha256()
    digest.update((_git("diff", "HEAD", "--", CODE_DIR) or "").encode())
    for name in sorted((_git("ls-files", "--others", "--exclude-standard", "--", CODE_DIR)
                        or "").splitlines()):
        path = paths.REPO_ROOT / name
        if path.is_file():
            digest.update(name.encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def chapter_files(chapter: int) -> dict:
    """``{relative path: sha256}`` of every file of the chapter directory
    (spec, brief, storyboard): the refusal can name the file that moved."""
    from factory.chapter_spec import chapter_dirs
    directory = chapter_dirs().get(chapter)
    if directory is None:
        return {}
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith(".")}


def _ollama_tags() -> dict:
    """The body of Ollama's `/api/tags`."""
    import httpx
    resp = httpx.get(f"{settings.ollama_url}/api/tags", timeout=10)
    resp.raise_for_status()
    return resp.json()


def model_digests(config: dict) -> dict:
    """``{model: digest}`` for the models the run names (author, QA, gesture,
    embeddings, probe); ``None`` for a model Ollama does not have. A re-pulled
    model is another model. The embedding model counts: retrieval runs while
    writing, on stage, against an index built with the prep's vectors."""
    names = [config.get("author_model"), config.get("qa_model"),
             config.get("gesture_model") or config.get("author_model"),
             config.get("embed_model"), settings.probe_model]
    try:
        tags = _ollama_tags()
    except Exception as exc:                            # noqa: BLE001
        raise FingerprintError([("models", f"Ollama injoignable ({type(exc).__name__}) : "
                                           "empreintes des modèles illisibles")]) from exc
    known = {}
    for m in tags.get("models") or []:
        for key in (m.get("name"), m.get("model")):
            if key:
                known[key] = m.get("digest")
    out = {}
    for name in dict.fromkeys(n for n in names if n):
        out[name] = known.get(name, known.get(f"{name}:latest"))
    return out


def narrative_chunk_id(chapter: int) -> str:
    from factory.chapter_spec.narrative_state import NARRATOR_DOC_ID
    from factory.retrieval.context import STATE_SECTION
    return f"{NARRATOR_DOC_ID}::{STATE_SECTION}::ch{chapter:02d}"


def narrative_chunk(chapter: int) -> str | None:
    """sha256 of the chapter's narrative-state chunk in Chroma, None if absent."""
    from factory.retrieval import context as retrieval
    got = retrieval._collection().get(ids=[narrative_chunk_id(chapter)], include=["documents"])
    docs = got.get("documents") or []
    return hashlib.sha256(docs[0].encode()).hexdigest() if docs else None


def fingerprint(run: Run, state: dict) -> dict:
    """The fingerprint of a prepared run's final state. The narrative-state
    chunk counts only when the prep indexed one (`narrative_state_path`)."""
    config = resolved_config(run.overrides)
    return {
        "commit": (_git("rev-parse", "HEAD") or "unknown").strip(),
        "dirty": code_dirty(),
        "chapter": chapter_files(run.chapter),
        "config": config,
        "models": model_digests(config),
        "narrative_state": (narrative_chunk(run.chapter)
                            if state.get("narrative_state_path") else None),
    }


def check_fingerprint(prepared: Run, state: dict) -> None:
    """Recompute the prepared run's fingerprint; raise `FingerprintError`
    naming every difference."""
    recorded = prepared.manifest.get("fingerprint") or {}
    if not recorded:
        raise FingerprintError([("fingerprint", f"run {prepared.id} : aucune empreinte "
                                                "consignée (préparation non approuvée ?)")])
    now = fingerprint(prepared, state)
    diff: list[tuple[str, str]] = []
    if now["commit"] != recorded.get("commit"):
        diff.append(("commit", f"commit : {str(recorded.get('commit'))[:12]} → "
                               f"{now['commit'][:12]}"))
    if now["dirty"] != recorded.get("dirty"):
        diff.append(("dirty", f"code non commité sous {CODE_DIR} : modifié depuis la préparation"))
    was = recorded.get("chapter") or {}
    moved = sorted(k for k in set(was) | set(now["chapter"])
                   if was.get(k) != now["chapter"].get(k))
    if moved:
        diff.append(("chapter", f"chapitre {prepared.chapter} : {', '.join(moved)} "
                                "modifié(s) depuis la préparation"))
    was = recorded.get("config") or {}
    for key in sorted(set(was) | set(now["config"])):
        if was.get(key) != now["config"].get(key):
            diff.append((f"config.{key}", f"configuration « {key} » : {was.get(key)!r} → "
                                          f"{now['config'].get(key)!r}"))
    was = recorded.get("models") or {}
    for name in sorted(set(was) | set(now["models"])):
        before, after = was.get(name), now["models"].get(name)
        if before != after:
            what = ("absent d'Ollama" if after is None
                    else f"empreinte {str(before)[:19]} → {str(after)[:19]}")
            diff.append((f"models.{name}", f"modèle {name} : {what}"))
    if now["narrative_state"] != recorded.get("narrative_state"):
        what = "absent de Chroma" if now["narrative_state"] is None else "modifié"
        diff.append(("narrative_state", f"état narratif {narrative_chunk_id(prepared.chapter)} : "
                                        f"{what}"))
    if diff:
        raise FingerprintError(diff)


def create_run(chapter: int, slug: str, *, seed: int, overrides: dict | None = None,
               root: Path | None = None, now: datetime | None = None,
               extra: dict | None = None) -> Run:
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
        **(extra or {}),
    }
    write_manifest(run)
    return run


def run_config(run: Run) -> dict:
    """The graph config of a run: its own checkpoint thread."""
    from factory.pipeline.checkpoint import thread_config
    return thread_config(run.id)


def open_checkpointer(run: Run, *, read_only: bool = False):
    """The run's SQLite saver (a context manager). Imported lazily: the
    indexer container has no LangGraph."""
    from factory.pipeline.checkpoint import open_saver
    return open_saver(run.checkpoints_path, read_only=read_only)


def write_manifest(run: Run, **fields) -> None:
    run.manifest.update(fields)
    if "status" in fields:
        run.status = fields["status"]
    # Atomic: the API reads manifests while the worker writes them, and a
    # truncated file read mid-write made a live run answer 404.
    target = run.dir / "manifest.yaml"
    partial = run.dir / ".manifest.yaml.partial"
    partial.write_text(yaml.safe_dump(_plain(run.manifest), allow_unicode=True, sort_keys=False),
                       encoding="utf-8")
    os.replace(partial, target)


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
    if data.get("kind") not in ("run", "prepared"):
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


def latest_prepared(chapter: int | None, root: Path | None = None) -> Run | None:
    """The newest run with status `prepared` (of that chapter, when given)."""
    return next((r for r in list_runs(root) if r.status == "prepared"
                 and (chapter is None or r.chapter == chapter)), None)


def resolve_prepared(token, chapter: int | None, root: Path | None = None) -> Run:
    """The prepared run a resume names: a whitelisted id or `latest`. Raises
    `RunError` with the reason (unknown, not prepared, other chapter)."""
    if not isinstance(token, str) or not token:
        raise RunError("prepared : identifiant de run ou « latest » attendu")
    if token == "latest":
        run = latest_prepared(chapter, root)
        if run is None:
            raise RunError("aucun run préparé"
                           + (f" pour le chapitre {chapter}" if chapter is not None else ""))
        return run
    if not RUN_ID.match(token):
        raise RunError(f"prepared : identifiant de run invalide « {token} »")
    run = find_run(token, root)
    if run is None:
        raise RunError(f"prepared : run inconnu « {token} »")
    if run.status != "prepared":
        raise RunError(f"run {run.id} non préparé (état « {run.status} »)")
    if chapter is not None and run.chapter != chapter:
        raise RunError(f"run {run.id} préparé pour le chapitre {run.chapter}, pas {chapter}")
    return run


def create_resumed_run(prepared: Run, *, seed: int, root: Path | None = None) -> Run:
    """A NEW run resuming a prepared one, beside it. The prepared run is never
    consumed: rehearsals and the stage resume the same approved plan. Its
    configuration is the prepared one; `plan.md` is copied so the deck reads
    the plan from the run it launched."""
    from factory.chapter_spec import load_chapter
    run = create_run(prepared.chapter, load_chapter(prepared.chapter).slug, seed=seed,
                     overrides=prepared.overrides, root=root or prepared.dir.parent,
                     extra={"prepared_from": prepared.id, "prepared_seed": prepared.seed,
                            "fingerprint": prepared.manifest.get("fingerprint")})
    if prepared.plan_path.is_file():
        run.plan_path.write_bytes(prepared.plan_path.read_bytes())
    return run


def render_plan(chapter: int, plan: list[str]) -> str:
    """`plan.md`: the approved plan alone, what the stage shows."""
    lines = [f"# Plan — chapitre {chapter}", ""]
    lines += [f"{n}. {beat}" for n, beat in enumerate(plan, 1)]
    return "\n".join(lines) + "\n"


def write_plan(run: Run, final: dict) -> None:
    """`plan.md` and `plan-report.md` (the check report: machinery, never
    shown) of a prepared run."""
    run.plan_path.write_text(render_plan(run.chapter, list(final.get("plan") or [])),
                             encoding="utf-8")
    report = (final.get("plan_report") or "").rstrip() or "(aucun contrôle : plan imposé)"
    (run.dir / "plan-report.md").write_text(
        f"# Contrôle du plan — chapitre {run.chapter}\n\n{report}\n", encoding="utf-8")


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
        if c.get("start"):
            out.append("### début de la réponse (le modèle le continue)\n\n```\n"
                       + str(c["start"]).rstrip() + "\n```\n")
    return "\n".join(out).rstrip() + "\n"


def render_variants(variants: list[dict]) -> str:
    """`variants.md`: every best-of variant drawn, before selection and pruning."""
    out = [f"# Variants tirés — {len(variants)}", ""]
    for v in variants:
        mark = " — RETENU" if v.get("winner") else ""
        defects = ", ".join(v.get("defects") or []) or "aucun"
        out.append(f"## entrée {v['entry']} / {v['beat']} / variant {v['variant']}{mark}\n")
        out.append(f"score {v['score']} — défauts : {defects}\n")
        out.append("```\n" + str(v.get("text", "")).rstrip() + "\n```\n")
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
        variants = final.get("beat_variants") or []
        if variants:
            (run.dir / "variants.md").write_text(render_variants(variants), encoding="utf-8")
            fields["variants"] = {"drawn": len(variants),
                                  "with_defects": sum(1 for v in variants if v.get("defects"))}
        text = final.get("chapter_md") or ""
        if text:
            from factory.eval.lint import analyze, report
            (run.dir / "lint.md").write_text(report(analyze(text), title=run.id) + "\n",
                                            encoding="utf-8")
    if calls is not None:
        run.prompts_path.write_text(render_prompts(calls), encoding="utf-8")
    write_manifest(run, **fields)
