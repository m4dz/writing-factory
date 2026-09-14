#!/usr/bin/env python3
"""Calibration stages, one run file per draw (`factory calibrate --stage`).

Runs the full graph (`plan → write → review → repair → coherence`) for the
archived stages A, B, Bp, C, S6, S7 and the chapter 7 rehearsal CH7. A and B
differ by `rag` alone (A: no Chroma, no embedding call; B: indexed collections).
Briefs come from the chapter 2 spec (`chapters/02-*/spec.yaml`), except the
historical v2/v3/C constants kept below so the archived stages stay replayable.
Run files land under `experiments/runs/<date>-<stage>/` (ADR-0003).

Superseded by `factory generate`, which writes runs with a manifest; this driver
stays for the calibration series and their grids.

Usage:
  factory calibrate --stage A                 # A1-A3 + AC
  factory calibrate --stage A --only A1
  factory calibrate --stage B
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from factory.paths import REPO_ROOT as RACINE

from factory.eval.lint import analyze
from factory.retrieval import context as retrieval
from factory.text import ends_mid_sentence
from factory.infra.preflight import PreflightError
# Chapter knowledge (7 and 2) comes from chapters/NN-slug/spec.yaml through the
# loader — the single source shared with the API's live path and the CLI.
from factory.chapter_spec import load_chapter

# Chapter 2 brief v2, verbatim from the session protocol §3
# (experiments/reports/protocole-calibration-ch2.md). Served to the SCORED runs
# of stages A and B.
BRIEF_V2 = (
    "Chapitre 2, entrée unique du carnet, 450-600 mots. En-tête imposé, "
    "première ligne exacte : « Mardi 12. Ciel couvert. »\n"
    "Squelette, dans l'ordre : en-tête → citation → constat → reconstruction "
    "→ verdict → notation physiologique → couperet.\n"
    "Citation ancre, recopiée verbatim entre guillemets après l'en-tête : "
    "« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table "
    "jusqu'au matin. »\n"
    "Beats : 1. le rituel posé en une ou deux phrases — elle relit l'entrée "
    "de la veille du cahier, comme chaque soir. 2. La citation, puis le "
    "constat d'écart : sa mémoire dit une assiette, un dîner seule. 3. La "
    "vérification, perceptive : la cuisine, l'égouttoir — regarder, compter ; "
    "la vérification confirme l'entrée, pas sa mémoire. 4. La rationalisation "
    "argumentée : la fatigue, l'automatisme — et la spirale de reprise des "
    "faits dans l'ordre. 5. Verdict : erreur de relevé — la faute est à elle, "
    "pas au texte ; résolution de pointer plus précisément ; physiologie ; "
    "couperet.\n"
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.\n"
    "Interdits : aucun nom propre, aucun dialogue, aucune explication, "
    "« journal » et « journal intime » bannis, aucun terme réservé "
    "(la tierce, l'errata, le bon à tirer)."
)

# Chapter goal for AC/BC, outside the score. Supplied by the owner to settle the
# contradiction between brief v2 (a single entry) and protocol §4 (the whole
# chapter 2, three entries).
CHAPTER_GOAL = (
    "Chapitre 2 complet, trois entrées du carnet à dates consécutives, "
    "450-600 mots chacune. Matière du chapitre : la première divergence — "
    "l'entrée relue du cahier mentionne une seconde assiette (ancre, à "
    "recopier verbatim dans l'entrée concernée : « Deux assiettes mises, sans "
    "y penser. Je l'ai laissée sur la table jusqu'au matin. »), vérification "
    "perceptive à la cuisine, rationalisation par la fatigue, verdict : "
    "erreur de relevé, résolution de pointer plus précisément. Interdits du "
    "brief v2 inchangés."
)


# --- Brief v3 (session 5, item 6) -------------------------------------------
#
# Delta from v2: the RESULT of the verification becomes an imposed, counted fact
# in the material. M4 (the reread entry is right against memory) broke two runs
# out of three at stage B despite an explicit beat 3: the model settled the
# conflict through every channel but the novel's (the object vanished, or the
# body contradicted the text). The state of the world is given, not debated.
# Quotation anchor only: the header is composed by the code (`graph.header`,
# ADR-0018), no longer copied from a constant. Served to full chapters too: the
# missing anchor is what produced the inner manuscript of B′C.
# (The anchor quotation is now `prefix` in chapters/02-*/spec.yaml.)

BRIEF_V3 = BRIEF_V2.replace(
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.",
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.\n"
    "FAIT IMPOSÉ, au matériau : « L'égouttoir, ce soir : deux assiettes. » "
    "La vérification CONSTATE ce fait, elle ne le découvre pas.\n"
    "En-tête : jamais de mois, jamais d'année."
)

# The chapter goal inherits the same imposed fact.
CHAPTER_GOAL_V3 = CHAPTER_GOAL + (
    " Fait imposé, au matériau : « L'égouttoir, ce soir : deux assiettes. » "
    "En-tête : jamais de mois, jamais d'année."
)

# STAGE C BRIEF. It no longer asks for the header or the anchor copy: the code
# POSES them (block B, item 5; ADR-0018). Leaving them in the brief gave the
# first C run two headers and two anchors, the model's and the code's. An
# instruction and a concatenation doing the same thing add up.

BRIEF_C = (BRIEF_V3
           .replace("En-tête imposé, "
                    "première ligne exacte : « Mardi 12. Ciel couvert. »", "")
           .replace("Citation ancre, recopiée verbatim entre guillemets après "
                    "l'en-tête : « Deux assiettes mises, sans y penser. Je "
                    "l'ai laissée sur la table jusqu'au matin. »\n", "")
           .replace("Squelette, dans l'ordre : en-tête → citation → constat",
                    "L'en-tête et la citation sont DÉJÀ ÉCRITS. Squelette de "
                    "ce qui reste, dans l'ordre : constat"))

# BRIEF V4 (session 6) and the chapter goal v4 live in chapters/02-*/spec.yaml
# (`entry_brief`, `brief`); the loader asserts them free of workshop terms.

# Calendar, verdict, objects and anchor of chapter 2 are read from its spec.

PLAN_RUNS = {
    "A": [("A1", BRIEF_V2, "score"), ("A2", BRIEF_V2, "score"),
          ("A3", BRIEF_V2, "score"),
          ("AC", CHAPTER_GOAL, "chapitre complet, hors score")],
    "B": [("B1", BRIEF_V2, "score"), ("B2", BRIEF_V2, "score"),
          ("B3", BRIEF_V2, "score"),
          ("BC", CHAPTER_GOAL, "chapitre complet, hors score")],
    # B′: the repaired service. Brief v3, retrieval active; the corrective batch
    # is the only variable against B.
    "Bp": [("Bp1", BRIEF_V3, "score"), ("Bp2", BRIEF_V3, "score"),
           ("Bp3", BRIEF_V3, "score"),
           ("BpC", CHAPTER_GOAL_V3, "chapitre complet, hors score")],
    # C: B′ with the assembly micro-nodes added. L3 and M1 become blocking.
    "C": [("C1", BRIEF_C, "score"), ("C2", BRIEF_C, "score"),
          ("C3", BRIEF_C, "score"),
          ("CC", CHAPTER_GOAL_V3, "chapitre complet, hors score")],
    # S6: `write` split into three segments, brief v4, drift drawn from the bank.
    # The measured variable is the SPLIT; the rest of the batch fixes defects
    # born at stage C and adds no device.
    "S6": [("S6-1", "entry", "score"), ("S6-2", "entry", "score"),
           ("S6-3", "entry", "score"),
           ("S6-C", "chapter", "chapitre complet, hors score")],
    # S7: the corrective batch. Brief v4 unchanged; what moves is INSIDE the
    # pipeline (stations, instructions as facts, target-aware guard, dedup,
    # anchor buffer) and the bible, so the comparison with S6 isolates the
    # batch.
    "S7": [("S7-1", "entry", "score"), ("S7-2", "entry", "score"),
           ("S7-3", "entry", "score"),
           ("S7-C", "chapter", "chapitre complet, hors score")],
    # CH7: the rehearsal. One run, the whole chapter, two entries.
    "CH7": [("CH7", None, "répétition — chapitre 7 en conditions réelles")],
}


def time_per_node(metrics: list[dict]) -> dict[str, float]:
    """Durations aggregated per node: the deliverable for the 28-minute margin."""
    out: dict[str, float] = {}
    for m in metrics:
        key = (m.get("noeud") or "?").split("/")[0]
        out[key] = round(out.get(key, 0.0) + m.get("wall_s", 0.0), 1)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="factory calibrate",
                                description="Calibration stages of chapter 2 and the "
                                            "chapter 7 rehearsal, one run file per draw.")
    p.add_argument("--stage", choices=["A", "B", "Bp", "C", "S6", "S7", "CH7"],
                   required=True)
    # Seed of the drift draw, recorded in the frontmatter: the draw varies from
    # run to run (else the same sentence at the same place becomes a liturgy of
    # our own template), yet a run replays identically when a gesture misfires.
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--skip-preflight", action="store_true",
                   help="passe outre le préflight — les durées relevées ne "
                        "sont alors PAS comparables au run de référence")
    p.add_argument("--only", nargs="*", default=None)
    p.add_argument("--out-dir", default=None)
    args = p.parse_args(argv)

    # PREFLIGHT, BLOCKING FOR THE TIMED STAGES ONLY (ADR-0016).
    #
    # Calibration tooling judges prose, not durations, so its preflight was a
    # warning. Session 6 measures the COST of the three-segment split and
    # recomputes the 28-minute budget from those figures; a run played during
    # `mediaanalysisd` gave uninterpretable times (32 and 49 minutes at runs 3
    # and 4, holes of 5 to 18 minutes between two calls). The other stages keep
    # the old rule: a stage's rule is not changed in passing.
    #
    # Since revamp step 4 the preflight is the first graph node, run BEFORE
    # EVERY RUN: blocking for the timed stages, a warning elsewhere.
    timer = args.stage in ("S6", "S7", "CH7")
    preflight_request = {"strict": timer and not args.skip_preflight, "timer": timer}
    if timer and args.skip_preflight:
        print("  (--skip-preflight : on passe outre, temps NON comparables)",
              file=sys.stderr)

    rag = args.stage != "A"
    # Runs land under experiments/runs/<date>-<stage> (ADR-0003).
    out_dir = Path(args.out_dir or (
        RACINE / "experiments" / "runs"
        / f"{datetime.now():%Y%m%d}-{args.stage.lower()}"))
    out_dir.mkdir(parents=True, exist_ok=True)

    # LATE import: building the graph imports chromadb, and stage A must run
    # with the container down. The import itself does not connect; the order
    # stays clean.
    from factory.pipeline.graph import build_graph
    graph = build_graph()

    for ident, brief, role in PLAN_RUNS[args.stage]:
        if args.only and ident not in args.only:
            continue
        print(f"\n{'=' * 66}\n[{ident}] {role} — rag={rag}\n{'=' * 66}",
              flush=True)
        # Protocol §5: the routing journal is cleared before each run so the
        # collections seen are attributable to THIS run alone.
        retrieval.clear_routing()
        # One seed PER RUN: three runs of one stage must draw different drifts,
        # else the variation sought is cancelled inside the series itself.
        # Recorded in the frontmatter.
        seed = (args.seed if args.seed is not None
                  else random.randrange(1, 10**6))
        start, wall_start = time.monotonic(), time.time()
        # `entry_count` short-circuits the plan (item 10) and `prefix` is the
        # text posed in advance (item 5), for single-entry runs only: a full
        # chapter keeps its plan and its own headers.
        mono = role == "score"
        # CHAPTER 7 differs from the rest by STRUCTURE, not wiring: two entries
        # the same day, the first two sentences without quotation. `entry_specs`
        # carries that structure; elsewhere it is empty and behaviour unchanged
        # (ADR-0018, doctrine 9).
        ch7 = args.stage == "CH7"
        # The chapter spec builds the state (step 5); the stage only sets the
        # run options: brief version, RAG, micro-nodes, segments, single entry.
        spec = load_chapter(7 if ch7 else 2)
        served = {"entry": spec.entry_brief, "chapter": spec.brief}.get(brief, brief)
        try:
            status = graph.invoke(
                {**spec.state(
                    seed=seed,
                    brief=None if ch7 else served,
                    entry_count=None if ch7 else (1 if mono else 3),
                    rag=rag,
                    micro_nodes=args.stage in ("C", "S6", "S7", "CH7"),
                    # Session 6's MEASURED VARIABLE: outside S6, `write` stays
                    # the single call everything was timed by.
                    segments=args.stage in ("S6", "S7", "CH7"),
                    prefix=None if ch7 else (
                        spec.prefix if args.stage in ("Bp", "C", "S6", "S7") else ""),
                 ),
                 "preflight": preflight_request},
                config={"recursion_limit": 50},
            )
        except PreflightError as exc:
            print(f"\n{exc}\n", file=sys.stderr)
            return 1
        for w in status.get("preflight_warnings") or []:
            print(f"  ⚠ {w}", file=sys.stderr)
        duration = time.monotonic() - start
        # TWO CLOCKS, measuring different things (ADR-0016): `time.monotonic()`
        # STOPS during system sleep, `time.time()` does not, and the stage budget
        # is WALL time. Found at S7-3: `duree_s` said 374 s while the model calls
        # summed to 2682 s, after two Maintenance Sleeps (`pmset -g log`).
        wall_duration = time.time() - wall_start

        entries = status.get("repaired") or status.get("reviewed") or status["scenes"]
        text = "\n\n".join(entries)
        lint = analyze(text)
        per_node = time_per_node(status.get("metrics") or [])
        # TIME PER SEGMENT: the figure deciding whether the split fits the 28'
        # budget. The three writing calls carry a label « entrée N/segment », so
        # they sum per segment without another counter in the graph.
        segment_times: dict[str, float] = {}
        for m in status.get("metrics") or []:
            seg = m.get("segment")
            if seg:
                # `wall_s`, not `ms`: the key `chat()` produces and the one
                # `time_per_node` has always used. The first version summed a
                # missing key and returned 0.0 s per segment: a wrong figure
                # reads as a measure where an absence would have shown.
                segment_times[seg] = round(
                    segment_times.get(seg, 0.0) + m.get("wall_s", 0.0), 1)
        guards = [w for w in status.get("warnings", []) if "garde-fou 60 %" in w]
        collections = sorted(set(retrieval.routing()))
        # `ctx_need` is the only reliable window-saturation signal: Ollama
        # truncates silently and reports only what it read (ADR-0008). Mandatory
        # reading for the corrective batch, whose extra texture raises it.
        ctx_max = max((m.get("ctx_need", 0) for m in status.get("metrics") or []),
                      default=0)

        path = out_dir / f"run-{ident}.md"
        path.write_text(
            "---\n"
            f"run: {ident}\n"
            f"etage: {args.stage}\n"
            f"role: {role}\n"
            f"rag: {rag}\n"
            f"ctx_need_max: {ctx_max}\n"
            f"graine: {seed}\n"
            f"segments: {args.stage in ('S6', 'S7', 'CH7')}\n"
            f"temps_par_segment: {json.dumps(segment_times, ensure_ascii=False)}\n"
            f"date: {datetime.now().isoformat(timespec='seconds')}\n"
            f"mots: {len(text.split())}\n"
            f"entrees_generees: {len(entries)}\n"
            f"entrees_detectees: {lint['entrees']}\n"
            f"temperature: 0.7\n"
            f"duree_s: {duration:.0f}\n"
            f"duree_mur_s: {wall_duration:.0f}\n"
            f"veille_s: {max(0, wall_duration - duration):.0f}\n"
            f"done_reason: {'length' if ends_mid_sentence(text) else 'stop'}\n"
            f"temps_par_noeud: {json.dumps(per_node, ensure_ascii=False)}\n"
            f"garde_fou_60: {len(guards)}\n"
            f"collections_interrogees: {json.dumps(collections, ensure_ascii=False)}\n"
            f"fin_pendante: {ends_mid_sentence(text)}\n"
            f"plan: {json.dumps(status.get('plan') or [], ensure_ascii=False)}\n"
            f"plan_report: {json.dumps(status.get('plan_report') or '', ensure_ascii=False)}\n"
            f"coherence: {json.dumps(status.get('coherence') or '', ensure_ascii=False)}\n"
            f"warnings: {json.dumps(status.get('warnings') or [], ensure_ascii=False)}\n"
            "---\n\n" + text + "\n",
            encoding="utf-8",
        )
        print(f"[{ident}] {len(text.split())} mots, {len(entries)} entrée(s), "
              f"{duration:.0f}s → {path}")
        # A gap above 30 s between the clocks means the machine slept or was
        # suspended. Say it LOUD: contaminated durations compare to nothing, and
        # duration is the session's central figure (ADR-0016).
        if wall_duration - duration > 30:
            print(f"  ⚠ VEILLE DÉTECTÉE : {wall_duration - duration:.0f}s d'écart "
                  f"entre l'horloge de mur ({wall_duration:.0f}s) et le temps de "
                  f"calcul ({duration:.0f}s). Les durées de ce run ne sont PAS "
                  f"comparables. Brancher la machine et relancer "
                  f"(`caffeinate -is`).", file=sys.stderr)
        print(f"        temps par nœud : {per_node}")
        print(f"        collections interrogées : {collections or 'aucune'}")
        for g in guards:
            print(f"  ⚠ {g}", file=sys.stderr)

    print(f"\nGrille : factory eval grid {out_dir} 450-600")
    return 0


if __name__ == "__main__":
    sys.exit(main())
