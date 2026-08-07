#!/usr/bin/env python3
"""Affichage de progression et compte à rebours pour la démo de scène.

Le problème que ce module résout n'est pas cosmétique. La génération d'un
chapitre prend dix-sept minutes, pendant lesquelles `run_chapter.py` n'affichait
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

import os
import shutil
import sys
import time

# Budget de scène, en minutes. La keynote récolte le chapitre ~25 min après
# l'avoir lancé (abaissé de 35' à 25' le 2026-08-06).
BUDGET_MIN = float(os.environ.get("DEMO_BUDGET_MIN", "25"))

_ANSI_EFFACE_LIGNE = "\x1b[2K"
_ANSI_DEBUT_LIGNE = "\r"


def _mmss(secondes: float) -> str:
    secondes = max(0, int(secondes))
    return f"{secondes // 60:d}:{secondes % 60:02d}"


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

    def __init__(self, *, actif: bool = False, budget_min: float = BUDGET_MIN,
                 flux=None):
        self.actif = actif
        self.budget = budget_min * 60
        self.flux = flux or sys.stdout
        self.interactif = actif and self.flux.isatty()
        self.t0 = time.time()
        self.phase_courante = ""
        self.detail = ""
        self.gen_toks = 0          # tokens du chapitre entier
        self._toks_appel = 0       # tokens de l'appel en cours
        self._dernier_dessin = 0.0
        self._t_appel = 0.0

    # --- API appelée par le graphe -------------------------------------------

    def phase(self, titre: str, detail: str = "") -> None:
        """Change de phase (plan, écriture scène 2/4, relecture, QA…)."""
        if not self.actif:
            return
        self.phase_courante = titre
        self.detail = detail
        self._toks_appel = 0
        self._t_appel = time.time()
        if self.interactif:
            self._dessiner(force=True)
        else:
            self._ligne(f"{titre}" + (f" — {detail}" if detail else ""))

    def note(self, message: str) -> None:
        """Événement ponctuel digne d'être vu (replanification, réparation…)."""
        if not self.actif:
            return
        if self.interactif:
            self.flux.write(_ANSI_EFFACE_LIGNE + _ANSI_DEBUT_LIGNE)
            self.flux.write(f"  · {message}\n")
            self._dessiner(force=True)
        else:
            self._ligne(f"  · {message}")

    def on_token(self, fragment: str, cumul: int) -> None:
        """Callback de streaming : un fragment vient d'arriver."""
        if not self.actif:
            return
        self._toks_appel = cumul
        self.gen_toks += 1
        if self.interactif:
            self._dessiner()

    def fin(self) -> None:
        """Rend la ligne au terminal (le panneau ne doit pas rester collé)."""
        if self.actif and self.interactif:
            self.flux.write(_ANSI_EFFACE_LIGNE + _ANSI_DEBUT_LIGNE)
            self.flux.flush()

    # --- rendu ---------------------------------------------------------------

    def _ligne(self, texte: str) -> None:
        ecoule = time.time() - self.t0
        self.flux.write(f"[{_mmss(ecoule)} / {_mmss(self.budget)}] {texte}\n")
        self.flux.flush()

    def _dessiner(self, *, force: bool = False) -> None:
        # Dix tokens par seconde suffiraient à redessiner dix fois par seconde,
        # ce qui ne se voit pas et coûte des écritures : on plafonne à 5 Hz.
        maintenant = time.time()
        if not force and maintenant - self._dernier_dessin < 0.2:
            return
        self._dernier_dessin = maintenant

        ecoule = maintenant - self.t0
        restant = self.budget - ecoule
        vitesse = self._toks_appel / max(0.1, maintenant - self._t_appel)
        # Le dépassement s'affiche en clair plutôt que de rester à zéro : sur
        # scène, mieux vaut savoir qu'on est à +2:30 que croire qu'il reste 0:00.
        horloge = (f"reste {_mmss(restant)}" if restant >= 0
                   else f"DÉPASSÉ de {_mmss(-restant)}")
        ligne = (
            f"⏱ {_mmss(ecoule)} / {_mmss(self.budget)} ({horloge})  "
            f"│ {self.phase_courante}"
            + (f" {self.detail}" if self.detail else "")
            + f"  │ {self._toks_appel} tok à {vitesse:.1f} tok/s"
            + f"  │ total {self.gen_toks}"
        )
        largeur = shutil.get_terminal_size((100, 24)).columns
        self.flux.write(_ANSI_EFFACE_LIGNE + _ANSI_DEBUT_LIGNE + ligne[:largeur - 1])
        self.flux.flush()


# Puits global. Le graphe l'utilise sans le connaître : par défaut il est
# inactif, donc importer le graphe depuis un test n'affiche rien.
SINK = Progress(actif=False)


def install(sink: Progress) -> None:
    """Remplace le puits global (appelé par run_chapter.py)."""
    global SINK
    SINK = sink


def phase(titre: str, detail: str = "") -> None:
    SINK.phase(titre, detail)


def note(message: str) -> None:
    SINK.note(message)


def on_token(fragment: str, cumul: int) -> None:
    SINK.on_token(fragment, cumul)


def token_sink():
    """Callback de streaming à passer à `llm`, ou None si l'affichage est
    inactif — pour que le mode non-streamé reste le chemin par défaut."""
    return on_token if SINK.actif else None
