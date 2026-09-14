#!/usr/bin/env python3
"""Actor mode at the command line: talk to a character of the bible.

    factory chat --character judith
    factory chat --character judith --nom Judith --no-memoire

In-session commands: `/quit` ends and writes the memory, `/oubli` ends
without writing, `/etat` prints the rolling summary and the cost of the turns.

Preflight is NOT run here, unlike the author mode: a conversation is watched
live and stopped with Ctrl-C, where a chapter runs twenty minutes unattended.
The model is the same (ADR-0006), so a session started right after a chapter
finds nemo already warm.
"""

import argparse
import sys

from factory.roleplay.session import Session


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="factory chat",
                                description="Dialoguer avec un personnage.")
    p.add_argument("--character", required=True,
                   help="doc_id de la fiche (ex: judith)")
    p.add_argument("--nom", default=None,
                   help="Nom d'usage du personnage (défaut : déduit du doc_id)")
    p.add_argument("--no-memoire", action="store_true",
                   help="Ignorer les souvenirs des sessions précédentes")
    p.add_argument("--keep-turns", type=int, default=None,
                   help="Échanges gardés verbatim avant fonte dans le résumé")
    args = p.parse_args(argv)

    kwargs = {"name": args.nom, "remind": not args.no_memoire}
    if args.keep_turns is not None:
        kwargs["keep_turns"] = args.keep_turns
    try:
        session = Session(args.character, **kwargs)
    except ValueError as exc:
        raise SystemExit(str(exc))

    print(f"— Vous parlez à {session.name} ({args.character}).")
    if session.reminders:
        print(f"  {len(session.reminders)} souvenir(s) de sessions précédentes "
              "chargé(s).")
    print("  /quit pour finir, /oubli pour finir sans garder, /etat pour l'état.\n")

    while True:
        try:
            question = input("vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            question = "/quit"

        if not question:
            continue
        if question in ("/quit", "/oubli"):
            if question == "/oubli":
                print("(session oubliée, rien n'est écrit)")
                return
            path = session.close()
            print(f"(souvenir écrit : {path})" if path
                  else "(session trop courte, aucun souvenir)")
            if session.warnings:
                print("Alertes de la session :")
                for w in session.warnings:
                    print(f"  ⚠ {w}")
            return
        if question == "/etat":
            print(f"\n[résumé glissant]\n{session.summary or '(vide)'}")
            if session.warnings:
                print("[alertes]")
                for w in session.warnings:
                    print(f"  ⚠ {w}")
            total = sum(m["wall_s"] for m in session.metrics)
            print(f"[{len(session.metrics)} appels, {total:.0f} s cumulées, "
                  f"fenêtre : {session.metrics[-1]['ctx_need']:.2f}]\n"
                  if session.metrics else "[aucun appel]\n")
            continue

        reply = session.say(question)
        print(f"\n{session.name} > {reply}\n")


if __name__ == "__main__":
    sys.exit(main())
