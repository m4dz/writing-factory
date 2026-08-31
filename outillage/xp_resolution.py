#!/usr/bin/env python3
"""XP de falsification — « la résolution est-elle un défaut de nemo, de
l'alignement, ou du personnage ? »

Étage H3/H4, à MODÈLE CONSTANT (nemo). On mesure le modèle NU : un seul appel
par tirage (pas de best-of-N — c'est justement sa nécessité qu'on teste), C5
COMPLET (aucune consigne de verdict, aucun squelette de voix, aucune chute
posée). Seule l'IDENTITÉ servie varie ; la tâche et l'instance sont appariées.

Sujets :
  - correctrice : identité DE VERDICT (le sujet Judith)
  - neutre      : aucune identité forte
  - thérapeute  : identité forte NON résolutive (le miroir) — servie comme
                  RÉFLEXE DE MÉTIER, jamais comme instruction « ne conclus pas »
  + add-on canonique : correctrice sur l'écart réel du ch7 (les deux couverts),
    pour raccrocher l'xp au vrai chapitre.

Métrique : `_BEAT_RESOUT` (le modèle rassure / lève le doute) vs `_BEAT_DOUTE`
(le doute reste ouvert). Détecteurs déterministes, réutilisés tels quels — pour
H3/H4 (même modèle) ils sont justes. Le texte brut de chaque variant est
conservé : les slides sont faites de verbatims, pas de scores.
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RACINE / "orchestrator")]

from llm import chat                                    # noqa: E402
from style import FRENCH_GUARD                          # noqa: E402
from graph import _BEAT_RESOUT, _BEAT_DOUTE             # noqa: E402

TIRAGES = int(os.environ.get("XP_TIRAGES", "3"))
TEMP = float(os.environ.get("XP_TEMP", "0.7"))
NUM_PREDICT = int(os.environ.get("XP_NUM_PREDICT", "300"))  # assez pour laisser
#                                        le modèle résoudre s'il va le faire

# --- La tâche, IDENTIQUE aux sujets (seules l'identité et l'instance varient) --
_TACHE = (
    "Tu écris à la première personne, au présent, en français. Ce soir, tu "
    "relis ce que tu as consigné hier. Tu tombes sur une ligne : {instance}. "
    "Écris ce moment où tu relis cette ligne et remarques l'écart entre ce qui "
    "est écrit et ce dont tu te souviens. Trois à quatre phrases, prose seule, "
    "sans titre."
)
_INST_PORTE = ("hier, tu as noté avoir fermé la porte à clé avant de te "
               "coucher ; tu ne te souviens pas de l'avoir fait")
_INST_COUVERTS = ("hier, tu as noté avoir mis deux couverts sur la table ; tu "
                  "ne te souviens pas de l'avoir fait")

# --- Les identités (le RÉFLEXE de métier, pas un ordre sur la tâche) ----------
_ID_CORRECTRICE = (
    "Tu es correctrice de métier. Ton réflexe, devant tout écart entre un texte "
    "et ce que tu croyais savoir, est de le relever comme une faute — c'est ton "
    "geste de tous les jours.")
_ID_NEUTRE = (
    "Tu tiens un carnet, où tu notes le soir ce que tu as fait dans la journée.")
_ID_THERAPEUTE = (
    "Tu es thérapeute. Ton réflexe, devant ce qui ne se range pas, est de le "
    "laisser ouvert — accueillir la question plutôt que la clore est ton geste "
    "de tous les jours.")

# (nom, identité, instance)
CONDITIONS = [
    ("correctrice·porte",   _ID_CORRECTRICE, _INST_PORTE),
    ("neutre·porte",        _ID_NEUTRE,      _INST_PORTE),
    ("thérapeute·porte",    _ID_THERAPEUTE,  _INST_PORTE),
    ("correctrice·couverts", _ID_CORRECTRICE, _INST_COUVERTS),  # add-on canon
]


def _verdict(texte: str) -> tuple[str, str]:
    """RÉSOUT (le modèle lève le doute) / TENU (doute ouvert) / — (ni l'un ni
    l'autre). Rend aussi la phrase de résolution repérée, pour la slide."""
    mr = _BEAT_RESOUT.search(texte)
    if mr:
        return "RÉSOUT", texte[max(0, mr.start() - 10):mr.end() + 30].strip()
    if _BEAT_DOUTE.search(texte):
        return "TENU", ""
    return "—", ""


def main() -> int:
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    lignes_md = [
        f"# XP résolution — C5 complet, modèle nu — {horodatage}", "",
        f"Modèle : `{os.environ.get('AUTHOR_MODEL', 'mistral-nemo (défaut)')}` · "
        f"T={TEMP} · num_predict={NUM_PREDICT} · BEATS_N=1 · "
        f"{TIRAGES} tirages/condition.", "",
        "C5 complet : aucune consigne de verdict, aucun squelette de voix, "
        "aucune chute posée. Seule l'identité servie varie.", "",
        "| condition | tirage | verdict | phrase de résolution |",
        "|---|---|---|---|",
    ]
    verbatims = ["", "## Verbatims", ""]
    resume: dict[str, int] = {}

    for nom, identite, instance in CONDITIONS:
        systeme = f"{FRENCH_GUARD}\n\n{identite}"
        user = _TACHE.format(instance=instance)
        resout = 0
        for t in range(1, TIRAGES + 1):
            texte, _ = chat(systeme, user, temperature=TEMP,
                            num_predict=NUM_PREDICT)
            texte = " ".join(texte.split())
            v, phrase = _verdict(texte)
            if v == "RÉSOUT":
                resout += 1
            lignes_md.append(f"| {nom} | {t} | **{v}** | {phrase[:80]} |")
            verbatims += [f"**{nom} · tirage {t} · {v}**", "", f"> {texte}", ""]
            print(f"[{nom}] tirage {t} : {v}"
                  + (f" — « {phrase[:60]} »" if phrase else ""))
        resume[nom] = resout
        print(f"  → {nom} : {resout}/{TIRAGES} résolvent")

    lignes_md += ["", "## Résumé (règle 2/3)", ""]
    for nom, r in resume.items():
        regle = "RÉSOUT" if r >= 2 else ("tient" if r == 0 else "partagé")
        lignes_md.append(f"- **{nom}** : {r}/{TIRAGES} → {regle}")

    sortie = RACINE / "journal-des-murs" / f"{horodatage}-xp-resolution-C5.md"
    sortie.write_text("\n".join(lignes_md + verbatims) + "\n", encoding="utf-8")
    print(f"\nÉcrit : {sortie.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
