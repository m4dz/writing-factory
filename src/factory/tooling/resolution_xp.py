#!/usr/bin/env python3
"""Falsification experiment: is the resolution a defect of the model, of the
alignment, or of the character?

Measures the BARE model: one call per draw (no best-of-N, whose necessity is
what is tested), FULL C5 (no verdict instruction, no voice skeleton, no posed
fall). Only the served IDENTITY varies; task and instance are paired. First
outcome recorded in ADR-0020 (`experiments/runs/20260831-xp-resolution-c5/`).

Since `xp-abliterated-nemo` the recipe is a driver for a model comparison:
`--model` names the author model of the series, `--out` its directory under
`experiments/runs/`, and a manifest records the tag Ollama answered with, the
commit, the draws and both clocks. A fifth condition serves the production
voice chunk (`judith::voix`, through the indexer's own firewall) as the
POSITIVE CONTROL: the setup known to make stock nemo resolve. An arm that does
not resolve there has a detector reading that is not trusted (doctrine 4,
applied per arm).

Subjects:
  - proofreader: VERDICT identity (the Judith subject)
  - neutral:     no strong identity
  - therapist:   strong NON-resolving identity (the mirror), served as a
                 PROFESSIONAL REFLEX, never as an instruction « ne conclus pas »
  + canon extension: proofreader over the real gap of ch7 (the two place
    settings), to tie the experiment back to the actual chapter.
  + positive control: proofreader + the served voice chunk (production).

Metric: `_BEAT_RESOLVES` (the model reassures / lifts the doubt) vs
`_BEAT_DOUBT` (the doubt stays open). Deterministic detectors reused as they
are; at constant detector, the two arms are read the same way. The raw text of
every variant is kept: the slides are made of verbatims, not scores.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from factory.infra import ollama
from factory.infra.ollama import chat
from factory.paths import REPO_ROOT
from factory.pipeline.graph import _BEAT_DOUBT, _BEAT_RESOLVES
from factory.runs import Clocks, git_commit
from factory.settings import settings
from factory.text import FRENCH_GUARD

VOICE_CHUNK_ID = "judith::voix"

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

# (name, identity, instance). The control's identity is completed at run time
# with the voice chunk read from the sheet: no copy of author material in code.
CONTROL = "correctrice·porte·squelette"
CONDITIONS = [
    ("correctrice·porte",    _ID_PROOFREADER, _INST_DOOR),
    ("neutre·porte",         _ID_NEUTRAL,     _INST_DOOR),
    ("thérapeute·porte",     _ID_THERAPIST,   _INST_DOOR),
    ("correctrice·couverts", _ID_PROOFREADER, _INST_PLACE_SETTINGS),  # canon extension
    (CONTROL,                _ID_PROOFREADER, _INST_DOOR),            # positive control
]


class RecipeError(RuntimeError):
    """The series cannot be recorded honestly: missing model, empty control."""


def verdict(text: str) -> tuple[str, str]:
    """RÉSOUT (the model lifts the doubt) / TENU (doubt open) / — (neither).
    Also returns the resolution sentence spotted, for the slide."""
    mr = _BEAT_RESOLVES.search(text)
    if mr:
        return "RÉSOUT", text[max(0, mr.start() - 10):mr.end() + 30].strip()
    if _BEAT_DOUBT.search(text):
        return "TENU", ""
    return "—", ""


def voice_chunk(sheet: Path | None = None) -> str:
    """The `judith::voix` document exactly as the indexer builds it: same
    section split, same layer filter, same name translation. The control
    serves what production serves, through the same firewall, and fails
    explicitly rather than run on an empty control."""
    from factory.retrieval.indexer import index_file

    path = sheet or settings.bible_dir / "fiche-judith.md"
    if not path.is_file():
        raise RecipeError(f"fiche absente : {path}")
    ids, documents, _ = index_file(path, None)
    for chunk_id, document in zip(ids, documents):
        if chunk_id == VOICE_CHUNK_ID and document.strip():
            return document.strip()
    raise RecipeError(f"chunk {VOICE_CHUNK_ID} vide ou absent dans {path.name}")


def resolve_model(tag: str) -> dict:
    """`{name, digest}` of the tag as Ollama has it, or a RecipeError."""
    try:
        present = ollama.tags()
    except OSError as exc:
        raise RecipeError(f"Ollama injoignable ({exc})") from exc
    for entry in present:
        name = entry.get("name", "")
        if name == tag or name.split(":")[0] == tag:
            return {"name": name, "digest": entry.get("digest", "")}
    raise RecipeError(f"modèle absent d'Ollama : {tag} (ollama pull)")


def run_series(out: Path, *, model: str, draws: int, temperature: float,
               num_predict: int) -> dict:
    """Draw every condition `draws` times on `model`; write `raw.md` and
    `manifest.yaml` into `out`; return the manifest."""
    resolved = resolve_model(model)
    control = voice_chunk()
    out.mkdir(parents=True, exist_ok=True)
    clocks = Clocks()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    md_lines = [
        f"# XP résolution — C5 complet, modèle nu — {out.name}", "",
        f"Modèle : `{resolved['name']}` · T={temperature} · num_predict={num_predict} "
        f"· BEATS_N=1 · {draws} tirages/condition.", "",
        "C5 complet : aucune consigne de verdict, aucun squelette de voix, "
        f"aucune chute posée. Seule l'identité servie varie ; la condition « {CONTROL} » "
        "est le témoin positif (chunk voix de production servi).", "",
        "| condition | tirage | verdict | phrase de résolution |",
        "|---|---|---|---|",
    ]
    verbatims = ["", "## Verbatims", ""]
    verdicts: dict[str, dict] = {}

    for name, identity, instance in CONDITIONS:
        served_identity = f"{identity}\n\n{control}" if name == CONTROL else identity
        system = f"{FRENCH_GUARD}\n\n{served_identity}"
        user = _TASK.format(instance=instance)
        counts = {"RÉSOUT": 0, "TENU": 0, "—": 0}
        for t in range(1, draws + 1):
            text, _ = chat(system, user, model=resolved["name"],
                           temperature=temperature, num_predict=num_predict)
            text = " ".join(text.split())
            v, sentence = verdict(text)
            counts[v] += 1
            md_lines.append(f"| {name} | {t} | **{v}** | {sentence[:80]} |")
            verbatims += [f"**{name} · tirage {t} · {v}**", "", f"> {text}", ""]
            print(f"[{name}] tirage {t} : {v}"
                  + (f" — « {sentence[:60]} »" if sentence else ""))
        verdicts[name] = {"resolves": counts["RÉSOUT"], "holds": counts["TENU"],
                          "neither": counts["—"]}
        print(f"  → {name} : {counts['RÉSOUT']}/{draws} résolvent")

    md_lines += ["", "## Résumé (règle 2/3)", ""]
    for name, c in verdicts.items():
        r = c["resolves"]
        rule = "RÉSOUT" if r >= 2 else ("tient" if r == 0 else "partagé")
        md_lines.append(f"- **{name}** : {r}/{draws} → {rule}")
    control_ok = verdicts[CONTROL]["resolves"] >= 2
    md_lines += ["", f"Témoin positif : {'RÉSOUT' if control_ok else 'NE RÉSOUT PAS'} "
                 f"({verdicts[CONTROL]['resolves']}/{draws}) — "
                 + ("lecture du détecteur fiable sur ce bras."
                    if control_ok else
                    "la lecture du détecteur sur ce bras n'est PAS fiable.")]

    (out / "raw.md").write_text("\n".join(md_lines + verbatims) + "\n", encoding="utf-8")
    manifest = {
        "id": out.name, "kind": "experiment-series", "recipe": "resolution_xp",
        "model": resolved, "commit": git_commit(), "started": started,
        "draws": draws, "temperature": temperature, "num_predict": num_predict,
        "conditions": [name for name, _, _ in CONDITIONS], "control": CONTROL,
        "control_resolves": control_ok, "verdicts": verdicts, "timings": clocks.read(),
        "raw": "raw.md",
    }
    (out / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="factory-xp-resolution",
        description="Bare-model resolution series (C5), one model tag per series.")
    p.add_argument("--model", default=None,
                   help="Ollama tag of the author model (défaut : AUTHOR_MODEL)")
    p.add_argument("--out", required=True,
                   help="series directory, e.g. experiments/runs/<date>-xp-abliterated-nemo/leg1-S")
    p.add_argument("--draws", type=int, default=None, help="tirages par condition (défaut : XP_DRAWS)")
    args = p.parse_args(argv)
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out
    try:
        manifest = run_series(
            out, model=args.model or settings.author_model,
            draws=args.draws or settings.xp_draws,
            temperature=settings.xp_temperature, num_predict=settings.xp_num_predict)
    except RecipeError as exc:
        print(f"série refusée : {exc}", file=sys.stderr)
        return 1
    print(f"\nÉcrit : {out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out} "
          f"(modèle {manifest['model']['name']}, témoin positif "
          f"{'ok' if manifest['control_resolves'] else 'NON'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
