#!/usr/bin/env python3
"""HTTP surface: one-worker queue, per-run routes, actor mode (ADR-0005, ADR-0014).

    factory serve            # listens at settings.api_host:settings.api_port

    POST /generate {chapter, seed?, overrides?}   202 {run_id}; queued, never refused
    GET  /runs/<id>/status|events|chapter|audio|prompts|manifest
    POST /runs/<id>/cancel                        `/runs/latest/…` aliases the newest
    POST /chat, GET /characters, /sessions, /session/<c>/<ts>, /acteur, /health

Two principles the deck's fallback policy imposes, which dictate the rest:

1. **The deck NEVER sees an error.** At any failure it falls back silently to
   its embedded assets. A refused preflight, a fallen model, an exception in
   the graph: all of it yields `204` for artifacts and `phase: error` in the
   status, never a 500 in the deck's face. The error must wake the OPERATOR
   (notifications), not the room.

2. **Artifacts live IN A RUN DIRECTORY before they are served.** `GET /runs/<id>/chapter`
   reads a file. If this server dies after the generation, the chapter is
   still there and a restart serves it again; keeping it in process memory
   would lose twenty minutes of compute to an unlucky Ctrl-C.
"""

import json
import random
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from factory.infra import notify
from factory.settings import settings
from factory.infra import progress
from factory import runs as run_registry
from factory.chapter_spec import ChapterSpecError, chapter_dirs, load_chapter
from factory.infra.ollama import client as model_client
from factory.retrieval import context as retrieval
from factory.pipeline.graph import build_graph
from factory.infra.preflight import PreflightError, report
from factory.runs import Run
from factory.retrieval.context import list_characters
from factory.roleplay.session import read_session, list_sessions

STATIC = Path(__file__).resolve().parent / "static"

# The talk's Slidev build, served AT THE ROOT: the build references its assets
# by ABSOLUTE path (`/assets/...`, `/favicon.svg`) and cannot be mounted under
# a prefix without a rebuild with a `base`. Happy consequence: the deck sits at
# the SAME origin as the API, so its fetches of `/runs/<id>/…` are same-origin,
# no CORS. The presentation machine loads the deck HERE and the API answers
# beside it, same host. Path: `settings.slides_dir`.

# MIME types for the static build. `mimetypes` would do for most, but the
# critical ones (`.js`, `.mjs`, `.css`, `.woff2`) are PINNED: an ES module
# served as `text/plain` is refused by the browser, and the system default
# varies from one machine to the next.
_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".map": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".wav": "audio/wav",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}

# Host, port and allowed origin: `settings.api_host`, `settings.api_port`,
# `settings.cors_origin` (`*` by default: local network, the service reads no
# secret and accepts no sensitive data, and a misguessed origin would break the
# demo for nothing. Tighten once the deck has a stable, known origin).

# ONE WORKER (ADR-0005). The machine holds one 13 GB model: runs execute one
# after the other, in POST order. A POST during a run is queued, not refused;
# the deck gets its `run_id` at once and follows `/runs/<id>/status`. The
# chapter to write is in the payload: there is no default chapter.


class Worker:
    """The run queue and the thread that executes it, one run at a time."""

    def __init__(self):
        self.lock = threading.Lock()
        self.wake = threading.Condition(self.lock)
        self.queue: list[Run] = []
        self.current: Run | None = None
        self.tracking: progress.Progress | None = None
        self.started_at: float | None = None
        self.thread: threading.Thread | None = None

    # --- submission ----------------------------------------------------------

    def submit(self, run: Run) -> int:
        """Queue the run; return its position (0 = starts right away)."""
        with self.lock:
            self.queue.append(run)
            position = len(self.queue) - 1 + (1 if self.current else 0)
            if self.thread is None or not self.thread.is_alive():
                self.thread = threading.Thread(target=self._loop, daemon=True)
                self.thread.start()
            self.wake.notify()
        return position

    @property
    def busy(self) -> bool:
        with self.lock:
            return self.current is not None

    def cancel(self, run_id: str) -> bool:
        """Remove a run from the queue, or ask the current run to stop.

        Operator escape hatch (the deck's recovery policy): the stop takes
        effect at the next node boundary, so at worst after the model call in
        flight.
        """
        with self.lock:
            for run in self.queue:
                if run.id == run_id:
                    self.queue.remove(run)
                    run_registry.write_manifest(run, status="cancelled")
                    return True
            if self.current and self.current.id == run_id and self.tracking:
                self.tracking.cancelled = True
                return True
        return False

    # --- execution -----------------------------------------------------------

    def _loop(self) -> None:
        while True:
            with self.lock:
                while not self.queue:
                    self.wake.wait()
                run = self.queue.pop(0)
                self.current = run
            try:
                self._execute(run)
            finally:
                with self.lock:
                    self.current, self.tracking, self.started_at = None, None, None

    def _execute(self, run: Run) -> None:
        """Execute ONE run. NEVER fails towards the HTTP caller."""
        tracking = progress.Progress(active=True)
        # The beeper observes phase changes. It receives only the phase LABEL
        # and the percentage, never the notes, which quote the bible and the
        # chapter (ADR-0015).
        tracking.observer = lambda s: notify.advancement(
            s.current_phase, s.advancement, int(time.time() - s.t0))
        with self.lock:
            self.tracking, self.started_at = tracking, time.time()
        progress.install(tracking)
        run_registry.write_manifest(run, status="generating",
                                    started=time.strftime("%Y-%m-%dT%H:%M:%S"))
        notify.startup(f"chapitre {run.chapter}")
        clocks = run_registry.Clocks()
        saved = {k: getattr(settings, k) for k in run.overrides}
        for k, v in run.overrides.items():
            setattr(settings, k, v)
        model_client.recording = []
        retrieval.clear_routing()
        final: dict | None = None
        status, error = "error", None
        try:
            # Preflight is the FIRST NODE of the graph; its refusal becomes an
            # `error` state the deck reads as not ready. `timer=True`: the
            # stage path (ADR-0016). `narrative_state=True`: the chapter's
            # state is regenerated and indexed before the first call.
            # `render=True`: the last node writes `chapitre.md` then the WAV
            # into the run directory; a voice failure leaves the chapter
            # served (ADR-0012).
            graph = build_graph()
            final = graph.invoke(
                {**load_chapter(run.chapter).state(seed=run.seed),
                 "preflight": {"strict": True, "timer": True},
                 "narrative_state": True,
                 "render": True,
                 "artifacts_dir": str(run.dir)},
                config={"recursion_limit": 50},
            )
            status = "ready"
            progress.note("chapitre prêt")
            notify.ready(int(time.time() - self.started_at),
                         len(final.get("repaired") or []),
                         (final.get("audio") or {}).get("audio_s"))
        except progress.Cancelled:
            status = "cancelled"
            progress.note("génération annulée")
            notify.cancelled()
        except PreflightError as exc:
            # The preflight message is OURS, with no content of the work, but
            # it is a multi-line how-to, unreadable at a glance: the beeper
            # gets only its first line.
            error = f"préflight refusé : {exc}"
            lines = str(exc).splitlines()
            self._fail(error, kind="préflight",
                       short=lines[1].strip(" -") if len(lines) > 1 else str(exc))
        except Exception as exc:                       # noqa: BLE001
            # Deliberately broad: onstage an unexpected exception must produce
            # a clean fallback, not a traceback in a thread.
            error = f"{type(exc).__name__} : {exc}"
            self._fail(error, kind=type(exc).__name__, short=str(exc))
        finally:
            calls = model_client.recording
            model_client.recording = None
            for k, v in saved.items():
                setattr(settings, k, v)
            tracking.end()
            try:
                run_registry.record_result(
                    run, final, clocks=clocks.read(), calls=calls,
                    collections=retrieval.routing(), status=status, error=error)
            except Exception as exc:                   # noqa: BLE001
                progress.note(f"manifeste non écrit : {exc}")

    def _fail(self, reason: str, *, kind: str = "erreur", short: str = "") -> None:
        progress.note(f"ÉCHEC : {reason}")
        notify.failure(kind, short or reason)

    # --- reading -------------------------------------------------------------

    def snapshot(self, run: Run) -> dict:
        """Payload of `GET /runs/<id>/status`.

        In memory for the current run (the progress sink) and the queued
        runs; from the manifest for finished runs. The server keeps no
        chapter in memory (ADR-0005).
        """
        with self.lock:
            current = self.current
            tracking, started = self.tracking, self.started_at
            position = next((i for i, r in enumerate(self.queue) if r.id == run.id), None)
        base = {"run_id": run.id, "chapter": run.chapter, "seed": run.seed}
        if current and current.id == run.id and tracking:
            snap = tracking.snapshot()
            snap.update(base)
            snap["state"] = "generating"
            snap["ready"] = False
            if started:
                snap["elapsed_s"] = int(time.time() - started)
            return snap
        if position is not None:
            return {**base, "phase": "queued", "state": "queued", "ready": False,
                    "progress": 0.0, "label": "", "detail": f"en file, position {position + 1}",
                    "elapsed_s": 0, "budget_s": int(settings.stage_budget_min * 60),
                    "gen_toks": 0, "notes": [], "position": position + 1}
        manifest = run_registry.load_run(run.dir)
        m = manifest.manifest if manifest else run.manifest
        state = m.get("status", "unknown")
        snap = {**base, "state": state,
                # `phase` and `ready` are the two fields of the deck's GenStatus contract.
                "phase": {"ready": "ready", "error": "error", "cancelled": "idle",
                          "queued": "queued"}.get(state, "generating"),
                "ready": state == "ready" and run.chapter_path.exists(),
                "progress": 1.0 if state == "ready" else 0.0,
                "label": "", "detail": "", "gen_toks": (m.get("metrics") or {}).get("gen_toks", 0),
                "budget_s": int(settings.stage_budget_min * 60),
                "notes": [], "elapsed_s": int((m.get("timings") or {}).get("wall_s", 0))}
        if m.get("error"):
            snap["error"] = m["error"]
        if m.get("timings"):
            snap["duration_s"] = int(m["timings"].get("wall_s", 0))
        if m.get("audio") is not None:
            snap["audio_s"] = m["audio"].get("audio_s")
        return snap


WORKER = Worker()


# --- Actor mode --------------------------------------------------------------
#
# Roleplay sessions live SERVER-SIDE: the memory is stateful (rolling summary,
# indexed memories), which is exactly why an OpenAI-compatible API was not
# taken: it assumes a client resending the whole history each turn and would
# bypass the summariser (ADR-0014).



class ChatRoom:
    """Registry of open conversations, purged after inactivity."""

    def __init__(self):
        self.lock = threading.Lock()
        self.sessions: dict[str, tuple[object, float]] = {}

    def _purge(self) -> None:
        """Close and WRITE inactive sessions before forgetting them.

        A session that evaporates without a trace would contradict the whole
        memory design, and this API is how the stage's pre-generated sessions
        are recorded. Silent forgetting would lose demo content.
        """
        limit = time.time() - settings.chat_ttl_s   # 2 h of inactivity
        for key in [k for k, (_, seen) in self.sessions.items() if seen < limit]:
            session, _ = self.sessions.pop(key)
            try:
                session.close()
            except Exception:                           # noqa: BLE001
                pass    # a purge must never fail the request in flight

    def close_chat(self, key: str):
        """End a session: write the Markdown and index it. Return the path,
        or None if the session is unknown or too short."""
        with self.lock:
            entry = self.sessions.pop(key, None)
        if entry is None:
            return None
        return entry[0].close()

    def acquire(self, key: str | None, character: str, name: str | None):
        """Existing session, or a new one. Return (key, session)."""
        from factory.roleplay.session import Session

        with self.lock:
            self._purge()
            if key and key in self.sessions:
                session, _ = self.sessions[key]
                self.sessions[key] = (session, time.time())
                return key, session
        # Built OUTSIDE the lock: it queries ChromaDB (memories, sheet) and has
        # no reason to block the other conversations.
        session = Session(character, name=name)
        key = f"{character}-{int(time.time() * 1000):x}"
        with self.lock:
            self.sessions[key] = (session, time.time())
        return key, session


ROOM = ChatRoom()


class Handler(BaseHTTPRequestHandler):
    server_version = "fiction-assistant/1.0"

    # --- helpers -------------------------------------------------------------

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", settings.cors_origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _reply(self, code: int, body: bytes = b"",
                  mime_type: str = "application/json") -> None:
        self.send_response(code)
        self._cors()
        if body:
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(body)))
        # No cache: the deck polls the same URL while the state changes.
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code: int, payload_dict: dict) -> None:
        self._reply(code, json.dumps(payload_dict, ensure_ascii=False).encode())

    def _file(self, path: Path, mime_type: str) -> None:
        """Serve an artifact, or 204 when it is not ready.

        204 and not 404: the deck treats both as not ready, but 204 says
        "nothing to give yet" where 404 would say "this route does not
        exist". The deck retries, then falls back to its embedded assets
        (ADR-0005).
        """
        if not path.exists() or path.stat().st_size == 0:
            self._reply(204)
            return
        self._reply(200, path.read_bytes(), mime_type)

    def _serve_static(self, path: Path, mime: str) -> None:
        """Serve a file of the build, with a fitting cache policy.

        Not `_reply`: it forces `no-store`, right for changing artifacts
        (`/runs/<id>/chapter`, `/runs/<id>/status`) but wasteful for the
        deck's hashed assets. `/assets/<hash>.<ext>` files are immutable by
        construction (the hash changes with the content) → long cache; the
        index and the rest → plain revalidation.
        """
        body = path.read_bytes()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        if "/assets/" in path.as_posix() and path.suffix.lower() != ".html":
            self.send_header("Cache-Control",
                             "public, max-age=31536000, immutable")
        else:
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _serve_slides(self, route: str) -> None:
        """Serve the talk's Slidev build (SPA with base `/`), falling back to index.html.

        Order matters: the API routes are tested BEFORE this one, higher in
        `do_GET`. Everything else lands here: build assets, but also Slidev's
        CLIENT routes (`/2`, `/overview`, `/presenter/...`) that have no
        file: they render the app, which routes in the browser. Exactly the
        build's `_redirects: /* -> /index.html`.
        """
        slides = settings.slides_dir.resolve()
        if not slides.is_dir():
            # Build absent: not an API route, so a plain 404, not a 204 "not
            # ready" (which has a precise meaning for the deck's artifacts).
            self._json(404, {"error": "slides non buildées",
                             "detail": f"attendu dans {slides}"})
            return
        rel = route.lstrip("/") or "index.html"
        target = (slides / rel).resolve()
        # Anti-traversal: the target MUST stay under dist. This server listens
        # to a conference network; same guard as the session identifiers.
        try:
            target.relative_to(slides)
        except ValueError:
            self._reply(403)
            return
        if not target.is_file():
            target = slides / "index.html"
            if not target.is_file():
                self._json(404, {"error": "index des slides absent"})
                return
        mime = _TYPES.get(target.suffix.lower(), "application/octet-stream")
        self._serve_static(target, mime)

    def _event_stream(self, run: Run) -> None:
        """SSE stream of `/runs/<id>/status` snapshots; the deck's counter reads
        the steps live there (phase, label, detail, notes, progress).

        Not `_reply`: it forces `Content-Length` and a single write. The
        response is opened by hand as `text/event-stream`, and a
        `WORKER.snapshot(run)` is pushed about every second. Each event is
        ABSOLUTE, not incremental: a reconnection resumes from the current
        state, no `Last-Event-ID` needed.

        An ENRICHMENT, not a dependency: if it drops, the deck's counter
        stays autonomous. Stream while the generation runs, emit one last
        event at the terminal state (`ready`/`error`/`idle`), then close.
        """
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        # `BaseHTTPRequestHandler` does not chunk by itself: close the
        # connection at the end rather than announce a length unknown upfront.
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            while True:
                snap = WORKER.snapshot(run)
                self.wfile.write(b"data: "
                                 + json.dumps(snap, ensure_ascii=False).encode()
                                 + b"\n\n")
                self.wfile.flush()
                if snap.get("state") in run_registry.TERMINAL or snap.get("state") == "unknown":
                    break
                time.sleep(1)
        except (BrokenPipeError, ConnectionResetError):
            # Client gone (slide changed, deck closed): the generation continues
            # in its thread. Without this guard, one traceback per disconnect.
            pass

    # --- routes --------------------------------------------------------------

    def do_OPTIONS(self) -> None:          # noqa: N802
        self._reply(204)

    def _param(self, name: str) -> str:
        """Value of a query parameter, or the empty string."""
        _, _, request = self.path.partition("?")
        return parse_qs(request).get(name, [""])[0]

    # Session identifier components. The filter is a WHITELIST, not a hunt for
    # `..`: this server listens to a conference network, and both values end
    # up in a file path (ADR-0014).
    _CHARACTER_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
    _TIMESTAMP_ID = re.compile(r"^[0-9A-Za-z:_-]{1,40}$")

    def _saved_session(self, rest: str) -> None:
        """`GET /session/<character>/<timestamp>`: a replayable transcription."""
        pieces = [m for m in rest.split("?")[0].split("/") if m]
        if len(pieces) != 2:
            self._json(400, {"error": "format attendu : /session/<perso>/<horodatage>"})
            return
        char_id, timestamp = pieces
        if not self._CHARACTER_ID.match(char_id) or not self._TIMESTAMP_ID.match(timestamp):
            self._json(400, {"error": "identifiant de session invalide"})
            return
        try:
            self._json(200, read_session(char_id, timestamp))
        except FileNotFoundError as exc:
            self._json(404, {"error": str(exc)})

    def _json_body(self) -> dict:
        size = int(self.headers.get("Content-Length") or 0)
        if not size:
            return {}
        try:
            return json.loads(self.rfile.read(size) or b"{}")
        except json.JSONDecodeError:
            return {}

    def _chat(self) -> None:
        """One roleplay turn. `{character, message, session?, nom?}`."""
        # ONE MODEL AT A TIME FOR THIS MACHINE (ADR-0006). Roleplay runs the
        # same nemo (13 GB) as the generation: during a chapter, a line would
        # wait for the writing call in flight, up to two minutes of silence
        # onstage. Two co-resident models are 17.8 GB of 19.3, the pressure
        # that panicked the machine. Refuse plainly rather than let the latency
        # be discovered live. Planning consequence: the actor demo plays BEFORE
        # the chapter launch, or AFTER its harvest.
        if WORKER.busy:
            self._json(409, {
                "error": "génération en cours",
                "detail": "Le mode acteur et la génération partagent le même "
                          "modèle ; la machine n'en tient qu'un. Réessayer "
                          "après la récolte du chapitre.",
                "state": "generating",
            })
            return

        payload_dict = self._json_body()
        character = (payload_dict.get("character") or "").strip()
        message = (payload_dict.get("message") or "").strip()

        # Explicit end: this is what turns a conversation into an artifact
        # replayable onstage (summary + transcription written as Markdown).
        if payload_dict.get("close") and payload_dict.get("session"):
            path = ROOM.close_chat(payload_dict["session"])
            self._json(200, {
                "closed": True,
                "fichier": str(path) if path else None,
                "detail": None if path else "session inconnue ou trop courte",
            })
            return

        if not character or not message:
            self._json(400, {"error": "champs `character` et `message` requis"})
            return

        try:
            key, session = ROOM.acquire(payload_dict.get("session"), character,
                                         payload_dict.get("nom"))
        except ValueError as exc:          # sheet absent from the bible
            self._json(404, {"error": str(exc)})
            return

        try:
            reply = session.say(message)
        except Exception as exc:           # noqa: BLE001
            self._json(503, {"error": f"{type(exc).__name__} : {exc}"})
            return

        self._json(200, {
            "session": key,
            "character": character,
            "nom": session.name,
            "reply": reply,
            # Warnings (caught out-of-role reply, language leak) are returned
            # for the operator; the page does not show them to the audience.
            "warnings": session.warnings[-3:],
            "turns": len(session.metrics),
        })

    # --- runs (ADR-0005) -----------------------------------------------------

    _RUN_ID = run_registry.RUN_ID
    _LEGACY = ("/generate", "/status", "/events", "/chapter", "/audio", "/cancel")

    def _generate(self) -> None:
        """`POST /generate {chapter, seed?, overrides?}` → 202 {run_id}.

        The payload is MANDATORY: the chapter names an existing spec, the
        seed is random by default and recorded, the overrides are a whitelist
        of configuration keys (ADR-0005).
        """
        payload_dict = self._json_body()
        if not payload_dict or "chapter" not in payload_dict:
            self._json(400, {"error": "charge utile requise : {chapter, seed?, overrides?}",
                             "chapters": sorted(chapter_dirs())})
            return
        try:
            chapter = int(payload_dict["chapter"])
            spec = load_chapter(chapter)
        except (TypeError, ValueError, ChapterSpecError) as exc:
            self._json(400, {"error": f"chapitre invalide : {exc}",
                             "chapters": sorted(chapter_dirs())})
            return
        seed = payload_dict.get("seed")
        if seed is not None and not isinstance(seed, int):
            self._json(400, {"error": "seed : entier attendu"})
            return
        try:
            run = run_registry.create_run(
                chapter, spec.slug, seed=seed if seed is not None else random.randrange(1, 10**6),
                overrides=payload_dict.get("overrides") or {})
        except run_registry.RunError as exc:
            self._json(400, {"error": str(exc)})
            return
        position = WORKER.submit(run)
        self._json(202, {"accepted": True, "run_id": run.id, "chapter": chapter,
                         "seed": run.seed, "position": position,
                         "state": "generating" if position == 0 else "queued"})

    def _run_of(self, token: str) -> Run | None:
        """The run named in a path (`latest` or a whitelisted id), else None."""
        if token == "latest":
            return run_registry.latest_run()
        if not self._RUN_ID.match(token):
            return None
        return run_registry.find_run(token)

    def _runs_route(self, route: str, method: str) -> None:
        pieces = [m for m in route[len("/runs"):].split("/") if m]
        if not pieces:
            if method != "GET":
                self._json(404, {"error": "route inconnue"})
                return
            self._json(200, {"runs": [
                {"run_id": r.id, "chapter": r.chapter, "seed": r.seed,
                 "state": WORKER.snapshot(r)["state"], "created": r.created}
                for r in run_registry.list_runs()]})
            return
        token, rest = pieces[0], pieces[1:]
        if token != "latest" and not self._RUN_ID.match(token):
            self._json(400, {"error": "identifiant de run invalide"})
            return
        run = self._run_of(token)
        if run is None:
            self._json(404, {"error": "run inconnu" if token != "latest" else "aucun run"})
            return
        leaf = rest[0] if rest else "status"
        if method == "POST":
            if leaf == "cancel":
                stopped = WORKER.cancel(run.id)
                self._json(200, {"cancelled": stopped, "run_id": run.id,
                                 "detail": None if stopped else "ce run ne tourne pas"})
            else:
                self._json(404, {"error": "route inconnue"})
            return
        if leaf == "status":
            self._json(200, WORKER.snapshot(run))
        elif leaf == "events":
            self._event_stream(run)
        elif leaf == "chapter":
            self._file(run.chapter_path, "text/markdown; charset=utf-8")
        elif leaf == "audio":
            self._file(run.audio_path, "audio/wav")
        elif leaf == "prompts":
            self._file(run.prompts_path, "text/markdown; charset=utf-8")
        elif leaf == "manifest":
            self._file(run.dir / "manifest.yaml", "application/yaml; charset=utf-8")
        else:
            self._json(404, {"error": "route inconnue"})

    def do_POST(self) -> None:             # noqa: N802
        route = self.path.split("?")[0].rstrip("/") or "/"
        if route == "/chat":
            self._chat()
        elif route == "/generate":
            self._generate()
        elif route.startswith("/runs"):
            self._runs_route(route, "POST")
        elif route in self._LEGACY:
            self._gone(route)
        else:
            self._json(404, {"error": "route inconnue"})

    def _gone(self, route: str) -> None:
        # The keynote contract's singleton routes, replaced by ADR-0005. 410
        # and not a silent fallback: an unmigrated client must know at once.
        self._json(410, {"error": f"{route} n'existe plus",
                         "detail": "POST /generate {chapter, seed?} puis /runs/<id>/status, "
                                   "/events, /chapter, /audio, /prompts, POST /runs/<id>/cancel "
                                   "— ou /runs/latest/…"})

    def do_GET(self) -> None:              # noqa: N802
        route = self.path.split("?")[0].rstrip("/") or "/"
        if route.startswith("/runs"):
            self._runs_route(route, "GET")
        elif route in self._LEGACY:
            self._gone(route)
        elif route == "/health":
            with WORKER.lock:
                active, queued = WORKER.current, len(WORKER.queue)
            self._json(200, {"ok": True, "machine": report(),
                             "active": active.id if active else None, "queued": queued,
                             "chapters": sorted(chapter_dirs())})
        elif route == "/characters":
            self._json(200, {"characters": list_characters()})
        elif route == "/sessions":
            char_id = self._param("character")
            self._json(200, {"sessions": list_sessions(char_id or None)})
        elif route.startswith("/session/"):
            self._saved_session(route[len("/session/"):])
        elif route == "/acteur":
            # The actor mode page, served by us so a slide can open it in an
            # iframe at the same host as the rest. The root `/` is the DECK;
            # the iframe points here, `/acteur` (ADR-0014).
            page = STATIC / "acteur.html"
            if page.exists():
                self._reply(200, page.read_bytes(), "text/html; charset=utf-8")
            else:
                self._json(404, {"error": "page absente"})
        else:
            # Everything else (`/`, `/favicon.svg`, `/assets/...`, Slidev
            # client routes) is served from the deck's build, index.html as
            # fallback.
            self._serve_slides(route)

    def log_message(self, fmt: str, *args) -> None:
        # The default log writes to stderr over the progress panel. Keep one
        # short, prefixed line.
        print(f"[api] {fmt % args}")


def main() -> None:
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((settings.api_host, settings.api_port), Handler)
    print(f"[api] écoute sur http://{settings.api_host}:{settings.api_port}")
    print(f"[api] machine : {report()}")
    print(f"[api] runs : {settings.runs_dir} — chapitres : {sorted(chapter_dirs())}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[api] arrêt")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
