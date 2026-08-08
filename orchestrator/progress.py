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

# Bandes d'avancement par phase, en fraction du travail total. Les bornes sont
# grossières et c'est assumé : elles servent à faire progresser une barre pour
# la salle, pas à prédire une fin. Elles vivent ICI et non dans les nœuds du
# graphe, pour qu'on puisse les recaler après une répétition sans toucher au
# pipeline. Mesures du run de référence (17,0 min, 4 scènes) : le plan pèse
# ~2 min, l'écriture ~7, la relecture ~5, la QA ~3.
BANDES = {
    "Invariants de la bible": (0.00, 0.04),
    "Plan de scènes": (0.04, 0.10),
    "Contrôle du plan contre la bible": (0.10, 0.12),
    "Écriture": (0.12, 0.55),
    "Relecture": (0.55, 0.80),
    "Bascule des modèles": (0.80, 0.81),
    "Réparation linguistique": (0.81, 0.90),
    "Cohérence par faits": (0.90, 0.97),
    "Lecture en voix clonée": (0.97, 1.00),
}

# Phases telles que le deck les connaît (contrat gelé côté talk :
# `GenStatus`). Notre granularité interne est plus fine ; on la projette.
PHASES_DECK = {
    "Lecture en voix clonée": "tts",
}


class Annulation(RuntimeError):
    """Le job en cours a été annulé par l'opérateur.

    Levée depuis `phase()`, c'est-à-dire aux FRONTIÈRES DE NŒUD du graphe : on
    ne peut pas tuer proprement un thread Python, mais on peut refuser de passer
    à l'étape suivante. Le pire délai est donc la durée d'un appel au modèle
    (~2 min sur une écriture de scène), pas l'éternité.
    """


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
        self.phase_deck = "generating"   # projection sur le contrat du deck
        self.avancement = 0.0            # fraction 0..1, monotone
        self.gen_toks = 0          # tokens du chapitre entier
        self.annule = False              # demande d'arrêt de l'opérateur
        self.notes: list[str] = []       # événements marquants, pour /status
        self._toks_appel = 0       # tokens de l'appel en cours
        self._dernier_dessin = 0.0
        self._t_appel = 0.0

    # --- API appelée par le graphe -------------------------------------------

    def phase(self, titre: str, detail: str = "", *,
              i: int | None = None, n: int | None = None) -> None:
        """Change de phase (plan, écriture scène 2/4, relecture, QA…).

        `i`/`n` situent l'étape dans sa bande d'avancement (scène 2 sur 4). Les
        nœuds les fournissent quand ils les connaissent ; sans eux, la phase
        vaut le début de sa bande.

        Ce calcul tourne MÊME si l'affichage est inactif : `/status` doit pouvoir
        rendre un avancement quand le serveur HTTP n'écrit rien sur un terminal.
        """
        if self.annule:
            raise Annulation("génération annulée par l'opérateur")
        debut, fin = BANDES.get(titre, (self.avancement, self.avancement))
        part = (i / n) if (i is not None and n) else 0.0
        # Monotone : un avancement qui recule (replanification, phase inconnue)
        # se lit comme un bug depuis la salle.
        self.avancement = max(self.avancement, debut + (fin - debut) * part)
        self.phase_courante = titre
        self.detail = detail
        self.phase_deck = PHASES_DECK.get(titre, "generating")
        if not self.actif:
            return
        self._toks_appel = 0
        self._t_appel = time.time()
        if self.interactif:
            self._dessiner(force=True)
        else:
            self._ligne(f"{titre}" + (f" — {detail}" if detail else ""))

    def note(self, message: str) -> None:
        """Événement ponctuel digne d'être vu (replanification, réparation…)."""
        # Conservées même en mode inactif : ce sont elles que `/status` et les
        # notifications téléphone relaient, et le serveur HTTP n'a pas de
        # terminal. Bornées, sinon un run long les accumule sans fin.
        self.notes.append(message)
        del self.notes[:-20]
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

    def instantane(self) -> dict:
        """État courant, pour `GET /status` et les notifications.

        `phase` est la valeur du CONTRAT GELÉ côté deck
        (`generating` | `tts` | `ready`, cf. talk/openspec remote-integration) ;
        tout le reste est additif et le deck peut l'ignorer sans rien perdre —
        c'est la condition pour enrichir l'affichage sans casser le contrat.
        """
        return {
            "phase": self.phase_deck,
            "ready": False,
            "progress": round(self.avancement, 3),
            "label": self.phase_courante,
            "detail": self.detail,
            "elapsed_s": int(time.time() - self.t0),
            "budget_s": int(self.budget),
            "gen_toks": self.gen_toks,
            "notes": list(self.notes[-5:]),
        }

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


def phase(titre: str, detail: str = "", *,
          i: int | None = None, n: int | None = None) -> None:
    SINK.phase(titre, detail, i=i, n=n)


def note(message: str) -> None:
    SINK.note(message)


def on_token(fragment: str, cumul: int) -> None:
    SINK.on_token(fragment, cumul)


def token_sink():
    """Callback de streaming à passer à `llm`, ou None si l'affichage est
    inactif — pour que le mode non-streamé reste le chemin par défaut."""
    return on_token if SINK.actif else None
