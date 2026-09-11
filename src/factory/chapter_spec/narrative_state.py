#!/usr/bin/env python3
"""Génère le chunk 7 (état narratif) de la fiche Judith — item 2, session 5.

Le chunk ne COPIE plus la table de pilotage, il la RACONTE en langue du monde.
C'est tout l'objet du correctif : servi en langue de production (« Régime 1,
grade 1. Verdict imposé : erreur de relevé. Ratio : commentaire dominant. »),
il apprenait au modèle à remplir un formulaire — et l'étage B a écrit des
formulaires. Un contexte en langue de tableau produit de la prose en langue de
tableau.

Discipline canonique (notes d'outillage §6) : **la table est la source, le
chunk est un artefact généré**. Jamais l'inverse, jamais d'édition à la main
entre deux chapitres.

Le chunk décrit l'état au MOMENT OÙ ELLE OUVRE le chapitre N — donc ce que le
chapitre N-1 a laissé. Écrire l'état du chapitre courant reviendrait à lui
donner sa propre fin avant de l'avoir écrite.

Usage :
  python3 outillage/build_etat_narratif.py --chapitre 2
  python3 outillage/build_etat_narratif.py --chapitre 2 --dry-run

Stdlib uniquement.
"""

import argparse
import re
import sys

from factory.paths import REPO_ROOT as RACINE
TABLE = RACINE / "bible" / "profond" / "chronologie-partie-double.md"
SHEET = RACINE / "bible" / "fiche-judith.md"

# Le début de chapitre 1 n'a pas de veille : rien à raconter, seulement le
# dispositif en place.
OPENING = (
    "Le dispositif est installé depuis peu : le cahier du soir, le manuscrit "
    "qui tarde, le carnet pour garder la main. Elle relit chaque soir l'entrée "
    "de la veille et la commente. Rien n'a encore cloché."
)


def read_table() -> dict[int, dict]:
    """Lignes de la table de pilotage, indexées par numéro de chapitre.

    La table vit dans un fichier FIREWALLÉ côté modèle. L'outillage a le droit
    de la lire : un générateur n'est pas un modèle, il ne raconte rien de ce
    qu'il ne doit pas — c'est précisément son travail de traduire.
    """
    lines: dict[int, dict] = {}
    if not TABLE.is_file():
        return lines
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 12 and cells[1].isdigit():
            lines[int(cells[1])] = {
                "verdict": cells[5], "marche": cells[6], "objets": cells[10],
                # La colonne « Événement réel payeur » est LA COLONNE RÉELLE —
                # la vérité profonde de la partie double. Elle n'est PAS lue :
                # la traduire reviendrait à servir au modèle auteur ce que tout
                # le firewall existe pour lui cacher. (Et sur le chapitre 1
                # elle produisait « le journal prescrit », où « journal » est
                # de surcroît un mot banni du brief.)
            }
    return lines


def read_anchors() -> dict[int, str]:
    """Ancres de continuité, lues dans les blocs [VALEURS] de la fiche.

    Côté PERÇU, contrairement à la colonne réelle de la table : l'ancre dit ce
    qu'elle a constaté, pas ce qui s'est produit. C'est la seule formulation de
    la divergence qu'on ait le droit de lui servir.
    """
    anchors: dict[int, str] = {}
    if not SHEET.is_file():
        return anchors
    for block in re.finditer(
            r"### \[VALEURS — chapitre (\d+).*?\](.*?)(?=^### |^## |\Z)",
            SHEET.read_text(encoding="utf-8"), re.MULTILINE | re.DOTALL):
        m = re.search(r"Ancre\s*:\s*([^.]*(?:\.[^.]*?)??)(?=\s*(?:Interdits|$))",
                      block.group(2), re.DOTALL)
        if m:
            anchors[int(block.group(1))] = " ".join(m.group(1).split()).rstrip(" .;")
    return anchors


def narrate(previous: dict | None) -> str:
    """Traduit une ligne de table en langue du monde.

    Aucun terme de pilotage ne survit : ni régime, ni grade, ni ratio, ni
    chaleur — ce sont des réglages de fabrication, pas des faits qu'elle
    pourrait connaître. Ne restent que ce qu'elle a constaté, ce qu'elle a
    conclu, et ce qu'elle a décidé.
    """
    if previous is None:
        return OPENING

    verdict = previous["verdict"]
    sentences: list[str] = []

    # L'ancre porte souvent DÉJÀ le verdict et la résolution : elle est écrite
    # comme une phrase de récit, pas comme un champ. On ne rajoute donc que ce
    # qu'elle ne dit pas — sans quoi l'état narratif répète le verdict deux
    # fois en trois lignes, et c'est exactement la langue de formulaire qu'on
    # cherche à faire disparaître.
    anchor = (previous.get("ancre") or "").strip()
    if anchor:
        sentences.append(anchor[0].upper() + anchor[1:] + ".")

    def already_said(what: str) -> bool:
        return bool(what) and what.lower() in anchor.lower()

    core = "" if verdict.startswith("aucun") else re.split(r"\s*\(", verdict)[0].strip()
    if verdict.startswith("aucun"):
        if not anchor:
            sentences.append("Elle n'a rien relevé d'anormal.")
    elif not already_said(core):
        sentences.append(f"Verdict rendu : {core}, la faute à elle.")

    pace = previous.get("marche", "").strip()
    if pace and pace not in ("—", "aucune"):
        first = re.split(r"\s*(?:→|,)\s*", pace)[0].strip()
        if not already_said(first):
            sentences.append(f"L'explication qu'elle s'est donnée : {first}.")

    # La résolution de pointer plus précisément RÉPOND à une anomalie : après
    # un chapitre sans verdict, elle ne suit rien.
    if core and not any(m in anchor.lower()
                         for m in ("résolution", "résolu", "pointer")):
        sentences.append("Elle a résolu de pointer plus précisément.")

    objects = previous.get("objets", "").split(";")[0].strip()
    if objects:
        sentences.append(f"Ce qu'elle a sous la main, ces jours-ci : {objects}.")

    return " ".join(sentences)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--chapitre", type=int, required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    table, anchors = read_table(), read_anchors()
    previous = table.get(args.chapitre - 1)
    if previous is not None:
        previous = {**previous, "ancre": anchors.get(args.chapitre - 1, "")}
    if args.chapitre > 1 and previous is None:
        print(f"ERREUR : pas de ligne pour le chapitre {args.chapitre - 1} "
              f"dans {TABLE}", file=sys.stderr)
        return 1

    narrative = narrate(previous)
    narrative_block = (
        "### [SURFACE]\n\n"
        f"<!-- GÉNÉRÉ par outillage/build_etat_narratif.py --chapitre "
        f"{args.chapitre} — ne pas éditer à la main : la table de pilotage est "
        "la source. -->\n\n"
        f"{narrative}\n"
    )

    if args.dry_run:
        print("## 7. État narratif courant\n\n" + narrative_block)
        return 0

    text = SHEET.read_text(encoding="utf-8")
    section = re.compile(r"^## 7\. État narratif courant.*?(?=^## |\Z)",
                         re.MULTILINE | re.DOTALL)
    if not section.search(text):
        print(f"ERREUR : section 7 introuvable dans {SHEET}", file=sys.stderr)
        return 1

    # On ne RECONSTRUIT pas la section : on remplace le seul bloc [SURFACE], ou
    # on l'insère s'il n'existe pas encore. Reconstruire dupliquait [GABARIT] et
    # [VALEURS] à chaque passe — et ces blocs sont la SOURCE dont ce script se
    # nourrit. Un générateur qui abîme sa propre source ne tourne qu'une fois.
    def substitute(m: re.Match) -> str:
        body = m.group(0)
        surface = re.compile(r"^### \[SURFACE\].*?(?=^### |\Z)",
                             re.MULTILINE | re.DOTALL)
        if surface.search(body):
            return surface.sub(lambda _: narrative_block + "\n", body, count=1)
        title, rest = body.split("\n", 1)
        return f"{title}\n\n{narrative_block}\n{rest.lstrip()}"

    SHEET.write_text(section.sub(substitute, text, count=1), encoding="utf-8")
    print(f"Section 7 régénérée pour le chapitre {args.chapitre} :\n\n{narrative}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
