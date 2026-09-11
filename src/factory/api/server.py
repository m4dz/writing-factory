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
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from factory.infra import notify
from factory.paths import OUTPUT_DIR, REPO_ROOT
from factory.infra import progress
from factory.chapter_spec import chapter7 as ch7
from factory.pipeline.assembly import assembler
from factory.pipeline.graph import build_graph
from factory.infra.ollama import unload
from factory.infra.preflight import PreflightError, preflight, report
from factory.pipeline.qa import QA_MODEL
from factory.retrieval.context import list_characters
from factory.roleplay.session import lire_session, lister_sessions
from factory.infra.tts import rendre_chapitre

STATIC = Path(__file__).resolve().parent / "static"

# Build Slidev du talk. Servi À LA RACINE parce que le build référence ses
# assets en chemins ABSOLUS (`/assets/...`, `/favicon.svg`) : impossible de le
# monter sous un préfixe sans le rebuilder avec une `base`. Conséquence
# heureuse — le deck se retrouve sur la MÊME origine que l'API, donc ses fetch
# `/status`, `/chapter`, `/audio` sont same-origin, sans CORS. C'est la raison
# d'être de cet endpoint : la machine de présentation charge le deck ICI, et
# l'API répond à côté, sur le même hôte.
#   ../../talk/slides/dist depuis orchestrator/  →  ia-devant-soi/talk/slides/dist
SLIDES = Path(os.environ.get(
    "API_SLIDES_DIR",
    REPO_ROOT.parent / "talk" / "slides" / "dist",
)).resolve()

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

HOST = os.environ.get("API_HOST", "0.0.0.0")
PORT = int(os.environ.get("API_PORT", "8420"))

# Origine autorisée. `*` par défaut : on est sur un réseau local, le service ne
# lit aucun secret et n'accepte aucune donnée sensible — et une origine mal
# devinée le jour J casserait la démo pour rien. À resserrer si le deck est
# servi depuis une origine stable connue.
CORS_ORIGIN = os.environ.get("API_CORS_ORIGIN", "*")

SORTIE = Path(os.environ.get("API_OUTPUT_DIR", OUTPUT_DIR))
CHAPITRE_MD = SORTIE / "chapitre.md"
CHAPITRE_WAV = SORTIE / "chapitre.wav"

# Le récit généré est le CHAPITRE 7 de « L'Involontaire ». Le contrat dit
# « corps minimal ou vide » : le deck ne connaît pas le récit, c'est la machine
# qui sait quoi écrire. Toute la structure du chapitre (deux entrées, ancre,
# beats, chute) vient de `ch7.etat_ch7()` — source unique partagée avec le
# driver de calibration (`outillage/run_s4.py`), pour qu'API et outillage
# convergent sur un seul chapitre. Graine aléatoire par run : vraie variance
# live du best-of-3 de l'entrée 1 et du tirage du glissement.


class Job:
    """Le job de génération unique, et son verrou.

    Un seul job en vol, par construction : la machine n'a de mémoire que pour un
    modèle de 13 GB, et le contrat exige qu'un second POST ne relance rien.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.etat = "idle"        # idle | generating | tts | ready | error
        self.demarre_a: float | None = None
        self.fini_a: float | None = None
        self.erreur: str | None = None
        self.suivi: progress.Progress | None = None
        self.resultat: dict | None = None
        self.thread: threading.Thread | None = None

    # --- lancement -----------------------------------------------------------

    def lancer(self) -> bool:
        """Démarre la génération si rien ne tourne. Retourne True si démarré.

        L'idempotence est ici, pas dans le handler : c'est une propriété du job,
        et le contrat en dépend (« un second POST ne relance pas »).
        """
        with self.lock:
            if self.etat in ("generating", "tts", "ready"):
                return False
            self.etat = "generating"
            self.demarre_a = time.time()
            self.fini_a = None
            self.erreur = None
            self.resultat = None
            self.suivi = progress.Progress(actif=True)
            # Le bipeur écoute les changements de phase. Il ne reçoit que le
            # LIBELLÉ de phase et le pourcentage — jamais les notes, qui citent
            # la bible et le chapitre (cf. notify.py).
            self.suivi.observateur = lambda s: notify.avancement(
                s.phase_courante, s.avancement, int(time.time() - s.t0)
            )
            progress.install(self.suivi)
            notify.demarrage()
            self.thread = threading.Thread(target=self._tourner, daemon=True)
            self.thread.start()
            return True

    def _tourner(self) -> None:
        """Exécute le pipeline. N'échoue JAMAIS vers l'appelant HTTP."""
        try:
            # Le préflight refuse une machine étranglée — mais son refus ne doit
            # pas devenir une erreur réseau pour le deck : il devient un état
            # `error` que le deck traite comme « pas prêt », donc un fallback
            # silencieux, tandis que la raison m'est rapportée telle quelle.
            # `chrono=True` : c'est la voie de la scène, celle qui court contre
            # le compteur du deck. Ici la durée est l'enjeu, donc un swap saturé
            # redevient bloquant — au contraire de l'outillage de calibration,
            # qui juge de la prose et se moque des secondes.
            avertissements = preflight(strict=True, chrono=True)
            for a in avertissements:
                progress.note(f"préflight : {a}")

            graph = build_graph()
            final = graph.invoke(
                ch7.etat_ch7(),
                config={"recursion_limit": 50},
            )
            self._ecrire_chapitre(final)
            audio = self._rendre_audio()
            with self.lock:
                self.resultat = {
                    "audio": audio,
                    "scenes": len(final.get("repaired") or []),
                    "warnings": final.get("warnings") or [],
                    "coherence": final.get("coherence") or "",
                    "plan_report": final.get("plan_report") or "",
                }
                self.etat = "ready"
                self.fini_a = time.time()
            progress.note("chapitre prêt")
            notify.pret(int(self.fini_a - self.demarre_a),
                        len(final.get("repaired") or []),
                        (audio or {}).get("audio_s"))
        except progress.Annulation:
            with self.lock:
                self.etat = "idle"       # la machine redevient disponible
                self.fini_a = time.time()
            progress.note("génération annulée")
            notify.annule()
        except PreflightError as exc:
            # Le message de préflight vient de NOUS, sans contenu d'œuvre — mais
            # c'est un mode d'emploi de plusieurs lignes, illisible sur une
            # montre : le bipeur n'en reçoit que la première.
            self._echouer(f"préflight refusé : {exc}", classe="préflight",
                          bref=str(exc).splitlines()[1].strip(" -") if
                          len(str(exc).splitlines()) > 1 else str(exc))
        except Exception as exc:                       # noqa: BLE001
            # Large volontairement : sur scène, une exception non prévue doit
            # produire un fallback propre, pas un traceback dans un thread.
            self._echouer(f"{type(exc).__name__} : {exc}",
                          classe=type(exc).__name__, bref=str(exc))
        finally:
            if self.suivi:
                self.suivi.fin()

    def _echouer(self, raison: str, *, classe: str = "erreur",
                 bref: str = "") -> None:
        with self.lock:
            self.etat = "error"
            self.erreur = raison
            self.fini_a = time.time()
        progress.note(f"ÉCHEC : {raison}")
        notify.echec(classe, bref or raison)

    def _ecrire_chapitre(self, final: dict) -> None:
        """Écrit le Markdown du chapitre sur disque (source de `GET /chapter`).

        C'est ici que le marqueur de bascule est posé — par le code, jamais par
        le modèle (cf. `chapitre.py`). Les paramètres CH7 (`MARQUEURS_CH7`)
        placent la bascule sur le SECOND en-tête daté — les deux entrées portent
        le même jour — et bornent l'audio sur la chute « Constat : anniversaire. »
        plutôt que sur un plafond de mots.
        """
        SORTIE.mkdir(parents=True, exist_ok=True)
        scenes = final.get("repaired") or final.get("scenes") or []
        CHAPITRE_MD.write_text(assembler(scenes, **ch7.MARQUEURS_CH7),
                               encoding="utf-8")

    def _rendre_audio(self) -> dict | None:
        """Synthétise l'extrait post-bascule. Retourne les métriques, ou None.

        Un échec de TTS ne fait PAS échouer le job. Le chapitre, lui, est valide
        et écrit : le deck doit pouvoir afficher le vrai texte tout en repliant
        sur son audio embarqué. Le contrat gèle un fallback PAR RESSOURCE — se
        rabattre sur les deux parce que la voix a manqué serait perdre du bon
        travail pour rien.
        """
        with self.lock:
            self.etat = "tts"
        # Qwen n'a plus rien à faire à ce stade, et 4,8 GB de rendus au modèle de
        # voix valent mieux qu'un swap. Même logique que la bascule nemo → Qwen.
        unload(QA_MODEL)
        try:
            metriques = rendre_chapitre(
                CHAPITRE_MD.read_text(encoding="utf-8"), CHAPITRE_WAV
            )
            progress.note(
                f"lecture prête : {metriques['audio_s']:.0f} s restituées en "
                f"{metriques['calcul_s']:.0f} s (×{metriques['facteur_temps_reel']})"
            )
            return metriques
        except Exception as exc:                        # noqa: BLE001
            progress.note(f"lecture indisponible : {exc} — chapitre servi sans lecture")
            return None

    def annuler(self) -> bool:
        """Demande l'arrêt du job en cours. Vrai s'il y avait quelque chose.

        Sortie de secours d'opérateur, née d'une interaction que le deck ne
        pouvait pas voir : sa politique de reprise re-POSTe une fois sur
        `phase: error` à moins de trois minutes du décompte. Le pipeline repart
        alors pour dix-sept minutes — bien après la fin du talk — et notre garde
        409 bloquerait le mode acteur pendant tout ce temps, précisément au
        moment où on veut le montrer. L'arrêt prend effet à la frontière de nœud
        suivante, donc au pire après l'appel modèle en cours.
        """
        with self.lock:
            if self.etat not in ("generating", "tts") or not self.suivi:
                return False
            self.suivi.annule = True
            return True

    # --- lecture -------------------------------------------------------------

    def instantane(self) -> dict:
        """Charge utile de `GET /status`.

        `phase` et `ready` sont les deux champs du contrat gelé ; tout le reste
        est additif, et le deck peut l'ignorer sans rien perdre.
        """
        with self.lock:
            etat, erreur = self.etat, self.erreur
            debut, fin = self.demarre_a, self.fini_a
            suivi = self.suivi
        base = suivi.instantane() if suivi else {
            "phase": "generating", "ready": False, "progress": 0.0,
            "label": "", "detail": "", "elapsed_s": 0,
            "budget_s": int(progress.BUDGET_MIN * 60), "gen_toks": 0, "notes": [],
        }
        # Projection sur `GenStatus` du deck. On lui dit `error` franchement :
        # son type le prévoit, et le savoir tôt lui permet de basculer sur ses
        # assets embarqués au lieu d'attendre un timeout. Le silence côté salle
        # est garanti par le deck, pas par un mensonge de notre part.
        # `idle` est dit franchement, comme `error` : c'est une valeur de leur
        # `GenStatus`, et prétendre « generating » avant tout lancement — ou
        # après une annulation — laisserait le deck attendre un chapitre que
        # personne n'écrit.
        base["phase"] = {
            "ready": "ready", "tts": "tts", "error": "error", "idle": "idle",
        }.get(etat, "generating")
        base["ready"] = etat == "ready" and CHAPITRE_MD.exists()
        base["state"] = etat
        base["progress"] = 1.0 if etat == "ready" else base["progress"]
        if erreur:
            base["error"] = erreur
        if debut and fin:
            base["duration_s"] = int(fin - debut)
        return base


JOB = Job()


# --- Mode acteur -------------------------------------------------------------
#
# Les sessions de roleplay vivent CÔTÉ SERVEUR : notre mémoire est stateful
# (résumé glissant, souvenirs indexés), et c'est précisément pourquoi on n'a pas
# pris une API compatible OpenAI, qui suppose un client renvoyant tout
# l'historique à chaque tour — il court-circuiterait le résumeur.

CHAT_TTL_S = float(os.environ.get("CHAT_TTL_S", "7200"))   # 2 h d'inactivité


class Salon:
    """Registre des conversations en cours, purgé sur inactivité."""

    def __init__(self):
        self.lock = threading.Lock()
        self.sessions: dict[str, tuple[object, float]] = {}

    def _purger(self) -> None:
        """Ferme et ÉCRIT les sessions inactives avant de les oublier.

        Une session qui s'évapore sans laisser de trace contredirait toute la
        conception de la mémoire — et c'est par cette API qu'on enregistre les
        sessions pré-générées de la scène. L'oubli silencieux serait la perte
        d'un contenu de démo.
        """
        limite = time.time() - CHAT_TTL_S
        for cle in [k for k, (_, vu) in self.sessions.items() if vu < limite]:
            session, _ = self.sessions.pop(cle)
            try:
                session.close()
            except Exception:                           # noqa: BLE001
                pass    # une purge ne doit jamais faire échouer la requête en cours

    def fermer(self, cle: str):
        """Termine une session : écrit le Markdown et l'indexe. Retourne le
        chemin, ou None si la session est inconnue ou trop courte."""
        with self.lock:
            entree = self.sessions.pop(cle, None)
        if entree is None:
            return None
        return entree[0].close()

    def obtenir(self, cle: str | None, personnage: str, nom: str | None):
        """Session existante, ou nouvelle. Retourne (clé, session)."""
        from factory.roleplay.session import Session

        with self.lock:
            self._purger()
            if cle and cle in self.sessions:
                session, _ = self.sessions[cle]
                self.sessions[cle] = (session, time.time())
                return cle, session
        # Construction HORS verrou : elle interroge ChromaDB (souvenirs, fiche)
        # et n'a aucune raison de bloquer les autres conversations.
        session = Session(personnage, nom=nom)
        cle = f"{personnage}-{int(time.time() * 1000):x}"
        with self.lock:
            self.sessions[cle] = (session, time.time())
        return cle, session


SALON = Salon()


class Handler(BaseHTTPRequestHandler):
    server_version = "fiction-assistant/1.0"

    # --- utilitaires ---------------------------------------------------------

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _repondre(self, code: int, corps: bytes = b"",
                  type_mime: str = "application/json") -> None:
        self.send_response(code)
        self._cors()
        if corps:
            self.send_header("Content-Type", type_mime)
            self.send_header("Content-Length", str(len(corps)))
        # Aucun cache : le deck interroge la même URL pendant que l'état change.
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if corps and self.command != "HEAD":
            self.wfile.write(corps)

    def _json(self, code: int, charge: dict) -> None:
        self._repondre(code, json.dumps(charge, ensure_ascii=False).encode())

    def _fichier(self, chemin: Path, type_mime: str) -> None:
        """Sert un artefact, ou 204 s'il n'est pas prêt.

        204 et non 404 : le contrat traite les deux comme « pas prêt », mais 204
        dit « rien à donner pour l'instant » là où 404 dirait « cette route
        n'existe pas ». Le deck retentera puis basculera sur son embarqué.
        """
        if not chemin.exists() or chemin.stat().st_size == 0:
            self._repondre(204)
            return
        self._repondre(200, chemin.read_bytes(), type_mime)

    def _servir_statique(self, chemin: Path, mime: str) -> None:
        """Sert un fichier du build, avec cache adapté.

        On N'UTILISE PAS `_repondre` : il force `no-store`, ce qui est juste pour
        les artefacts changeants (`/chapter`, `/status`) mais gâche le cache des
        assets hashés du deck. Ici les fichiers `/assets/<hash>.<ext>` sont
        immuables par construction (le hash change avec le contenu) → cache long ;
        l'index et le reste → revalidation simple.
        """
        corps = chemin.read_bytes()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(corps)))
        if "/assets/" in chemin.as_posix() and chemin.suffix.lower() != ".html":
            self.send_header("Cache-Control",
                             "public, max-age=31536000, immutable")
        else:
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corps)

    def _servir_slides(self, route: str) -> None:
        """Sert le build Slidev du talk (SPA à base `/`), repli sur index.html.

        Ordre imposé par le contrat : les routes de l'API passent AVANT (elles
        sont testées plus haut dans `do_GET`). Tout le reste tombe ici — assets
        du build, mais aussi les routes CLIENT de Slidev (`/2`, `/overview`,
        `/presenter/...`) qui n'ont pas de fichier : elles rendent l'app, qui
        route côté navigateur. C'est exactement le `_redirects: /* -> /index.html`
        du build.
        """
        if not SLIDES.is_dir():
            # Build absent : ce n'est pas une route d'API, donc 404 franc, pas un
            # 204 « pas prêt » (qui a un sens précis pour les artefacts du deck).
            self._json(404, {"error": "slides non buildées",
                             "detail": f"attendu dans {SLIDES}"})
            return
        rel = route.lstrip("/") or "index.html"
        cible = (SLIDES / rel).resolve()
        # Anti-traversée : la cible DOIT rester sous dist. Ce serveur écoute sur
        # le réseau d'une conférence — même garde que les identifiants de session.
        try:
            cible.relative_to(SLIDES)
        except ValueError:
            self._repondre(403)
            return
        if not cible.is_file():
            cible = SLIDES / "index.html"
            if not cible.is_file():
                self._json(404, {"error": "index des slides absent"})
                return
        mime = _TYPES.get(cible.suffix.lower(), "application/octet-stream")
        self._servir_statique(cible, mime)

    def _flux_evenements(self) -> None:
        """Flux SSE des instantanés de `/status` — le compteur du deck y lit les
        étapes en direct (phase, label, detail, notes, progress).

        On N'UTILISE PAS `_repondre` : il force `Content-Length` et un write
        unique. On ouvre la réponse à la main, en `text/event-stream`, et on
        pousse un snapshot `JOB.instantane()` toutes les ~1 s. Chaque événement
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
                snap = JOB.instantane()
                self.wfile.write(b"data: "
                                 + json.dumps(snap, ensure_ascii=False).encode()
                                 + b"\n\n")
                self.wfile.flush()
                if snap.get("state") in ("ready", "error", "idle"):
                    break
                time.sleep(1)
        except (BrokenPipeError, ConnectionResetError):
            # Client parti (slide changée, deck fermé) : la génération continue
            # sur son thread. Sans ce garde, une traceback par déconnexion.
            pass

    # --- routes --------------------------------------------------------------

    def do_OPTIONS(self) -> None:          # noqa: N802
        self._repondre(204)

    def _param(self, nom: str) -> str:
        """Valeur d'un paramètre de requête, ou chaîne vide."""
        _, _, requete = self.path.partition("?")
        return parse_qs(requete).get(nom, [""])[0]

    # Composants d'identifiant de session. Le filtre est une LISTE BLANCHE, pas
    # une chasse aux `..` : ce serveur écoute sur le réseau d'une conférence, et
    # ces deux valeurs arrivent dans un chemin de fichier.
    _ID_PERSO = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
    _ID_HORODATAGE = re.compile(r"^[0-9A-Za-z:_-]{1,40}$")

    def _session_enregistree(self, reste: str) -> None:
        """`GET /session/<personnage>/<horodatage>` — transcription rejouable."""
        morceaux = [m for m in reste.split("?")[0].split("/") if m]
        if len(morceaux) != 2:
            self._json(400, {"error": "format attendu : /session/<perso>/<horodatage>"})
            return
        perso, horodatage = morceaux
        if not self._ID_PERSO.match(perso) or not self._ID_HORODATAGE.match(horodatage):
            self._json(400, {"error": "identifiant de session invalide"})
            return
        try:
            self._json(200, lire_session(perso, horodatage))
        except FileNotFoundError as exc:
            self._json(404, {"error": str(exc)})

    def _corps_json(self) -> dict:
        taille = int(self.headers.get("Content-Length") or 0)
        if not taille:
            return {}
        try:
            return json.loads(self.rfile.read(taille) or b"{}")
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
        if JOB.etat in ("generating", "tts"):
            self._json(409, {
                "error": "génération en cours",
                "detail": "Le mode acteur et la génération partagent le même "
                          "modèle ; la machine n'en tient qu'un. Réessayer "
                          "après la récolte du chapitre.",
                "state": JOB.etat,
            })
            return

        charge = self._corps_json()
        personnage = (charge.get("character") or "").strip()
        message = (charge.get("message") or "").strip()

        # Fin explicite : c'est ce qui transforme une conversation en artefact
        # rejouable sur scène (résumé + transcription écrits en Markdown).
        if charge.get("close") and charge.get("session"):
            chemin = SALON.fermer(charge["session"])
            self._json(200, {
                "closed": True,
                "fichier": str(chemin) if chemin else None,
                "detail": None if chemin else "session inconnue ou trop courte",
            })
            return

        if not personnage or not message:
            self._json(400, {"error": "champs `character` et `message` requis"})
            return

        try:
            cle, session = SALON.obtenir(charge.get("session"), personnage,
                                         charge.get("nom"))
        except ValueError as exc:          # fiche absente de la bible
            self._json(404, {"error": str(exc)})
            return

        try:
            reponse = session.say(message)
        except Exception as exc:           # noqa: BLE001
            self._json(503, {"error": f"{type(exc).__name__} : {exc}"})
            return

        self._json(200, {
            "session": cle,
            "character": personnage,
            "nom": session.nom,
            "reply": reponse,
            # Les alertes (sortie de rôle rattrapée, fuite de langue) sont
            # rendues pour l'opérateur — la page ne les montre pas au public.
            "warnings": session.warnings[-3:],
            "turns": len(session.metrics),
        })

    def do_POST(self) -> None:             # noqa: N802
        route = self.path.split("?")[0].rstrip("/") or "/"
        if route == "/chat":
            self._chat()
            return
        if route == "/cancel":
            arrete = JOB.annuler()
            self._json(200, {"cancelled": arrete, "state": JOB.etat,
                             "detail": None if arrete else "aucun job en cours"})
            return
        if route != "/generate":
            self._json(404, {"error": "route inconnue"})
            return
        # On lit et jette le corps : le contrat le dit « minimal ou vide », et
        # laisser des octets non lus dans la socket casse le keep-alive.
        taille = int(self.headers.get("Content-Length") or 0)
        if taille:
            self.rfile.read(taille)
        demarre = JOB.lancer()
        # 202 dans les DEUX cas : « accepté », que ce POST ait démarré le job ou
        # qu'il ait trouvé le travail déjà en route. C'est ça, l'idempotence vue
        # du deck — qui ne doit pas avoir à distinguer.
        self._json(202, {"accepted": True, "started": demarre,
                         "state": JOB.etat})

    def do_GET(self) -> None:              # noqa: N802
        route = self.path.split("?")[0].rstrip("/") or "/"
        if route == "/status":
            self._json(200, JOB.instantane())
        elif route == "/events":
            self._flux_evenements()
        elif route == "/chapter":
            self._fichier(CHAPITRE_MD, "text/markdown; charset=utf-8")
        elif route == "/audio":
            self._fichier(CHAPITRE_WAV, "audio/wav")
        elif route == "/health":
            self._json(200, {"ok": True, "machine": report()})
        elif route == "/characters":
            self._json(200, {"characters": list_characters()})
        elif route == "/sessions":
            perso = self._param("character")
            self._json(200, {"sessions": lister_sessions(perso or None)})
        elif route.startswith("/session/"):
            self._session_enregistree(route[len("/session/"):])
        elif route == "/acteur":
            # La page du mode acteur. Servie par nous : elle peut donc être
            # ouverte en iframe depuis une slide, sur le même hôte que le reste.
            # La racine `/` est désormais le DECK — l'iframe pointe ici, `/acteur`.
            page = STATIC / "acteur.html"
            if page.exists():
                self._repondre(200, page.read_bytes(), "text/html; charset=utf-8")
            else:
                self._json(404, {"error": "page absente"})
        else:
            # Tout le reste — `/`, `/favicon.svg`, `/assets/...`, routes client
            # de Slidev — est servi par le build du deck, repli sur index.html.
            self._servir_slides(route)

    def log_message(self, fmt: str, *args) -> None:
        # Le journal par défaut écrit sur stderr en écrasant le panneau de
        # progression. On garde une ligne courte, préfixée.
        print(f"[api] {fmt % args}")


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    serveur = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"[api] écoute sur http://{HOST}:{PORT}")
    print(f"[api] machine : {report()}")
    print(f"[api] artefacts : {SORTIE}")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\n[api] arrêt")
    finally:
        serveur.server_close()


if __name__ == "__main__":
    main()
