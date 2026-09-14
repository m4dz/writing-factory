#!/usr/bin/env python3
"""Three interviews of Judith (ACTOR mode), ready to play for the stage.

Generates three INDEPENDENT roleplay sessions with the narrator, three
questions each. They are pre-generated DEMO ASSETS (runbook §4.1), curated by
hand before the stage; the aim is three replayable transcripts, not a measure
of the pipeline.

Three decisions, matched to the task:

- **Each interview = a fresh `Session` = its own context window.** Inside an
  interview the three questions SHARE the context: at the third, the model sees
  the two previous questions AND its own answers (verbatim memory of the last N
  turns; nothing melts into the summary at three turns).

- **`remind=False`.** No interview loads the memories of the others: the three
  takes compare because they are INDEPENDENT. The question sets overlap by
  design (Q3 identical everywhere); the comparison is honest only if no context
  leaks into another.

- **`close(indexer=False)`.** The three Markdown transcripts are written under
  `sessions/judith/`; nothing is indexed in the Chroma collection `sessions`. A
  regenerable demo take must not become a canonical memory of the character
  that would pollute later sessions.

The character is served FIREWALLED (ADR-0017): the indexed sheet says
« la narratrice », never « Judith ». Hence `name="la narratrice"`: the
`Session` default would be « Judith » and would reinject into the system prompt
the name the firewall removed.

No preflight, as in `factory chat`: a short generation is watched live. Ollama
must run (author model nemo) and Chroma must serve the collection `auteur`.

Usage (repository root, project venv):
    .venv/bin/python -m factory.tooling.interviews
    .venv/bin/python -m factory.tooling.interviews --temperature 0.8
"""

import argparse
import time


from factory.roleplay.session import Session

# Retrieval doc_id of the narrator (key of the chunks `judith::voix`, …). The
# name served to the model is « la narratrice »: the indexing firewall scrubs
# « Judith » from the sheet text (ADR-0017).
DOC_ID = "judith"
NAME = "la narratrice"

# The three sets, verbatim. One item = one interview = three questions asked in
# order, in one and the same context.
INTERVIEWS: list[list[str]] = [
    # INT-a
    [
        "Que faites-vous quand une phrase que vous avez écrite contredit votre souvenir ?",
        "Un personnage de votre manuscrit ment. Vous le corrigez ?",
        "Avez-vous déjà questionné la nature de votre réalité ?",
    ],
    # INT-b
    [
        "Que faites-vous quand une phrase que vous avez écrite contredit votre souvenir ?",
        "Qu'est-ce que vous faites d'une phrase juste que vous n'aimez pas ?",
        "Avez-vous déjà questionné la nature de votre réalité ?",
    ],
    # INT-c
    [
        "Que faites-vous quand une phrase que vous avez écrite contredit votre souvenir ?",
        "Y a-t-il une entrée de votre carnet que vous n'avez jamais réussi à corriger ?",
        "Avez-vous déjà questionné la nature de votre réalité ?",
    ],
]


def play_interview(number: int, questions: list[str], *,
                    temperature: float, keep_turns: int) -> dict:
    """Play one interview end to end and return its summary.

    A single `Session` for the three questions: context shared inside, isolated
    outside (`remind=False`).
    """
    print(f"\n{'=' * 70}\nINTERVIEW {number} — {len(questions)} questions\n{'=' * 70}")

    session = Session(DOC_ID, name=NAME, keep_turns=keep_turns, remind=False)

    for i, question in enumerate(questions, 1):
        t0 = time.monotonic()
        reply = session.say(question, temperature=temperature)
        dt = time.monotonic() - t0
        print(f"\n[Q{i}] {question}")
        print(f"[{NAME}, {dt:.0f}s] {reply}")

    # close() forces a last melt (summary) then writes the Markdown;
    # indexer=False → nothing enters the collection `sessions`.
    path = session.close(indexer=False)

    total = sum(m["wall_s"] for m in session.metrics)
    ctx_max = max((m["ctx_need"] for m in session.metrics), default=0.0)
    if session.warnings:
        print(f"\n⚠ Interview {number} — {len(session.warnings)} alerte(s) :")
        for w in session.warnings:
            print(f"    {w}")
    print(f"\n→ Interview {number} écrite : {path}"
          f"  ({len(session.metrics)} appels, {total:.0f}s, ctx_need max {ctx_max:.2f})")

    return {
        "numero": number,
        "chemin": path,
        "warnings": list(session.warnings),
        "appels": len(session.metrics),
        "wall_s": total,
        "ctx_need_max": ctx_max,
    }


def main() -> None:
    p = argparse.ArgumentParser(
        description="Trois interviews de Judith en mode acteur (assets de démo).")
    p.add_argument("--temperature", type=float, default=0.85,
                   help="Température de génération des répliques (défaut 0.85).")
    p.add_argument("--keep-turns", type=int, default=6,
                   help="Tours gardés verbatim avant fonte (défaut 6 ; sans "
                        "effet à trois tours, homogène avec le REPL).")
    args = p.parse_args()

    try:
        Session(DOC_ID, name=NAME, remind=False)  # validates the sheet BEFORE playing
    except ValueError as exc:
        raise SystemExit(
            f"Fiche « {DOC_ID} » introuvable dans la collection Chroma. "
            f"Vérifier que la bible est indexée (collection `auteur`, chunks "
            f"{DOC_ID}::voix …) et que Chroma répond.\n  → {exc}")

    summaries = []
    for number, questions in enumerate(INTERVIEWS, 1):
        summaries.append(play_interview(
            number, questions,
            temperature=args.temperature, keep_turns=args.keep_turns))

    print(f"\n{'=' * 70}\nBILAN — trois interviews de {NAME}\n{'=' * 70}")
    total_alerts = sum(len(b["warnings"]) for b in summaries)
    for b in summaries:
        mark = f"  ⚠ {len(b['warnings'])} alerte(s)" if b["warnings"] else ""
        print(f"  Interview {b['numero']} : {b['chemin']}{mark}")
    print(f"\n  {total_alerts} alerte(s) au total, "
          f"{sum(b['wall_s'] for b in summaries):.0f}s cumulées.")
    print("  Transcripts sous sessions/judith/ — à curer à la main avant la scène "
          "(section ## Transcription).")


if __name__ == "__main__":
    try:
        main()
    except (ConnectionError, OSError) as exc:
        raise SystemExit(
            f"Erreur réseau — Ollama ou Chroma injoignable ?\n  → {exc}\n"
            "  Ollama : launchctl bootstrap gui/501 "
            "scripts/local.ollama.plist, puis curl localhost:11434/api/tags.\n"
            "  Chroma : podman start stackfictionalwriting_chromadb_1.")
