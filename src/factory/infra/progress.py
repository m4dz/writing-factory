#!/usr/bin/env python3
"""Affichage de progression et compte à rebours pour la démo de scène.

Le problème que ce module résout n'est pas cosmétique. La génération d'un
chapitre prend dix-sept minutes, pendant lesquelles le pilote en ligne de commande n'affichait
RIEN : la sortie n'arrivait qu'à la fin. Devant une salle, un écran figé se lit
comme une machine plantée — soit l'inverse exact de ce que la démo doit montrer.

Deux principes de conception :

1. **Les nœuds du graphe ne connaissent pas l'affichage.** Ils appellent
   `phase()`, `note()`, `tokens()` sur un puits d'événements global. Le puits
   décide s'il dessine un panneau ANSI, écrit des lignes plates, ou se taise.
   Un `Progress` inactif (le défaut) rend tous les appels gratuits, ce qui
   permet d'instrumenter le graphe sans conditionnelle nulle part.

2. **Montrer le TRAVAIL, pas seulement le temps.** Un compte à rebours qui
   tourne pendant qu'un appel de 1 min 45 bloque prouve que le temps passe, pas
   que la machine calcule. Les tokens qui arrivent un par un, si — d'où le
   branchement sur le streaming d'Ollama (cf. `llm.chat_turns(on_token=…)`).
"""

import shutil
import sys
import time

from factory.settings import settings

# Budget de scène, en minutes : `settings.stage_budget_min`. La keynote récolte
# le chapitre ~25 min après l'avoir lancé (abaissé de 35' à 25' le 2026-08-06).

_ANSI_CLEAR_LINE = "\x1b[2K"
_ANSI_LINE_START = "\r"

# Bandes d'avancement par phase, en fraction du travail total. Les bornes sont
# grossières et c'est assumé : elles servent à faire progresser une barre pour
# la salle, pas à prédire une fin. Elles vivent ICI et non dans les nœuds du
# graphe, pour qu'on puisse les recaler après une répétition sans toucher au
# pipeline. Mesures du run de référence (17,0 min, 4 scènes) : le plan pèse
# ~2 min, l'écriture ~7, la relecture ~5, la QA ~3.
BANDS = {
    "Préflight": (0.00, 0.01),
    "Invariants de la bible": (0.01, 0.03),
    # Plan et « Plan d'entrées » sont deux CHEMINS du même nœud (brief imposé vs
    # généré) : même bande, un seul est émis par run.
    "Plan": (0.03, 0.08),
    "Plan d'entrées": (0.03, 0.08),
    "Contrôle du plan contre la bible": (0.08, 0.12),
    "Écriture": (0.12, 0.50),
    # Accumulation / Glissement : SOUS-ÉTAPES d'une entrée d'écriture, dans la
    # boucle write→accumulate→glisse. VOLONTAIREMENT sans bande : elles tiennent
    # la valeur atteinte par « Écriture » (dont i/n mène la barre). Une bande
    # propre sauterait à contretemps de la boucle, puis le garde monotone
    # figerait l'écriture des entrées suivantes.
    "Relecture": (0.50, 0.72),
    "Bascule des modèles": (0.72, 0.73),
    "Réparation linguistique": (0.73, 0.85),
    "Assemblage": (0.85, 0.90),
    "Pose des gestes": (0.90, 0.94),
    "Cohérence par faits": (0.94, 0.97),
    "Restitution": (0.97, 1.00),
}

# Phases telles que le deck les connaît (contrat gelé côté talk :
# `GenStatus`). Notre granularité interne est plus fine ; on la projette.
DECK_PHASES = {
    "Restitution": "tts",
}


class Cancelled(RuntimeError):
    """Le job en cours a été annulé par l'opérateur.

    Levée depuis `phase()`, c'est-à-dire aux FRONTIÈRES DE NŒUD du graphe : on
    ne peut pas tuer proprement un thread Python, mais on peut refuser de passer
    à l'étape suivante. Le pire délai est donc la durée d'un appel au modèle
    (~2 min sur une écriture de scène), pas l'éternité.
    """


def _mmss(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:d}:{seconds % 60:02d}"


class Progress:
    """Puits d'événements de progression.

    Trois modes, choisis à la construction :
      * `actif=False` — silencieux, coût nul. C'est le défaut, donc les tests et
        les appels programmatiques ne changent pas de comportement.
      * terminal interactif — un panneau d'une ligne réécrit en place.
      * sortie redirigée — des lignes plates horodatées, une par événement. Une
        barre réécrite en place produirait des milliers de `\\r` dans un fichier
        de log, illisible ; et c'est exactement le cas d'usage `> run.log`.
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
        self.deck_phase = "generating"   # projection sur le contrat du deck
        self.advancement = 0.0            # fraction 0..1, monotone
        self.gen_toks = 0          # tokens du chapitre entier
        self.cancelled = False              # demande d'arrêt de l'opérateur
        # Appelé à chaque changement de phase, avec le puits en argument. Sert
        # aux notifications téléphone sans que ce module connaisse le réseau.
        self.observer = None
        self.notes: list[str] = []       # événements marquants, pour /status
        self._call_toks = 0       # tokens de l'appel en cours
        self._last_draw = 0.0
        self._call_t = 0.0

    # --- API appelée par le graphe -------------------------------------------

    def phase(self, title: str, detail: str = "", *,
              i: int | None = None, n: int | None = None) -> None:
        """Change de phase (plan, écriture scène 2/4, relecture, QA…).

        `i`/`n` situent l'étape dans sa bande d'avancement (scène 2 sur 4). Les
        nœuds les fournissent quand ils les connaissent ; sans eux, la phase
        vaut le début de sa bande.

        Ce calcul tourne MÊME si l'affichage est inactif : `/status` doit pouvoir
        rendre un avancement quand le serveur HTTP n'écrit rien sur un terminal.
        """
        if self.cancelled:
            raise Cancelled("génération annulée par l'opérateur")
        start, end = BANDS.get(title, (self.advancement, self.advancement))
        part = (i / n) if (i is not None and n) else 0.0
        # Monotone : un avancement qui recule (replanification, phase inconnue)
        # se lit comme un bug depuis la salle.
        self.advancement = max(self.advancement, start + (end - start) * part)
        self.current_phase = title
        self.detail = detail
        self.deck_phase = DECK_PHASES.get(title, "generating")
        if self.observer:
            try:
                self.observer(self)
            except Exception:                          # noqa: BLE001
                pass    # un observateur défaillant n'arrête pas une génération
        if not self.active:
            return
        self._call_toks = 0
        self._call_t = time.time()
        if self.interactive:
            self._draw(force=True)
        else:
            self._line(f"{title}" + (f" — {detail}" if detail else ""))

    def note(self, message: str) -> None:
        """Événement ponctuel digne d'être vu (replanification, réparation…)."""
        # Conservées même en mode inactif : ce sont elles que `/status` et les
        # notifications téléphone relaient, et le serveur HTTP n'a pas de
        # terminal. Bornées, sinon un run long les accumule sans fin.
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
        """Callback de streaming : un fragment vient d'arriver."""
        if not self.active:
            return
        self._call_toks = cumulative
        self.gen_toks += 1
        if self.interactive:
            self._draw()

    def end(self) -> None:
        """Rend la ligne au terminal (le panneau ne doit pas rester collé)."""
        if self.active and self.interactive:
            self.stream.write(_ANSI_CLEAR_LINE + _ANSI_LINE_START)
            self.stream.flush()

    def snapshot(self) -> dict:
        """État courant, pour `GET /status` et les notifications.

        `phase` est la valeur du CONTRAT GELÉ côté deck
        (`generating` | `tts` | `ready`, cf. talk/openspec remote-integration) ;
        tout le reste est additif et le deck peut l'ignorer sans rien perdre —
        c'est la condition pour enrichir l'affichage sans casser le contrat.
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

    # --- rendu ---------------------------------------------------------------

    def _line(self, text: str) -> None:
        elapsed = time.time() - self.t0
        self.stream.write(f"[{_mmss(elapsed)} / {_mmss(self.budget)}] {text}\n")
        self.stream.flush()

    def _draw(self, *, force: bool = False) -> None:
        # Dix tokens par seconde suffiraient à redessiner dix fois par seconde,
        # ce qui ne se voit pas et coûte des écritures : on plafonne à 5 Hz.
        now = time.time()
        if not force and now - self._last_draw < 0.2:
            return
        self._last_draw = now

        elapsed = now - self.t0
        remaining = self.budget - elapsed
        speed = self._call_toks / max(0.1, now - self._call_t)
        # Le dépassement s'affiche en clair plutôt que de rester à zéro : sur
        # scène, mieux vaut savoir qu'on est à +2:30 que croire qu'il reste 0:00.
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


# Puits global. Le graphe l'utilise sans le connaître : par défaut il est
# inactif, donc importer le graphe depuis un test n'affiche rien.
SINK = Progress(active=False)


def install(sink: Progress) -> None:
    """Remplace le puits global (appelé par `factory generate` et l'API)."""
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
    """Callback de streaming à passer à `llm`, ou None si l'affichage est
    inactif — pour que le mode non-streamé reste le chemin par défaut."""
    return on_token if SINK.active else None
