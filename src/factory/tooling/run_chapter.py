#!/usr/bin/env python3
"""Lance la génération d'un chapitre (mode auteur) et profile le temps.

    python run_chapter.py --brief "..." --characters judith

    (Le chapitre 7 de scène se génère par l'API — `POST /generate`, cf.
    orchestrator/ch7.py — ou par `outillage/run_s4.py --etage CH7`. Ce CLI-ci
    reste un pilote générique pour un chapitre ad hoc.)

Le profilage total est LA mesure qui compte : le chapitre doit tenir dans les
~35 minutes de scène de la keynote. Chaque appel LLM est chronométré.
"""

import argparse
import time

from factory.infra import progress
from factory.pipeline.graph import build_graph
from factory.infra.preflight import PreflightError, preflight, report
from factory.settings import settings


def main() -> None:
    p = argparse.ArgumentParser(description="Génère un chapitre (mode auteur).")
    p.add_argument("--brief", required=True, help="Objectif du chapitre")
    p.add_argument(
        "--characters", nargs="+", required=True,
        help="doc_ids des personnages présents (ex: judith)",
    )
    p.add_argument(
        "--skip-preflight", action="store_true",
        help="Passer outre le contrôle machine (dev only, JAMAIS en scène)",
    )
    p.add_argument(
        "--muet", action="store_true",
        help="Sans compte à rebours ni progression (mesure au plus juste)",
    )
    p.add_argument(
        "--budget", type=float, default=settings.stage_budget_min,
        help="Budget de scène en minutes pour le compte à rebours (défaut 25)",
    )
    args = p.parse_args()

    # Un chapitre tourne ~20 min sans surveillance : mieux vaut refuser de
    # démarrer que planter la machine à la douzième minute de keynote.
    print(f"PRÉFLIGHT : {report()}")
    try:
        # `chrono=True` : générer un chapitre EST une mesure de temps — c'est
        # même la contrainte dure du projet. Un swap saturé ne casserait pas la
        # machine, mais rendrait la durée obtenue ininterprétable, et c'est
        # précisément ce chiffre qu'on vient chercher ici.
        for w in preflight(strict=not args.skip_preflight, chrono=True):
            print(f"  ⚠ {w}")
    except PreflightError as exc:
        raise SystemExit(f"\n{exc}\n\n  (--skip-preflight pour outrepasser)")

    # Le compte à rebours est actif par DÉFAUT : c'est le mode de scène, et un
    # écran figé pendant dix-sept minutes se lit comme une panne. `--muet` sert
    # à mesurer sans le coût du streaming (quelques écritures par seconde).
    suivi = progress.Progress(actif=not args.muet, budget_min=args.budget)
    progress.install(suivi)

    graph = build_graph()
    t0 = time.time()
    try:
        final = graph.invoke(
            {"brief": args.brief, "characters": args.characters},
            config={"recursion_limit": 50},  # la boucle d'écriture peut itérer
        )
    finally:
        suivi.fin()
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
    def _residuel(w: str) -> bool:
        # « réparation … » = relevé APRÈS la passe Qwen, donc encore présent.
        # « à reprendre à la main » = la continuation et la coupe propre ont
        # toutes deux échoué : c'est le seul cas où du texte sort amputé.
        return w.startswith("réparation ") or "à reprendre à la main" in w
    residuel = [w for w in warns if _residuel(w)]
    amont = [w for w in warns if not _residuel(w)]
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

    print("\n  détail par appel (« length » = génération coupée — une "
          "continuation a été relancée, cf. lint ; need > 1.00 = fenêtre "
          "insuffisante) :")
    for i, m in enumerate(final["metrics"]):
        flag = "  <-- COUPÉ (continuation)" if m.get("done_reason") == "length" else ""
        if m.get("ctx_truncated"):
            flag += "  <-- PROMPT AMPUTÉ"
        print(f"    #{i}  {m['gen_toks']:>4}/{m.get('num_predict', '?')} tok  "
              f"{m['gen_tok_s']:>5} tok/s  "
              f"ctx {m.get('ctx_fill', 0):.2f} / need {m.get('ctx_need', 0):.2f}  "
              f"[{m.get('done_reason')}]{flag}")


if __name__ == "__main__":
    main()
