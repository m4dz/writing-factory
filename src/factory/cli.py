"""The ``factory`` command line.

    factory doctor                      machine, backends, models, voice
    factory index                       bible → ChromaDB (idempotent)
    factory query "les deux couverts"   retrieval smoke test
    factory generate [--chapter 7]      one chapter, artifacts in output/
    factory calibrate --stage S7        calibration stages (run files)
    factory eval lint|grid|seal|journal scoring
    factory serve                       the HTTP surface for the deck
    factory chat --character judith     actor mode in the terminal
    factory promote <run>               (step 6) a chapter becomes canon

Every subcommand is a thin dispatch onto a module ``main(argv)``; the graph
and the machine nodes do the work. Imports of the pipeline are lazy so the
indexer container, which carries no LangGraph, still runs ``factory index``.
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.request

from factory.settings import settings

USAGE = __doc__.split("\n\n")[1]


# --- generate ----------------------------------------------------------------

def _generate_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="factory generate",
                                description="Génère un chapitre : préflight, graphe, "
                                            "assemblage, voix.")
    what = p.add_mutually_exclusive_group()
    what.add_argument("--chapter", type=int, default=7,
                      help="Chapitre à générer (7 : la structure de scène)")
    what.add_argument("--brief", help="Chapitre ad hoc : objectif libre (plan généré)")
    p.add_argument("--characters", nargs="+", default=["judith"],
                   help="doc_ids des personnages présents (mode --brief)")
    p.add_argument("--seed", type=int, default=None,
                   help="Graine du tirage du glissement (défaut : aléatoire)")
    p.add_argument("--no-render", action="store_true",
                   help="Sans écriture de chapitre.md ni synthèse vocale")
    p.add_argument("--skip-preflight", action="store_true",
                   help="Préflight en avertissement seulement (dev, JAMAIS en scène)")
    p.add_argument("--no-preflight", action="store_true",
                   help="Aucune sonde machine (tests, machine non-macOS)")
    p.add_argument("--quiet", action="store_true",
                   help="Sans compte à rebours ni progression (mesure au plus juste)")
    p.add_argument("--budget", type=float, default=None,
                   help="Budget de scène en minutes pour le compte à rebours")
    p.add_argument("--out", default=None, help="Dossier des artefacts (défaut : output/)")
    return p


def _generate_state(args) -> dict:
    if args.brief:
        state = {"brief": args.brief, "characters": args.characters}
        if args.seed is not None:
            state["seed"] = args.seed
    elif args.chapter == 7:
        from factory.chapter_spec import chapter7 as ch7
        state = ch7.ch7_state(seed=args.seed)
    else:
        raise SystemExit(f"chapitre {args.chapter} : aucune spécification "
                         "(étape 5 du plan : chapters/NN-slug/spec.yaml)")
    state["preflight"] = (None if args.no_preflight
                          else {"strict": not args.skip_preflight, "timer": True})
    state["render"] = not args.no_render
    return state


def generate(argv: list[str]) -> int:
    args = _generate_parser().parse_args(argv)
    from pathlib import Path

    from factory.infra import progress
    from factory.infra.preflight import PreflightError
    from factory.pipeline.graph import build_graph

    if args.out:
        settings.output_dir = Path(args.out)
    tracking = progress.Progress(active=not args.quiet, budget_min=args.budget)
    progress.install(tracking)
    graph = build_graph()
    t0 = time.time()
    try:
        final = graph.invoke(_generate_state(args), config={"recursion_limit": 50})
    except PreflightError as exc:
        print(f"\n{exc}\n\n  (--skip-preflight pour outrepasser)", file=sys.stderr)
        return 1
    finally:
        tracking.end()
    total = time.time() - t0
    _print_report(final, total)
    if final.get("render"):
        from factory.pipeline.nodes.render import audio_path, chapter_path
        print(f"\n  chapitre : {chapter_path()}")
        print(f"  audio    : {audio_path() if final.get('audio') else 'absent (voir notes)'}")
    return 0


def _print_report(final: dict, total: float) -> None:
    """The profiling report of the former ``run_chapter`` driver."""
    bar = "#" * 78
    if final.get("plan"):
        print(f"\n{bar}\nPLAN DE SCÈNES\n{bar}")
        for i, beat in enumerate(final["plan"], 1):
            print(f"  {i}. {beat}")
    if final.get("facts"):
        print("\n  invariants de la bible imposés au plan :")
        for f in final["facts"]:
            print(f"    - {f}")
    if final.get("plan_report"):
        print("\n  contrôle du plan AVANT rédaction :\n"
              + "\n".join(f"  {l}" for l in final["plan_report"].splitlines()))

    print(f"\n{bar}\nCHAPITRE (après relecture + réparation linguistique)\n{bar}")
    print(final.get("chapter_md") or "\n\n".join(final.get("repaired") or []))

    print(f"\n{bar}\nRAPPORT DE COHÉRENCE\n{bar}")
    print(final.get("coherence") or "(aucun)")

    print(f"\n{bar}\nLINT DE STYLE (fuites de langue, tokens corrompus)\n{bar}")
    # Distinguer ce qui SUBSISTE de ce qui a été rattrapé : les alertes émises
    # par l'écriture et la relecture décrivent un état ANTÉRIEUR à la
    # réparation par Qwen. Les afficher pêle-mêle fait passer un défaut corrigé
    # pour un défaut vivant.
    warns = final.get("warnings") or []
    residual = [w for w in warns if _residual(w)]
    upstream = [w for w in warns if not _residual(w)]
    if residual:
        print("  SUBSISTE dans le texte final :")
        for w in residual:
            print(f"    ⚠ {w}")
    else:
        print("  texte final : aucune alerte")
    if upstream:
        print("\n  détecté puis corrigé en amont (état avant réparation) :")
        for w in upstream:
            print(f"    · {w}")

    metrics = final.get("metrics") or []
    print(f"\n{bar}\nPROFILAGE (contrainte des 25 min)\n{bar}")
    gen = sum(m.get("gen_toks", 0) for m in metrics)
    print(f"  appels LLM       : {len(metrics)}")
    print(f"  tokens générés   : {gen}")
    if metrics:
        print(f"  vitesse moyenne  : "
              f"{sum(m.get('gen_tok_s', 0) for m in metrics) / len(metrics):.1f} tok/s")
    print(f"  TEMPS TOTAL      : {total:.0f} s  ({total / 60:.1f} min)")
    # `ctx_fill` est plafonné à 1 par construction : il ne peut PAS servir
    # d'alarme. Les deux signaux utiles sont l'estimation avant envoi
    # (`ctx_need`) et l'écart envoyé/lu (`ctx_truncated`).
    truncated = [i for i, m in enumerate(metrics) if m.get("ctx_truncated")]
    tight = [i for i, m in enumerate(metrics) if m.get("ctx_need", 0) > 0.9]
    if truncated:
        print(f"\n  ⚠ PROMPT AMPUTÉ sur les appels {truncated} : Ollama dit avoir "
              "lu bien moins que ce qui a été envoyé. Le début du prompt "
              "système (garde française, faits de la bible) est parti. "
              "Augmenter NUM_CTX.")
    if tight:
        print(f"\n  ⚠ Fenêtre serrée (> 90 %) sur les appels {tight} : "
              "prompt estimé + num_predict frôle NUM_CTX.")
    if metrics:
        print("\n  détail par appel (« length » = génération coupée — une "
              "continuation a été relancée, cf. lint ; need > 1.00 = fenêtre "
              "insuffisante) :")
    for i, m in enumerate(metrics):
        flag = "  <-- COUPÉ (continuation)" if m.get("done_reason") == "length" else ""
        if m.get("ctx_truncated"):
            flag += "  <-- PROMPT AMPUTÉ"
        print(f"    #{i}  {m.get('gen_toks', 0):>4}/{m.get('num_predict', '?')} tok  "
              f"{m.get('gen_tok_s', 0):>5} tok/s  "
              f"ctx {m.get('ctx_fill', 0):.2f} / need {m.get('ctx_need', 0):.2f}  "
              f"[{m.get('done_reason')}]{flag}")


def _residual(w: str) -> bool:
    # « réparation … » = relevé APRÈS la passe Qwen, donc encore présent.
    # « à reprendre à la main » = la continuation et la coupe propre ont
    # toutes deux échoué : c'est le seul cas où du texte sort amputé.
    return w.startswith("réparation ") or "à reprendre à la main" in w


# --- doctor ------------------------------------------------------------------

def _http_ok(url: str, timeout: float = 5.0) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return True, resp.read().decode("utf-8", "replace")
    except Exception as exc:                            # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def doctor(argv: list[str]) -> int:
    """Run the real probes on this machine and print what they say.

    Not a test: the probes and the synthesizer are faked in the suite. This
    is the runbook's first step, on the owner's machine.
    """
    argparse.ArgumentParser(prog="factory doctor",
                            description="État machine, backends, modèles, voix.").parse_args(argv)
    from factory.infra.preflight import PreflightError, preflight, report

    problems = 0

    def line(ok: bool | None, text: str) -> None:
        nonlocal problems
        mark = "✓" if ok else ("⚠" if ok is None else "✗")
        if ok is False:
            problems += 1
        print(f"  {mark} {text}")

    print("machine")
    try:
        line(True, report())
    except Exception as exc:                            # noqa: BLE001
        line(None, f"sondes macOS indisponibles ({type(exc).__name__}: {exc})")
    try:
        warnings = preflight(strict=True, timer=True)
        line(True, "préflight : accepté" + (f", {len(warnings)} avertissement(s)" if warnings else ""))
        for w in warnings:
            line(None, w)
    except PreflightError as exc:
        reasons = [l.strip(" -") for l in str(exc).splitlines()[1:] if l.strip()]
        line(False, "préflight refusé" + (f" : {reasons[0]}" if reasons else ""))
        for r in reasons[1:]:
            line(False, r)
    except Exception as exc:                            # noqa: BLE001
        line(None, f"préflight impossible ({type(exc).__name__}: {exc})")

    print("backends")
    ok, body = _http_ok(f"{settings.ollama_url}/api/tags")
    line(ok, f"Ollama {settings.ollama_url}" + ("" if ok else f" — {body}"))
    if ok:
        import json
        names = {m.get("name", "") for m in json.loads(body).get("models", [])}
        for role, model in (("auteur", settings.author_model), ("QA", settings.qa_model),
                            ("embeddings", settings.embed_model)):
            present = any(n == model or n.split(":")[0] == model for n in names)
            line(present, f"modèle {role} : {model}" + ("" if present else " — `ollama pull`"))
    ok, body = _http_ok(f"http://{settings.chroma_host}:{settings.chroma_port}/api/v2/heartbeat")
    line(ok, f"ChromaDB {settings.chroma_host}:{settings.chroma_port}"
         + ("" if ok else f" — {body} (podman-compose up -d chromadb)"))

    print("voix")
    voice = settings.voice_dir
    has_ref = (voice / "ma-voix.wav").is_file() and (voice / "ma-voix.txt").is_file()
    line(has_ref, f"référence vocale dans {voice}")
    try:
        import mlx_audio  # noqa: F401
        import soundfile  # noqa: F401
        line(True, "dépendances TTS (mlx-audio, soundfile)")
    except ImportError as exc:
        line(None, f"dépendances TTS absentes ({exc}) — pip install -e '.[tts]' sur la machine de scène")

    print("bible")
    line(settings.bible_dir.is_dir(), f"bible : {settings.bible_dir}")
    line(settings.style_path.is_file(), f"fiche de style : {settings.style_path}")
    print(f"\n{problems} problème(s) bloquant(s)." if problems else "\ntout est vert.")
    return 1 if problems else 0


# --- promote -----------------------------------------------------------------

def promote(argv: list[str]) -> int:
    print("factory promote : pas avant l'étape 6 du plan (docs/plans/2026-09-revamp.md §6) — "
          "un chapitre généré est un candidat, l'auteur le promeut après lecture.",
          file=sys.stderr)
    return 2


# --- dispatch ----------------------------------------------------------------

def _index(argv: list[str]) -> int:
    argparse.ArgumentParser(prog="factory index",
                            description="Indexe la bible dans ChromaDB.").parse_args(argv)
    from factory.retrieval.indexer import main
    return main()


def _query(argv: list[str]) -> int:
    from factory.retrieval.query import main
    main(argv)
    return 0


def _calibrate(argv: list[str]) -> int:
    from factory.tooling.stage_runner import main
    return main(argv)


def _serve(argv: list[str]) -> int:
    argparse.ArgumentParser(prog="factory serve",
                            description="Sert l'API du deck et le mode acteur.").parse_args(argv)
    from factory.api.server import main
    main()
    return 0


def _chat(argv: list[str]) -> int:
    from factory.roleplay.cli import main
    main(argv)
    return 0


def _eval(argv: list[str]) -> int:
    tools = {"lint": "factory.eval.lint", "grid": "factory.eval.grid",
             "seal": "factory.eval.seal", "journal": "factory.eval.journal"}
    if not argv or argv[0] not in tools:
        print("usage : factory eval {lint|grid|seal|journal} [...]", file=sys.stderr)
        return 2
    import importlib
    return int(importlib.import_module(tools[argv[0]]).main(argv[1:]) or 0)


COMMANDS = {
    "doctor": doctor, "index": _index, "query": _query, "generate": generate,
    "calibrate": _calibrate, "eval": _eval, "serve": _serve, "chat": _chat,
    "promote": promote,
}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(f"usage : factory <commande> [options]\n\n{USAGE}")
        return 0 if argv else 2
    command, rest = argv[0], argv[1:]
    if command not in COMMANDS:
        print(f"factory : commande inconnue « {command} »\n\n{USAGE}", file=sys.stderr)
        return 2
    return int(COMMANDS[command](rest) or 0)


if __name__ == "__main__":
    sys.exit(main())
