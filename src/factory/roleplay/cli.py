#!/usr/bin/env python3
"""Mode ACTEUR en ligne de commande : parler à un personnage de la bible.

    python chat_character.py --character judith
    python chat_character.py --character judith --nom Judith --no-memoire

Commandes en session : `/quit` termine et écrit le souvenir, `/oubli` termine
sans rien écrire, `/etat` affiche le résumé glissant et le coût des tours.

Le préflight n'est PAS appelé ici, contrairement au mode auteur : une
conversation se surveille en direct et s'interrompt d'un Ctrl-C, là où un
chapitre tourne vingt minutes sans témoin. En revanche le modèle est le même,
donc une session lancée juste après un chapitre trouvera nemo déjà chaud.
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
