#!/usr/bin/env python3
"""Lance la génération d'un chapitre (mode auteur) et profile le temps.

    python run_chapter.py --brief "..." --characters elara-vance kael-doran

Le profilage total est LA mesure qui compte : le chapitre doit tenir dans les
~35 minutes de scène de la keynote. Chaque appel LLM est chronométré.
"""

import argparse
import time

from graph import build_graph


def main() -> None:
    p = argparse.ArgumentParser(description="Génère un chapitre (mode auteur).")
    p.add_argument("--brief", required=True, help="Objectif du chapitre")
    p.add_argument(
        "--characters", nargs="+", required=True,
        help="doc_ids des personnages présents (ex: elara-vance kael-doran)",
    )
    args = p.parse_args()

    graph = build_graph()
    t0 = time.time()
    final = graph.invoke(
        {"brief": args.brief, "characters": args.characters},
        config={"recursion_limit": 50},  # la boucle d'écriture peut itérer
    )
    total = time.time() - t0

    print("\n" + "#" * 78)
    print("PLAN DE SCÈNES")
    print("#" * 78)
    for i, beat in enumerate(final["plan"], 1):
        print(f"  {i}. {beat}")

    print("\n" + "#" * 78)
    print("CHAPITRE (après relecture + réparation linguistique)")
    print("#" * 78)
    for i, scene in enumerate(final["repaired"], 1):
        print(f"\n--- Scène {i} ---\n{scene}")

    print("\n" + "#" * 78)
    print("RAPPORT DE COHÉRENCE")
    print("#" * 78)
    print(final["coherence"])

    print("\n" + "#" * 78)
    print("LINT DE STYLE (fuites de langue, tokens corrompus)")
    print("#" * 78)
    warns = final.get("warnings", [])
    if warns:
        for w in warns:
            print(f"  ⚠ {w}")
    else:
        print("  aucune alerte")

    print("\n" + "#" * 78)
    print("PROFILAGE (contrainte des 35 min)")
    print("#" * 78)
    gen = sum(m["gen_toks"] for m in final["metrics"])
    print(f"  appels LLM       : {len(final['metrics'])}")
    print(f"  tokens générés   : {gen}")
    print(f"  vitesse moyenne  : "
          f"{sum(m['gen_tok_s'] for m in final['metrics']) / len(final['metrics']):.1f} tok/s")
    print(f"  TEMPS TOTAL      : {total:.0f} s  ({total / 60:.1f} min)")
    print("\n  détail par appel (done_reason « length » = tronqué) :")
    for i, m in enumerate(final["metrics"]):
        flag = "  <-- TRONQUÉ" if m.get("done_reason") == "length" else ""
        print(f"    #{i}  {m['gen_toks']:>4}/{m.get('num_predict', '?')} tok  "
              f"{m['gen_tok_s']:>5} tok/s  [{m.get('done_reason')}]{flag}")


if __name__ == "__main__":
    main()
