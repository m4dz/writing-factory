#!/usr/bin/env python3
"""Archive les runs ratés — « rien ne se jette ».

Chaque run portant au moins un échec AUTO est copié tel quel dans
`experiments/journal/`, horodaté, avec sa ligne de grille en en-tête. C'est le
matériau des sections 5-6 de la keynote : les échecs authentiques sont plus
démonstratifs que la réussite, et les retoucher leur ôterait leur valeur de
pièce à conviction. La sortie du modèle n'est JAMAIS modifiée.

Usage :
  python3 outillage/journal_des_murs.py experiments/runs/20260818-s4-stage-a 2
"""

import sys

from factory.paths import REPO_ROOT as RACINE

from factory.eval.grid import decouvrir, frontmatter
from factory.eval.lint import (analyse, contraintes_chapitre,
                        controles_chapitre, strip_frontmatter)

MUR = RACINE / "experiments" / "journal"


def echecs_auto(texte: str, contraintes: dict | None) -> list[str]:
    """Les manquements que le code sait établir seul."""
    r = analyse(texte)
    out: list[str] = []
    if r["l1_noms_propres"]:
        out.append(f"L1 noms propres ({len(r['l1_noms_propres'])})")
    if r["l2_fuite"]:
        out.append(f"L2 fuite lexicale ({len(r['l2_fuite'])})")
    compte = [len(e) for e in r["l3_par_entree"]]
    if not all(c == 1 for c in compte):
        out.append(f"L3 accumulation par entrée ({'/'.join(map(str, compte))})")
    total = sum(c for c, _ in r["l4_par_entree"])
    hors = sum(len(h) for _, h in r["l4_par_entree"])
    if any(c > 1 for c, _ in r["l4_par_entree"]) or hors:
        out.append(f"L4 suspension ({total} occ., {hors} hors champ)")
    elif total == 0:
        out.append("L4/M1 aucun glissement")
    for cle, lib in (("pastiche", "pastiche"), ("tics_ia", "tic d'IA"),
                     ("exclamation_hors_dialogue", "point d'exclamation"),
                     ("incise_adverbiale", "incise"), ("elision", "élision")):
        if r[cle]:
            out.append(lib)
    if contraintes:
        sc = controles_chapitre(texte, contraintes)
        if sc["verdict"]:
            out.append("verdict du chapitre absent")
        if sc["reserves"]:
            out.append(f"termes réservés ({len(sc['reserves'])})")
        if sc["quatuor"]:
            out.append(f"quatuor réservé ch. 7 ({len(sc['quatuor'])})")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage : journal_des_murs.py <dossier-runs> [chapitre]")
    dossier = sys.argv[1]
    contraintes = (contraintes_chapitre(int(sys.argv[2]))
                   if len(sys.argv) > 2 else None)
    MUR.mkdir(exist_ok=True)

    archives = 0
    for nom, f in decouvrir(dossier):
        brut = f.read_text(encoding="utf-8")
        meta = frontmatter(f)
        fautes = echecs_auto(strip_frontmatter(brut), contraintes)
        if not fautes:
            print(f"  {nom} — aucun échec AUTO, non archivé")
            continue
        horo = meta.get("date", "?").replace(":", "").replace("-", "")
        dest = MUR / f"{horo}-{dossier}-{f.stem}.md"
        dest.write_text(
            "<!-- JOURNAL DES MURS — run raté, conservé tel quel, NON retouché. -->\n"
            f"# {nom} — {dossier}\n\n"
            f"- **Date** : {meta.get('date')}\n"
            f"- **Étage / rôle** : {meta.get('etage', '?')} · {meta.get('role', '?')}\n"
            f"- **RAG** : {meta.get('rag', '?')}\n"
            f"- **Mots** : {meta.get('mots')} · **durée** : {meta.get('duree_s', '?')} s\n"
            f"- **Temps par nœud** : {meta.get('temps_par_noeud', '—')}\n"
            f"- **Collections interrogées** : {meta.get('collections_interrogees', '—')}\n"
            f"- **Ligne de grille — échecs AUTO** : {', '.join(fautes)}\n\n"
            "---\n\n" + brut,
            encoding="utf-8")
        archives += 1
        print(f"  {dest.name}\n      {', '.join(fautes)}")
    print(f"\n{archives} run(s) archivé(s) depuis {dossier}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
