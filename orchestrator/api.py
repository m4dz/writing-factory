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
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import progress
from chapitre import assembler
from graph import build_graph
from llm import unload
from preflight import PreflightError, preflight, report
from qa import QA_MODEL
from tts import rendre_chapitre

HOST = os.environ.get("API_HOST", "0.0.0.0")
PORT = int(os.environ.get("API_PORT", "8420"))

# Origine autorisée. `*` par défaut : on est sur un réseau local, le service ne
# lit aucun secret et n'accepte aucune donnée sensible — et une origine mal
# devinée le jour J casserait la démo pour rien. À resserrer si le deck est
# servi depuis une origine stable connue.
CORS_ORIGIN = os.environ.get("API_CORS_ORIGIN", "*")

SORTIE = Path(os.environ.get("API_OUTPUT_DIR",
                             Path(__file__).resolve().parent.parent / "output"))
CHAPITRE_MD = SORTIE / "chapitre.md"
CHAPITRE_WAV = SORTIE / "chapitre.wav"

# Consigne par défaut. Le contrat dit « corps minimal ou vide » : le deck ne
# connaît pas le récit, c'est la machine qui sait quoi écrire.
BRIEF = os.environ.get(
    "DEMO_BRIEF",
    "Élara arrive à la forge de Valmir et doit convaincre Kael de lui forger "
    "une lame ; Kael refuse d'abord, puis cède pour une raison qu'il ne dit pas.",
)
CHARACTERS = os.environ.get("DEMO_CHARACTERS", "elara-vance kael-doran").split()


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
            progress.install(self.suivi)
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
            avertissements = preflight(strict=True)
            for a in avertissements:
                progress.note(f"préflight : {a}")

            graph = build_graph()
            final = graph.invoke(
                {"brief": BRIEF, "characters": CHARACTERS},
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
        except PreflightError as exc:
            self._echouer(f"préflight refusé : {exc}")
        except Exception as exc:                       # noqa: BLE001
            # Large volontairement : sur scène, une exception non prévue doit
            # produire un fallback propre, pas un traceback dans un thread.
            self._echouer(f"{type(exc).__name__} : {exc}")
        finally:
            if self.suivi:
                self.suivi.fin()

    def _echouer(self, raison: str) -> None:
        with self.lock:
            self.etat = "error"
            self.erreur = raison
            self.fini_a = time.time()
        progress.note(f"ÉCHEC : {raison}")

    def _ecrire_chapitre(self, final: dict) -> None:
        """Écrit le Markdown du chapitre sur disque (source de `GET /chapter`).

        C'est ici que le marqueur de bascule est posé — par le code, jamais par
        le modèle (cf. `chapitre.py`).
        """
        SORTIE.mkdir(parents=True, exist_ok=True)
        scenes = final.get("repaired") or final.get("scenes") or []
        CHAPITRE_MD.write_text(assembler(scenes), encoding="utf-8")

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
                f"audio prêt : {metriques['audio_s']:.0f} s de lecture en "
                f"{metriques['calcul_s']:.0f} s (×{metriques['facteur_temps_reel']} "
                "temps réel)"
            )
            return metriques
        except Exception as exc:                        # noqa: BLE001
            progress.note(f"TTS indisponible : {exc} — chapitre servi sans audio")
            return None

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
        base["phase"] = {
            "ready": "ready", "tts": "tts", "error": "error",
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

    # --- routes --------------------------------------------------------------

    def do_OPTIONS(self) -> None:          # noqa: N802
        self._repondre(204)

    def do_POST(self) -> None:             # noqa: N802
        if self.path.rstrip("/") != "/generate":
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
        elif route == "/chapter":
            self._fichier(CHAPITRE_MD, "text/markdown; charset=utf-8")
        elif route == "/audio":
            self._fichier(CHAPITRE_WAV, "audio/wav")
        elif route == "/health":
            self._json(200, {"ok": True, "machine": report()})
        else:
            self._json(404, {"error": "route inconnue"})

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
