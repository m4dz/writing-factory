#!/usr/bin/env python3
"""Falsification experiment: is the resolution a defect of nemo, of the
alignment, or of the character?

Stage H3/H4 at CONSTANT MODEL (nemo). Measures the BARE model: one call per
draw (no best-of-N, whose necessity is what is tested), FULL C5 (no verdict
instruction, no voice skeleton, no posed fall). Only the served IDENTITY varies;
task and instance are paired. Outcome recorded in ADR-0020.

Subjects:
  - proofreader: VERDICT identity (the Judith subject)
  - neutral:     no strong identity
  - therapist:   strong NON-resolving identity (the mirror), served as a
                 PROFESSIONAL REFLEX, never as an instruction « ne conclus pas »
  + canon extension: proofreader over the real gap of ch7 (the two place
    settings), to tie the experiment back to the actual chapter.

Metric: `_BEAT_RESOLVES` (the model reassures / lifts the doubt) vs
`_BEAT_DOUBT` (the doubt stays open). Deterministic detectors reused as they
are; for H3/H4 (same model) they are exact. The raw text of every variant is
kept: the slides are made of verbatims, not scores.
"""

import sys
from datetime import datetime, timezone

from factory.paths import REPO_ROOT as RACINE

from factory.infra.ollama import chat                                  
from factory.text import FRENCH_GUARD                        
from factory.pipeline.graph import _BEAT_RESOLVES, _BEAT_DOUBT           

from factory.settings import settings

DRAWS = settings.xp_draws
TEMPERATURE = settings.xp_temperature
NUM_PREDICT = settings.xp_num_predict  # enough room for the model to resolve
#                                        when it is going to

# --- The task, IDENTICAL across subjects (only identity and instance vary) ----
_TASK = (
    "Tu écris à la première personne, au présent, en français. Ce soir, tu "
    "relis ce que tu as consigné hier. Tu tombes sur une ligne : {instance}. "
    "Écris ce moment où tu relis cette ligne et remarques l'écart entre ce qui "
    "est écrit et ce dont tu te souviens. Trois à quatre phrases, prose seule, "
    "sans titre."
)
_INST_DOOR = ("hier, tu as noté avoir fermé la porte à clé avant de te "
               "coucher ; tu ne te souviens pas de l'avoir fait")
_INST_PLACE_SETTINGS = ("hier, tu as noté avoir mis deux couverts sur la table ; tu "
                  "ne te souviens pas de l'avoir fait")

# --- The identities (the professional REFLEX, not an order about the task) ----
_ID_PROOFREADER = (
    "Tu es correctrice de métier. Ton réflexe, devant tout écart entre un texte "
    "et ce que tu croyais savoir, est de le relever comme une faute — c'est ton "
    "geste de tous les jours.")
_ID_NEUTRAL = (
    "Tu tiens un carnet, où tu notes le soir ce que tu as fait dans la journée.")
_ID_THERAPIST = (
    "Tu es thérapeute. Ton réflexe, devant ce qui ne se range pas, est de le "
    "laisser ouvert — accueillir la question plutôt que la clore est ton geste "
    "de tous les jours.")

# (name, identity, instance)
CONDITIONS = [
    ("correctrice·porte",   _ID_PROOFREADER, _INST_DOOR),
    ("neutre·porte",        _ID_NEUTRAL,      _INST_DOOR),
    ("thérapeute·porte",    _ID_THERAPIST,  _INST_DOOR),
    ("correctrice·couverts", _ID_PROOFREADER, _INST_PLACE_SETTINGS),  # canon extension
]


def _verdict(text: str) -> tuple[str, str]:
    """RÉSOUT (the model lifts the doubt) / TENU (doubt open) / — (neither).
    Also returns the resolution sentence spotted, for the slide."""
    mr = _BEAT_RESOLVES.search(text)
    if mr:
        return "RÉSOUT", text[max(0, mr.start() - 10):mr.end() + 30].strip()
    if _BEAT_DOUBT.search(text):
        return "TENU", ""
    return "—", ""


def main() -> int:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    md_lines = [
        f"# XP résolution — C5 complet, modèle nu — {timestamp}", "",
        f"Modèle : `{settings.author_model}` · "
        f"T={TEMPERATURE} · num_predict={NUM_PREDICT} · BEATS_N=1 · "
        f"{DRAWS} tirages/condition.", "",
        "C5 complet : aucune consigne de verdict, aucun squelette de voix, "
        "aucune chute posée. Seule l'identité servie varie.", "",
        "| condition | tirage | verdict | phrase de résolution |",
        "|---|---|---|---|",
    ]
    verbatims = ["", "## Verbatims", ""]
    summary: dict[str, int] = {}

    for name, identity, instance in CONDITIONS:
        system = f"{FRENCH_GUARD}\n\n{identity}"
        user = _TASK.format(instance=instance)
        resolves = 0
        for t in range(1, DRAWS + 1):
            text, _ = chat(system, user, temperature=TEMPERATURE,
                            num_predict=NUM_PREDICT)
            text = " ".join(text.split())
            v, sentence = _verdict(text)
            if v == "RÉSOUT":
                resolves += 1
            md_lines.append(f"| {name} | {t} | **{v}** | {sentence[:80]} |")
            verbatims += [f"**{name} · tirage {t} · {v}**", "", f"> {text}", ""]
            print(f"[{name}] tirage {t} : {v}"
                  + (f" — « {sentence[:60]} »" if sentence else ""))
        summary[name] = resolves
        print(f"  → {name} : {resolves}/{DRAWS} résolvent")

    md_lines += ["", "## Résumé (règle 2/3)", ""]
    for name, r in summary.items():
        rule = "RÉSOUT" if r >= 2 else ("tient" if r == 0 else "partagé")
        md_lines.append(f"- **{name}** : {r}/{DRAWS} → {rule}")

    output = RACINE / "experiments" / "journal" / f"{timestamp}-xp-resolution-C5.md"
    output.write_text("\n".join(md_lines + verbatims) + "\n", encoding="utf-8")
    print(f"\nÉcrit : {output.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
