#!/usr/bin/env python3
"""Session de calibration 2 — chapitre 2 de L'Involontaire, frappe directe.

Exécute le plan de runs du §2 de `protocole-calibration-ch2.md`. Le prompt est
STRICTEMENT le couple fiche v3 (prompt système, via le Modelfile) + brief
machine du §1 (message utilisateur) : aucun RAG, aucune bible, aucun contexte
additionnel. C'est la condition pour que toute divergence observée soit
imputable au couple fiche + brief, et à rien d'autre.

Séparé de `run_scene.py` plutôt que greffé dessus : ce dernier lit un brief de
SCÈNE et retire des lignes « Régime : … » pour son contrôle, là où la session 2
lit un brief de CHAPITRE et retire des lignes de BEATS. Tordre un script pour
deux protocoles différents, c'est se garantir de casser le premier en servant
le second.

Deux écarts assumés au « rien d'autre » du protocole, tous deux dans le sens de
la comparabilité avec la session 1 :
  - `FRENCH_GUARD` reste en tête du prompt système. Il y était en session 1 ;
    l'enlever changerait plus que la fiche entre les deux sessions.
  - La boucle de renvoi de `run_scene.py` est ABSENTE ici. Elle ajouterait des
    tours de conversation et corrigerait le modèle : on mesurerait alors la
    boucle, pas le couple fiche + brief.

Usage :
  python3 outillage/run_ch2.py                 # les 6 runs du protocole
  python3 outillage/run_ch2.py --seulement 1 C # sous-ensemble

Stdlib uniquement.
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orchestrator"))
from lint_style import analyse  # noqa: E402
from style import ends_mid_sentence  # noqa: E402

OLLAMA_URL = "http://localhost:11434"

# Plan de runs du §2. X1/X2 sont HORS SCORE : ils explorent la plage de
# température, ils ne comptent pas dans la règle des 2 sur 3.
PLAN = [
    ("1", 0.7, True, "score"),
    ("2", 0.7, True, "score"),
    ("3", 0.7, True, "score"),
    ("C", 0.7, False, "contrôle — brief sans les lignes de beats"),
    ("X1", 0.5, True, "exploration, hors score"),
    ("X2", 0.9, True, "exploration, hors score"),
]

# Le brief machine vit dans un bloc de citation sous « ## 1. Brief machine ».
SECTION_BRIEF = re.compile(
    r"^## 1\. Brief machine.*?$(.*?)(?=^## )", re.MULTILINE | re.DOTALL)

# Les lignes de beats : l'énumération numérotée, plus son en-tête. Ce sont
# elles que le run C retire — pas les interdits ni le matériau imposé, qui
# appartiennent au cadre et non à la dramaturgie.
LIGNE_BEAT = re.compile(r"^\s*\d+\.\s+\*\*.+$", re.MULTILINE)
ENTETE_BEATS = re.compile(r"^\s*\*\*Beats, dans l'ordre :\*\*\s*$", re.MULTILINE)


def extraire_brief(protocole: Path) -> str:
    """Rend le brief machine du §1, débarrassé du balisage de citation."""
    texte = protocole.read_text(encoding="utf-8")
    m = SECTION_BRIEF.search(texte)
    if not m:
        sys.exit(f"ERREUR : section '## 1. Brief machine' introuvable dans {protocole}")
    lignes = [re.sub(r"^\s*>\s?", "", l) for l in m.group(1).splitlines()]
    return "\n".join(lignes).strip()


def sans_beats(brief: str) -> tuple[str, int]:
    """Retire les beats numérotés et leur en-tête (run de contrôle)."""
    brief, n = LIGNE_BEAT.subn("", brief)
    brief, n_entete = ENTETE_BEATS.subn("", brief)
    brief = re.sub(r"\n{3,}", "\n\n", brief)
    return brief.strip(), n + n_entete


def chat(model: str, prompt: str, temperature: float, timeout: int) -> dict:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--protocole", default="experiments/reports/protocole-calibration-ch2.md")
    p.add_argument("--model", default="auteur-test")
    p.add_argument("--out-dir", default="experiments/runs/ch2-calibration")
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--seulement", nargs="*", default=None,
                   help="Identifiants de runs à exécuter (défaut : tous)")
    args = p.parse_args()

    brief_complet = extraire_brief(Path(args.protocole))
    brief_controle, retires = sans_beats(brief_complet)
    print(f"Brief machine : {len(brief_complet)} caractères")
    print(f"Brief de contrôle : {retires} lignes de beats retirées, "
          f"{len(brief_controle)} caractères")
    if retires == 0:
        print("ATTENTION : aucune ligne de beat retirée — le run C serait "
              "identique aux runs de score.", file=sys.stderr)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True)

    consigne = ("Rédige le chapitre décrit dans le brief ci-dessous. Rends "
                "uniquement le texte du chapitre, sans titre ni commentaire.\n\n")

    plan = [r for r in PLAN
            if args.seulement is None or r[0] in args.seulement]
    for ident, temp, avec_beats, role in plan:
        brief = brief_complet if avec_beats else brief_controle
        print(f"[run-{ident}] T={temp} ({role})…", flush=True)
        res = chat(args.model, consigne + brief, temp, args.timeout)
        texte = res["message"]["content"].strip()
        duree = res.get("total_duration", 0) / 1e9
        done = res.get("done_reason", "?")
        n_mots = len(texte.split())

        lint = analyse(texte)
        alertes = []
        if done == "length":
            alertes.append("TRONQUÉ par num_predict")
        if ends_mid_sentence(texte):
            alertes.append("fin pendante")

        chemin = out_dir / f"run-{ident}.md"
        chemin.write_text(
            "---\n"
            f"run: {ident}\n"
            f"role: {role}\n"
            f"model: {args.model}\n"
            f"fiche: style-auteur v3\n"
            f"brief: protocole-calibration-ch2.md §1"
            f"{'' if avec_beats else ' (sans lignes de beats)'}\n"
            f"rag: aucun (frappe directe)\n"
            f"temperature: {temp}\n"
            f"date: {datetime.now().isoformat(timespec='seconds')}\n"
            f"mots: {n_mots}\n"
            f"duree_s: {duree:.0f}\n"
            f"done_reason: {done}\n"
            f"entrees: {lint['entrees']}\n"
            f"alertes: {alertes if alertes else '[]'}\n"
            "---\n\n" + texte + "\n",
            encoding="utf-8",
        )
        cible = "OK" if 450 <= n_mots <= 600 else "HORS CIBLE (450-600)"
        print(f"[run-{ident}] {n_mots} mots [{cible}], {duree:.0f}s, "
              f"done={done} → {chemin}")
        for a in alertes:
            print(f"  ⚠ {a}", file=sys.stderr)

    print(f"\nGrille : python3 outillage/grille_session.py {args.out_dir} "
          "> grille-lint-session-3.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
