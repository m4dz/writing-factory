#!/usr/bin/env python3
"""Construit le Modelfile `auteur-test` depuis la fiche de style.

Lit bible/style/style-auteur.md, retire le frontmatter YAML (métadonnées
d'indexation, inutiles au modèle), et produit un Modelfile avec la fiche
complète en prompt système.

Ce Modelfile mesure le PLAFOND : la fiche entière en contexte, sans RAG. Ce
n'est pas la forme de production — LangGraph servira plus tard des morceaux de
la fiche VALIDÉE. On ne câble pas l'orchestration sur une fiche non calibrée.

Usage :
  python outillage/build_modelfile.py
  python outillage/build_modelfile.py --temperature 0.9

Puis :
  ollama create auteur-test -f Modelfile.auteur-test

Stdlib uniquement : aucun pip install requis sur la machine hôte.
"""

import argparse
import sys
from pathlib import Path

# `orchestrator/` n'est pas un paquet installable : on l'ajoute au chemin pour
# importer FRENCH_GUARD depuis sa source unique plutôt que d'en recopier le
# texte ici. Une garde recopiée diverge le jour où l'originale bouge, et le
# test mesurerait alors autre chose que la production. style.py n'importe que
# `re` : l'outillage reste stdlib.
from factory.paths import BIBLE_DIR
from factory.text import FRENCH_GUARD

# Même valeur que `write_node` (graph.py). Sans plafond explicite, une scène
# coupée en cours de route ferait échouer les lignes « clôture » et
# « phrase-couperet » de la grille pour une raison MÉCANIQUE, et on irait
# durcir un chunk de la fiche qui n'a rien fait.
NUM_PREDICT = 1400

# Tag COMPLET du modèle de scène. `mistral-nemo` tout court n'existe pas en
# local : ollama partirait puller une autre quantification, donc un autre
# modèle que celui de la démo — et le verdict de style ne transférerait pas.
BASE_MODEL = "mistral-nemo:12b-instruct-2407-q8_0"


def strip_frontmatter(text: str) -> str:
    """Retire le bloc YAML entre les deux premiers `---`."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[i + 1:]).strip()
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fiche", default=str(BIBLE_DIR / "style-auteur.md"))
    parser.add_argument("--base", default=BASE_MODEL,
                        help="Modèle Ollama de base (tag COMPLET)")
    parser.add_argument("--name", default="auteur-test",
                        help="Nom du modèle à créer (informatif)")
    # Même température que `write_node` (graph.py) : une fiche calibrée à 0.8
    # puis déployée à 0.7 ne rend pas la même chose. run_scene.py surcharge
    # cette valeur par run (le protocole demande 0.7 / 0.7 / 0.9) ; celle-ci
    # reste le défaut d'un `ollama run auteur-test` interactif.
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--out", default=None,
                        help="Chemin du Modelfile (défaut : Modelfile.{name})")
    args = parser.parse_args()

    fiche_path = Path(args.fiche)
    if not fiche_path.is_file():
        print(f"ERREUR : fiche introuvable : {fiche_path}", file=sys.stderr)
        print("Place style-auteur.md dans bible/style/ d'abord.", file=sys.stderr)
        return 1

    body = strip_frontmatter(fiche_path.read_text(encoding="utf-8"))

    # La garde française précède la fiche, comme en production : llm.py préfixe
    # TOUT prompt système par FRENCH_GUARD. Sans elle, on mesurerait nemo sans
    # sa garde, et la grille se remplirait de fuites d'anglais que le pipeline
    # traite déjà — attention du relecteur brûlée sur un faux problème.
    system = f"{FRENCH_GUARD}\n\n{body}"

    if '"""' in system:
        print("ERREUR : la fiche contient une séquence \"\"\" qui casserait "
              "le Modelfile. Corrige-la d'abord.", file=sys.stderr)
        return 1

    out_path = Path(args.out or f"Modelfile.{args.name}")
    out_path.write_text(
        f"FROM {args.base}\n"
        f"PARAMETER temperature {args.temperature}\n"
        f"PARAMETER num_ctx {args.num_ctx}\n"
        f"PARAMETER num_predict {NUM_PREDICT}\n"
        f'SYSTEM """\n{system}\n"""\n',
        encoding="utf-8",
    )
    print(f"Modelfile écrit : {out_path}")
    print(f"  base={args.base}  temperature={args.temperature}  "
          f"num_ctx={args.num_ctx}  num_predict={NUM_PREDICT}")
    print(f"  fiche : {fiche_path} ({len(body)} caractères après frontmatter)")
    print(f"  + FRENCH_GUARD en tête ({len(system)} caractères de SYSTEM)")
    print(f"\nCréer le modèle :\n  ollama create {args.name} -f {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
