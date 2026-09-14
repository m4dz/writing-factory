#!/usr/bin/env python3
"""Archive the failed runs: nothing is thrown away (ADR-0003, doctrine 13).

Every run carrying at least one AUTO failure is copied as is into
`experiments/journal/`, timestamped, with its grid line as a header. It is the
material of the talk: authentic failures demonstrate more than success, and
retouching them would void their value as evidence. The model's output is
NEVER modified.

Usage:
  factory eval journal experiments/runs/20260818-s4-stage-a 2
"""

import sys

from factory.paths import REPO_ROOT as RACINE

from factory.eval.grid import discover, frontmatter
from factory.eval.lint import (analyze, chapter_constraints,
                        chapter_checks, strip_frontmatter)

WALL = RACINE / "experiments" / "journal"


def auto_failures(text: str, constraints: dict | None) -> list[str]:
    """The failures the code can establish alone."""
    r = analyze(text)
    out: list[str] = []
    if r["l1_noms_propres"]:
        out.append(f"L1 noms propres ({len(r['l1_noms_propres'])})")
    if r["l2_fuite"]:
        out.append(f"L2 fuite lexicale ({len(r['l2_fuite'])})")
    count = [len(e) for e in r["l3_par_entree"]]
    if not all(c == 1 for c in count):
        out.append(f"L3 accumulation par entrée ({'/'.join(map(str, count))})")
    total = sum(c for c, _ in r["l4_par_entree"])
    outside = sum(len(h) for _, h in r["l4_par_entree"])
    if any(c > 1 for c, _ in r["l4_par_entree"]) or outside:
        out.append(f"L4 suspension ({total} occ., {outside} hors champ)")
    elif total == 0:
        out.append("L4/M1 aucun glissement")
    for key, lib in (("pastiche", "pastiche"), ("tics_ia", "tic d'IA"),
                     ("exclamation_hors_dialogue", "point d'exclamation"),
                     ("incise_adverbiale", "incise"), ("elision", "élision")):
        if r[key]:
            out.append(lib)
    if constraints:
        sc = chapter_checks(text, constraints)
        if sc["verdict"]:
            out.append("verdict du chapitre absent")
        if sc["reserves"]:
            out.append(f"termes réservés ({len(sc['reserves'])})")
        if sc["quatuor"]:
            out.append(f"quatuor réservé ch. 7 ({len(sc['quatuor'])})")
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 1:
        sys.exit("usage : factory eval journal <dossier-runs> [chapitre]")
    folder = argv[0]
    constraints = (chapter_constraints(int(argv[1]))
                   if len(argv) > 1 else None)
    WALL.mkdir(exist_ok=True)

    archives = 0
    for name, f in discover(folder):
        raw = f.read_text(encoding="utf-8")
        meta = frontmatter(f)
        faults = auto_failures(strip_frontmatter(raw), constraints)
        if not faults:
            print(f"  {name} — aucun échec AUTO, non archivé")
            continue
        stamp = meta.get("date", "?").replace(":", "").replace("-", "")
        dest = WALL / f"{stamp}-{folder}-{f.stem}.md"
        dest.write_text(
            "<!-- JOURNAL DES MURS — run raté, conservé tel quel, NON retouché. -->\n"
            f"# {name} — {folder}\n\n"
            f"- **Date** : {meta.get('date')}\n"
            f"- **Étage / rôle** : {meta.get('etage', '?')} · {meta.get('role', '?')}\n"
            f"- **RAG** : {meta.get('rag', '?')}\n"
            f"- **Mots** : {meta.get('mots')} · **durée** : {meta.get('duree_s', '?')} s\n"
            f"- **Temps par nœud** : {meta.get('temps_par_noeud', '—')}\n"
            f"- **Collections interrogées** : {meta.get('collections_interrogees', '—')}\n"
            f"- **Ligne de grille — échecs AUTO** : {', '.join(faults)}\n\n"
            "---\n\n" + raw,
            encoding="utf-8")
        archives += 1
        print(f"  {dest.name}\n      {', '.join(faults)}")
    print(f"\n{archives} run(s) archivé(s) depuis {folder}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
