#!/usr/bin/env python3
"""Serveur HTTP de la démo — surface consommée par le deck de la keynote.

    python api.py            # écoute sur 0.0.0.0:8420

CONTRAT GELÉ AILLEURS. Ce fichier n'invente rien : il implémente le contrat
figé dans le dépôt du talk (`openspec/changes/remote-integration-contract/`),
qui attendait explicitement cette surface pour se débloquer. Les quatre
opérations, leurs codes et leur sémantique viennent de là.

    POST /generate   202, fire-and-forget, IDEMPOTENT (un second POST ne
                     relance pas la génération)
    GET  /chapter    200 text/markdown (contient `<!-- BASCULE -->`), sinon 204
    GET  /audio      200 audio/wav (portion post-bascule, voix clonée), sinon 204
    GET  /status     200 {phase, ready, …}  — OPTIONNEL côté deck

Deux principes que le contrat impose et qui dictent tout le reste :

1. **Le deck ne doit JAMAIS voir d'erreur.** À toute défaillance il bascule en
   silence sur ses assets embarqués. Donc un préflight qui refuse, un modèle qui
   tombe, une exception dans le graphe : tout cela rend `204` sur les
   ressources et un statut `error` sur `/status`, jamais un 500 dans la figure
   du deck. L'erreur, c'est MOI qu'elle doit réveiller (notifications), pas la
   salle.

2. **Les artefacts vivent sur le DISQUE avant d'être servis.** `GET /chapter`
   lit un fichier. Si ce serveur meurt après la génération, le chapitre est
   toujours là, et un simple redémarrage le ressert. L'inverse — garder le
   chapitre en mémoire de processus — perdrait vingt minutes de calcul sur un
   Ctrl-C malheureux.
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

# Build Slidev du talk. Servi À LA RACINE parce que le build référence ses
# assets en chemins ABSOLUS (`/assets/...`, `/favicon.svg`) : impossible de le
# monter sous un préfixe sans le rebuilder avec une `base`. Conséquence
# heureuse — le deck se retrouve sur la MÊME origine que l'API, donc ses fetch
# `/status`, `/chapter`, `/audio` sont same-origin, sans CORS. C'est la raison
# d'être de cet endpoint : la machine de présentation charge le deck ICI, et
# l'API répond à côté, sur le même hôte.
#   ../talk/slides/dist depuis le dépôt  →  ia-devant-soi/talk/slides/dist
# Chemin : `settings.slides_dir`.

# Types MIME servis pour le build statique. `mimetypes` suffirait pour la
# plupart, mais on FIGE les critiques (`.js`, `.mjs`, `.css`, `.woff2`) : un
# module ES servi en `text/plain` est refusé par le navigateur, et le défaut
# système varie d'une machine à l'autre.
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

# Hôte, port et origine autorisée : `settings.api_host`, `settings.api_port`,
# `settings.cors_origin` (`*` par défaut : on est sur un réseau local, le
# service ne lit aucun secret et n'accepte aucune donnée sensible — et une
# origine mal devinée le jour J casserait la démo pour rien. À resserrer si le
# deck est servi depuis une origine stable connue).

# UN SEUL TRAVAILLEUR (ADR-0005). La machine ne tient qu'un modèle de 13 GB :
# les runs s'exécutent l'un après l'autre, dans l'ordre des POST. Un POST
# pendant un run est mis en file, pas refusé — le deck reçoit son `run_id` tout
# de suite et suit `/runs/<id>/status`. Le chapitre à écrire est dans la charge
# utile : la machine ne connaît plus de chapitre par défaut.


class Worker:
    """La file des runs et le fil qui les exécute, un à la fois."""

    def __init__(self):
        self.lock = threading.Lock()
        self.wake = threading.Condition(self.lock)
        self.queue: list[Run] = []
        self.current: Run | None = None
        self.tracking: progress.Progress | None = None
        self.started_at: float | None = None
        self.thread: threading.Thread | None = None

    # --- soumission ----------------------------------------------------------

    def submit(self, run: Run) -> int:
        """Met le run en file ; rend sa position (0 = démarre tout de suite)."""
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
        """Retire un run de la file, ou demande l'arrêt du run en cours.

        Sortie de secours d'opérateur (cf. la politique de reprise du deck) :
        l'arrêt prend effet à la frontière de nœud suivante, donc au pire
        après l'appel modèle en cours.
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

    # --- exécution -----------------------------------------------------------

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
        """Exécute UN run. N'échoue JAMAIS vers l'appelant HTTP."""
        tracking = progress.Progress(active=True)
        # Le bipeur écoute les changements de phase. Il ne reçoit que le
        # LIBELLÉ de phase et le pourcentage — jamais les notes, qui citent
        # la bible et le chapitre (cf. notify.py).
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
            # Le préflight est le PREMIER NŒUD du graphe ; son refus devient un
            # état `error` que le deck traite comme « pas prêt ». `timer=True` :
            # c'est la voie de la scène. `narrative_state=True` : l'état du
            # chapitre est régénéré et indexé avant le premier appel.
            # `render=True` : le dernier nœud écrit chapitre.md puis le WAV dans
            # le dossier du run ; un échec de voix laisse le chapitre servi.
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
            # Le message de préflight vient de NOUS, sans contenu d'œuvre — mais
            # c'est un mode d'emploi de plusieurs lignes, illisible sur une
            # montre : le bipeur n'en reçoit que la première.
            error = f"préflight refusé : {exc}"
            lines = str(exc).splitlines()
            self._fail(error, kind="préflight",
                       short=lines[1].strip(" -") if len(lines) > 1 else str(exc))
        except Exception as exc:                       # noqa: BLE001
            # Large volontairement : sur scène, une exception non prévue doit
            # produire un fallback propre, pas un traceback dans un thread.
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

    # --- lecture -------------------------------------------------------------

    def snapshot(self, run: Run) -> dict:
        """Charge utile de `GET /runs/<id>/status`.

        En mémoire pour le run en cours (le puits de progression) et les runs
        en file ; depuis le manifeste pour les runs terminés — le serveur ne
        garde aucun chapitre en mémoire (ADR-0005).
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
                # `phase` et `ready` sont les deux champs du contrat du deck.
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


# --- Mode acteur -------------------------------------------------------------
#
# Les sessions de roleplay vivent CÔTÉ SERVEUR : notre mémoire est stateful
# (résumé glissant, souvenirs indexés), et c'est précisément pourquoi on n'a pas
# pris une API compatible OpenAI, qui suppose un client renvoyant tout
# l'historique à chaque tour — il court-circuiterait le résumeur.



class ChatRoom:
    """Registre des conversations en cours, purgé sur inactivité."""

    def __init__(self):
        self.lock = threading.Lock()
        self.sessions: dict[str, tuple[object, float]] = {}

    def _purge(self) -> None:
        """Ferme et ÉCRIT les sessions inactives avant de les oublier.

        Une session qui s'évapore sans laisser de trace contredirait toute la
        conception de la mémoire — et c'est par cette API qu'on enregistre les
        sessions pré-générées de la scène. L'oubli silencieux serait la perte
        d'un contenu de démo.
        """
        limit = time.time() - settings.chat_ttl_s   # 2 h d'inactivité
        for key in [k for k, (_, seen) in self.sessions.items() if seen < limit]:
            session, _ = self.sessions.pop(key)
            try:
                session.close()
            except Exception:                           # noqa: BLE001
                pass    # une purge ne doit jamais faire échouer la requête en cours

    def close_chat(self, key: str):
        """Termine une session : écrit le Markdown et l'indexe. Retourne le
        chemin, ou None si la session est inconnue ou trop courte."""
        with self.lock:
            entry = self.sessions.pop(key, None)
        if entry is None:
            return None
        return entry[0].close()

    def acquire(self, key: str | None, character: str, name: str | None):
        """Session existante, ou nouvelle. Retourne (clé, session)."""
        from factory.roleplay.session import Session

        with self.lock:
            self._purge()
            if key and key in self.sessions:
                session, _ = self.sessions[key]
                self.sessions[key] = (session, time.time())
                return key, session
        # Construction HORS verrou : elle interroge ChromaDB (souvenirs, fiche)
        # et n'a aucune raison de bloquer les autres conversations.
        session = Session(character, name=name)
        key = f"{character}-{int(time.time() * 1000):x}"
        with self.lock:
            self.sessions[key] = (session, time.time())
        return key, session


ROOM = ChatRoom()


class Handler(BaseHTTPRequestHandler):
    server_version = "fiction-assistant/1.0"

    # --- utilitaires ---------------------------------------------------------

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
        # Aucun cache : le deck interroge la même URL pendant que l'état change.
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code: int, payload_dict: dict) -> None:
        self._reply(code, json.dumps(payload_dict, ensure_ascii=False).encode())

    def _file(self, path: Path, mime_type: str) -> None:
        """Sert un artefact, ou 204 s'il n'est pas prêt.

        204 et non 404 : le contrat traite les deux comme « pas prêt », mais 204
        dit « rien à donner pour l'instant » là où 404 dirait « cette route
        n'existe pas ». Le deck retentera puis basculera sur son embarqué.
        """
        if not path.exists() or path.stat().st_size == 0:
            self._reply(204)
            return
        self._reply(200, path.read_bytes(), mime_type)

    def _serve_static(self, path: Path, mime: str) -> None:
        """Sert un fichier du build, avec cache adapté.

        On N'UTILISE PAS `_repondre` : il force `no-store`, ce qui est juste pour
        les artefacts changeants (`/chapter`, `/status`) mais gâche le cache des
        assets hashés du deck. Ici les fichiers `/assets/<hash>.<ext>` sont
        immuables par construction (le hash change avec le contenu) → cache long ;
        l'index et le reste → revalidation simple.
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
        """Sert le build Slidev du talk (SPA à base `/`), repli sur index.html.

        Ordre imposé par le contrat : les routes de l'API passent AVANT (elles
        sont testées plus haut dans `do_GET`). Tout le reste tombe ici — assets
        du build, mais aussi les routes CLIENT de Slidev (`/2`, `/overview`,
        `/presenter/...`) qui n'ont pas de fichier : elles rendent l'app, qui
        route côté navigateur. C'est exactement le `_redirects: /* -> /index.html`
        du build.
        """
        slides = settings.slides_dir.resolve()
        if not slides.is_dir():
            # Build absent : ce n'est pas une route d'API, donc 404 franc, pas un
            # 204 « pas prêt » (qui a un sens précis pour les artefacts du deck).
            self._json(404, {"error": "slides non buildées",
                             "detail": f"attendu dans {slides}"})
            return
        rel = route.lstrip("/") or "index.html"
        target = (slides / rel).resolve()
        # Anti-traversée : la cible DOIT rester sous dist. Ce serveur écoute sur
        # le réseau d'une conférence — même garde que les identifiants de session.
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
        """Flux SSE des instantanés de `/runs/<id>/status` — le compteur du deck
        y lit les étapes en direct (phase, label, detail, notes, progress).

        On N'UTILISE PAS `_repondre` : il force `Content-Length` et un write
        unique. On ouvre la réponse à la main, en `text/event-stream`, et on
        pousse un snapshot `WORKER.snapshot(run)` toutes les ~1 s. Chaque événement
        est ABSOLU (pas incrémental) : une reconnexion reprend l'état courant,
        aucun `Last-Event-ID` nécessaire.

        C'est un ENRICHISSEMENT, pas une dépendance : s'il tombe, le compteur du
        deck reste autonome (invariant du contrat). On streame tant que la
        génération tourne, on émet un dernier événement à l'état terminal
        (`ready`/`error`/`idle`), puis on ferme.
        """
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        # `BaseHTTPRequestHandler` n'auto-chunk pas : on ferme la connexion à la
        # fin plutôt que d'annoncer une longueur inconnue d'avance.
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
            # Client parti (slide changée, deck fermé) : la génération continue
            # sur son thread. Sans ce garde, une traceback par déconnexion.
            pass

    # --- routes --------------------------------------------------------------

    def do_OPTIONS(self) -> None:          # noqa: N802
        self._reply(204)

    def _param(self, name: str) -> str:
        """Valeur d'un paramètre de requête, ou chaîne vide."""
        _, _, request = self.path.partition("?")
        return parse_qs(request).get(name, [""])[0]

    # Composants d'identifiant de session. Le filtre est une LISTE BLANCHE, pas
    # une chasse aux `..` : ce serveur écoute sur le réseau d'une conférence, et
    # ces deux valeurs arrivent dans un chemin de fichier.
    _CHARACTER_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
    _TIMESTAMP_ID = re.compile(r"^[0-9A-Za-z:_-]{1,40}$")

    def _saved_session(self, rest: str) -> None:
        """`GET /session/<personnage>/<horodatage>` — transcription rejouable."""
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
        """Un tour de roleplay. `{character, message, session?, nom?}`."""
        # UN SEUL MODÈLE À LA FOIS SUR CETTE MACHINE. Le roleplay tourne sur le
        # même nemo (13 GB) que la génération : pendant un chapitre, une
        # réplique attendrait la fin de l'appel d'écriture en cours, soit
        # jusqu'à deux minutes de silence sur scène. Et faire cohabiter deux
        # modèles, c'est 17,8 GB sur 19,3 — la pression qui a fait paniquer la
        # machine. On refuse franchement plutôt que de laisser découvrir la
        # latence en direct. Conséquence de planning : la démo d'acteur se joue
        # AVANT le lancement du chapitre, ou APRÈS sa récolte.
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

        # Fin explicite : c'est ce qui transforme une conversation en artefact
        # rejouable sur scène (résumé + transcription écrits en Markdown).
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
        except ValueError as exc:          # fiche absente de la bible
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
            # Les alertes (sortie de rôle rattrapée, fuite de langue) sont
            # rendues pour l'opérateur — la page ne les montre pas au public.
            "warnings": session.warnings[-3:],
            "turns": len(session.metrics),
        })

    # --- runs (ADR-0005) -----------------------------------------------------

    _RUN_ID = run_registry.RUN_ID
    _LEGACY = ("/generate", "/status", "/events", "/chapter", "/audio", "/cancel")

    def _generate(self) -> None:
        """`POST /generate {chapter, seed?, overrides?}` → 202 {run_id}.

        La charge utile est OBLIGATOIRE : le chapitre nomme une spécification
        existante, la graine est aléatoire par défaut et consignée, les
        overrides sont une liste blanche de clés de configuration.
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
        # Les routes singleton du contrat de la keynote (ADR-0005 les remplace).
        # 410 et non un repli silencieux sur le deck : un client non migré doit
        # le savoir tout de suite.
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
            # La page du mode acteur. Servie par nous : elle peut donc être
            # ouverte en iframe depuis une slide, sur le même hôte que le reste.
            # La racine `/` est désormais le DECK — l'iframe pointe ici, `/acteur`.
            page = STATIC / "acteur.html"
            if page.exists():
                self._reply(200, page.read_bytes(), "text/html; charset=utf-8")
            else:
                self._json(404, {"error": "page absente"})
        else:
            # Tout le reste — `/`, `/favicon.svg`, `/assets/...`, routes client
            # de Slidev — est servi par le build du deck, repli sur index.html.
            self._serve_slides(route)

    def log_message(self, fmt: str, *args) -> None:
        # Le journal par défaut écrit sur stderr en écrasant le panneau de
        # progression. On garde une ligne courte, préfixée.
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
