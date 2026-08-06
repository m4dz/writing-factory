#!/usr/bin/env python3
"""Lance la génération d'un chapitre (mode auteur) et profile le temps.

    python run_chapter.py --brief "..." --characters elara-vance kael-doran

Le profilage total est LA mesure qui compte : le chapitre doit tenir dans les
~35 minutes de scène de la keynote. Chaque appel LLM est chronométré.
"""

import argparse
import time

from graph import build_graph
from preflight import PreflightError, preflight, report


def main() -> None:
    p = argparse.ArgumentParser(description="Génère un chapitre (mode auteur).")
    p.add_argument("--brief", required=True, help="Objectif du chapitre")
    p.add_argument(
        "--characters", nargs="+", required=True,
        help="doc_ids des personnages présents (ex: elara-vance kael-doran)",
    )
    p.add_argument(
        "--skip-preflight", action="store_true",
        help="Passer outre le contrôle machine (dev only, JAMAIS en scène)",
    )
    args = p.parse_args()

    # Un chapitre tourne ~20 min sans surveillance : mieux vaut refuser de
    # démarrer que planter la machine à la douzième minute de keynote.
    print(f"PRÉFLIGHT : {report()}")
    try:
        for w in preflight(strict=not args.skip_preflight):
            print(f"  ⚠ {w}")
    except PreflightError as exc:
        raise SystemExit(f"\n{exc}\n\n  (--skip-preflight pour outrepasser)")

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

    print("\n  invariants de la bible imposés au plan :")
    for f in final.get("facts", []):
        print(f"    - {f}")
    print(f"\n  contrôle du plan AVANT rédaction :\n"
          + "\n".join(f"  {l}" for l in final.get("plan_report", "").splitlines()))

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
    # Distinguer ce qui SUBSISTE de ce qui a été rattrapé : les alertes émises
    # par l'écriture et la relecture décrivent un état ANTÉRIEUR à la
    # réparation par Qwen. Les afficher pêle-mêle fait passer un défaut corrigé
    # pour un défaut vivant — sur scène, c'est un faux aveu de panne.
    warns = final.get("warnings", [])
    residuel = [w for w in warns if w.startswith("réparation ")]
    amont = [w for w in warns if not w.startswith("réparation ")]
    if residuel:
        print("  SUBSISTE dans le texte final :")
        for w in residuel:
            print(f"    ⚠ {w}")
    else:
        print("  texte final : aucune alerte")
    if amont:
        print("\n  détecté puis corrigé en amont (état avant réparation) :")
        for w in amont:
            print(f"    · {w}")

    print("\n" + "#" * 78)
    print("PROFILAGE (contrainte des 25 min)")
    print("#" * 78)
    gen = sum(m["gen_toks"] for m in final["metrics"])
    print(f"  appels LLM       : {len(final['metrics'])}")
    print(f"  tokens générés   : {gen}")
    print(f"  vitesse moyenne  : "
          f"{sum(m['gen_tok_s'] for m in final['metrics']) / len(final['metrics']):.1f} tok/s")
    print(f"  TEMPS TOTAL      : {total:.0f} s  ({total / 60:.1f} min)")
    # `ctx_fill` est plafonné à 1 par construction (Ollama ne rapporte que les
    # tokens qu'il a réellement évalués, après troncature) : il ne peut PAS
    # servir d'alarme. Les deux signaux utiles sont l'estimation avant envoi
    # (`ctx_need`) et l'écart envoyé/lu (`ctx_truncated`).
    ampute = [i for i, m in enumerate(final["metrics"]) if m.get("ctx_truncated")]
    serre = [i for i, m in enumerate(final["metrics"]) if m.get("ctx_need", 0) > 0.9]
    if ampute:
        print(f"\n  ⚠ PROMPT AMPUTÉ sur les appels {ampute} : Ollama dit avoir "
              "lu bien moins que ce qui a été envoyé. Le début du prompt "
              "système (garde française, faits de la bible) est parti. "
              "Augmenter NUM_CTX.")
    if serre:
        print(f"\n  ⚠ Fenêtre serrée (> 90 %) sur les appels {serre} : "
              "prompt estimé + num_predict frôle NUM_CTX.")

    print("\n  détail par appel (« length » = génération coupée, "
          "need > 1.00 = fenêtre insuffisante) :")
    for i, m in enumerate(final["metrics"]):
        flag = "  <-- TRONQUÉ" if m.get("done_reason") == "length" else ""
        if m.get("ctx_truncated"):
            flag += "  <-- PROMPT AMPUTÉ"
        print(f"    #{i}  {m['gen_toks']:>4}/{m.get('num_predict', '?')} tok  "
              f"{m['gen_tok_s']:>5} tok/s  "
              f"ctx {m.get('ctx_fill', 0):.2f} / need {m.get('ctx_need', 0):.2f}  "
              f"[{m.get('done_reason')}]{flag}")


if __name__ == "__main__":
    main()
