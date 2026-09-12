"""The ``factory`` command line.

    factory doctor                      machine, backends, models, voice
    factory index                       bible → ChromaDB (idempotent)
    factory query "les deux couverts"   retrieval smoke test
    factory generate [--chapter 7]      one run per chapter under experiments/runs/
    factory generate --chapters 2,7     several chapters back to back
    factory runs                        the runs, newest first
    factory promote <run>               a generated chapter becomes canon (bible/scenes/)
    factory calibrate --stage S7        calibration stages (run files)
    factory eval lint|grid|seal|journal scoring
    factory serve                       the HTTP surface for the deck
    factory chat --character judith     actor mode in the terminal

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
                                description="Génère un ou plusieurs chapitres : préflight, "
                                            "état narratif, graphe, assemblage, voix. Un run "
                                            "par chapitre sous experiments/runs/.")
    what = p.add_mutually_exclusive_group()
    what.add_argument("--chapter", type=int, default=None,
                      help="Chapitre à générer (chapters/NN-slug/spec.yaml ; défaut 7)")
    what.add_argument("--chapters", default=None,
                      help="Plusieurs chapitres, l'un après l'autre : « 2,7 » ou « 1-11 »")
    what.add_argument("--brief", help="Chapitre ad hoc : objectif libre (plan généré)")
    p.add_argument("--characters", nargs="+", default=["judith"],
                   help="doc_ids des personnages présents (mode --brief)")
    p.add_argument("--seed", type=int, default=None,
                   help="Graine du tirage du glissement (défaut : aléatoire, consignée)")
    p.add_argument("--no-render", action="store_true",
                   help="Sans écriture de chapitre.md ni synthèse vocale")
    p.add_argument("--skip-preflight", action="store_true",
                   help="Préflight en avertissement seulement (dev, JAMAIS en scène)")
    p.add_argument("--no-preflight", action="store_true",
                   help="Aucune sonde machine (tests, machine non-macOS)")
    p.add_argument("--no-narrative-state", action="store_true",
                   help="Sans régénération ni indexation de l'état narratif (sans Chroma)")
    p.add_argument("--quiet", action="store_true",
                   help="Sans compte à rebours ni progression (mesure au plus juste)")
    p.add_argument("--budget", type=float, default=None,
                   help="Budget de scène en minutes pour le compte à rebours")
    p.add_argument("--runs-dir", default=None,
                   help="Racine des dossiers de run (défaut : experiments/runs)")
    return p


def parse_chapters(text: str) -> list[int]:
    """« 2,7 » → [2, 7] ; « 1-3,7 » → [1, 2, 3, 7]."""
    out: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    if not out:
        raise SystemExit(f"--chapters : aucun numéro dans « {text} »")
    return out


def _machine_requests(args) -> dict:
    return {
        "preflight": (None if args.no_preflight
                      else {"strict": not args.skip_preflight, "timer": True}),
        "render": not args.no_render,
        "narrative_state": not args.no_narrative_state,
    }


def _generate_state(args) -> dict:
    """State of a single --chapter/--brief invocation (the run fields are added
    by `generate`)."""
    if args.brief:
        state = {"brief": args.brief, "characters": args.characters}
        if args.seed is not None:
            state["seed"] = args.seed
    else:
        from factory.chapter_spec import ChapterSpecError, load_chapter
        try:
            spec = load_chapter(args.chapter if args.chapter is not None else 7)
        except ChapterSpecError as exc:
            raise SystemExit(str(exc))
        state = spec.state(seed=args.seed)
        if spec.workshop_terms:
            print(f"  ⚠ le brief du chapitre {spec.chapter} porte des termes d'atelier "
                  f"que le lint bannit en sortie : {list(spec.workshop_terms)} — "
                  "à arbitrer par l'auteur", file=sys.stderr)
    state.update(_machine_requests(args))
    return state


def _run_one(state: dict, chapter: int, slug: str, args, root) -> int:
    """One run: directory, graph, manifest, report. Returns the exit code."""
    import random
    from factory import runs as run_registry
    from factory.infra import progress
    from factory.infra.ollama import client
    from factory.infra.preflight import PreflightError
    from factory.pipeline.graph import build_graph
    from factory.retrieval import context as retrieval

    seed = state.get("seed")
    if seed is None:
        seed = state["seed"] = random.randrange(1, 10**6)
    run = run_registry.create_run(chapter, slug, seed=seed, root=root)
    state["artifacts_dir"] = str(run.dir)
    print(f"\n=== run {run.id} ===", file=sys.stderr)
    tracking = progress.Progress(active=not args.quiet, budget_min=args.budget)
    progress.install(tracking)
    run_registry.write_manifest(run, status="generating")
    client.recording = []
    retrieval.clear_routing()
    clocks = run_registry.Clocks()
    final, status, error, code = None, "error", None, 1
    t0 = time.time()
    try:
        final = build_graph().invoke(state, config={"recursion_limit": 50})
        status, code = "ready", 0
    except PreflightError as exc:
        error = f"préflight refusé : {exc}"
        print(f"\n{exc}\n\n  (--skip-preflight pour outrepasser)", file=sys.stderr)
    except progress.Cancelled:
        status, error = "cancelled", "annulé"
    finally:
        calls, client.recording = client.recording, None
        tracking.end()
        run_registry.record_result(run, final, clocks=clocks.read(), calls=calls,
                                   collections=retrieval.routing(), status=status, error=error)
    if final:
        _print_report(final, time.time() - t0)
        print(f"\n  run      : {run.dir}")
        if state.get("render"):
            print(f"  chapitre : {run.chapter_path}")
            print(f"  audio    : {run.audio_path if final.get('audio') else 'absent (voir notes)'}")
    return code


def generate(argv: list[str]) -> int:
    args = _generate_parser().parse_args(argv)
    from pathlib import Path

    root = Path(args.runs_dir) if args.runs_dir else None
    if args.chapters:
        from factory.chapter_spec import ChapterSpecError, load_chapter
        numbers = parse_chapters(args.chapters)
        specs = []
        for n in numbers:
            try:
                specs.append(load_chapter(n))
            except ChapterSpecError as exc:
                raise SystemExit(f"{exc}\n  (aucun run lancé : la série est refusée entière)")
        for spec in specs:
            state = {**spec.state(seed=args.seed), **_machine_requests(args)}
            code = _run_one(state, spec.chapter, spec.slug, args, root)
            if code:
                print(f"chapitre {spec.chapter} en échec : la série s'arrête", file=sys.stderr)
                return code
        return 0
    state = _generate_state(args)
    chapter = int(state.get("chapter") or 0)
    if args.brief:
        slug = "brief"
    else:
        from factory.chapter_spec import load_chapter
        slug = load_chapter(chapter).slug
    return _run_one(state, chapter, slug, args, root)


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
    """A generated chapter becomes canon — by the owner's hand, after reading.

    Copies the run's chapter into `bible/scenes/ch-NN-<run>.md` with a
    frontmatter (`type: scene`, `chapter`, `promoted_from`) and indexes it, so
    it enters semantic retrieval. Nothing from an unpromoted run reaches the
    next chapter.
    """
    p = argparse.ArgumentParser(prog="factory promote",
                                description="Promeut le chapitre d'un run dans bible/scenes/.")
    p.add_argument("run_id")
    p.add_argument("--force", action="store_true", help="Écrase une scène déjà promue de ce run")
    p.add_argument("--no-index", action="store_true", help="Copie sans indexer (pas de Chroma)")
    args = p.parse_args(argv)
    from datetime import date

    from factory import runs as run_registry

    run = run_registry.find_run(args.run_id)
    if run is None:
        print(f"run inconnu : {args.run_id}", file=sys.stderr)
        return 1
    if run.status != "ready" or not run.chapter_path.is_file():
        print(f"run {run.id} : état « {run.status} », pas de chapitre à promouvoir", file=sys.stderr)
        return 1
    target = settings.bible_dir / "scenes" / f"ch-{run.chapter:02d}-{run.id}.md"
    if target.exists() and not args.force:
        print(f"déjà promu : {target} (--force pour écraser)", file=sys.stderr)
        return 1
    body = run.chapter_path.read_text(encoding="utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "---\n"
        f"doc_id: scene-ch{run.chapter:02d}\n"
        "type: scene\n"
        f"chapter: {run.chapter}\n"
        f"promoted_from: {run.id}\n"
        f"date: {date.today().isoformat()}\n"
        "---\n\n"
        f"# Chapitre {run.chapter} — promu depuis {run.id}\n\n"
        f"{body.strip()}\n", encoding="utf-8")
    run_registry.write_manifest(run, promoted_to=str(target))
    print(f"promu : {target}")
    if not args.no_index:
        from factory.pipeline.nodes.narrative_state import index_state_file
        ids = index_state_file(target)
        print(f"indexé : {', '.join(ids) or 'aucun chunk'}")
    return 0


def _runs(argv: list[str]) -> int:
    argparse.ArgumentParser(prog="factory runs",
                            description="Liste les runs, du plus récent au plus ancien.").parse_args(argv)
    from factory import runs as run_registry

    for r in run_registry.list_runs():
        print(f"{r.id}  ch{r.chapter:02d}  seed={r.seed}  {r.status}")
    return 0


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
    "promote": promote, "runs": _runs,
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
