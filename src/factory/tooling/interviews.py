#!/usr/bin/env python3
"""Trois interviews de Judith (mode ACTEUR), prêtes à jouer, pour la scène.

Génère trois sessions de roleplay INDÉPENDANTES avec la narratrice, chacune de
trois questions. Ce sont des ASSETS DE DÉMO pré-générés (RUNBOOK §4.1) : on les
curera à la main avant la scène. Le but n'est pas de mesurer le pipeline mais de
produire trois transcripts rejouables.

Trois décisions, alignées sur la nature de la tâche :

- **Chaque interview = une `Session` neuve = sa propre fenêtre de contexte.** À
  l'intérieur d'une interview, les trois questions PARTAGENT le contexte : à la
  troisième, le modèle voit les deux questions précédentes ET ses propres
  réponses (mémoire verbatim des N derniers tours ; à trois tours rien ne fond
  dans le résumé). C'est le « même contexte » voulu.

- **`rappeler=False`.** Aucune interview ne charge les souvenirs des autres :
  les trois prises sont comparables parce qu'INDÉPENDANTES. Les jeux de
  questions se recoupent volontairement (Q3 identique partout) ; la comparaison
  n'est honnête que si les contextes ne fuient pas l'un dans l'autre.

- **`close(indexer=False)`.** On écrit les trois transcripts Markdown sous
  `sessions/judith/`, mais on n'indexe RIEN dans la collection Chroma
  `sessions`. Une prise de démo régénérable n'a pas à devenir un souvenir
  canonique du personnage qui polluerait les sessions suivantes.

Le personnage est servi FIREWALLÉ : la fiche indexée dit « la narratrice », le
nom « Judith » n'y figure jamais (traduction à l'indexation). On passe donc
`nom="la narratrice"` — le défaut de `Session` serait « Judith », qui
réinjecterait dans le prompt système le nom que le firewall a retiré.

Pas de préflight, comme `chat_character.py` : une génération courte se surveille
en direct. Il faut seulement qu'Ollama tourne (modèle auteur nemo) et que Chroma
serve la collection `auteur`.

Usage (depuis la racine du dépôt, venv de l'orchestrateur) :
    orchestrator/.venv/bin/python outillage/run_interviews_judith.py
    orchestrator/.venv/bin/python outillage/run_interviews_judith.py --temperature 0.8

Stdlib + le venv de l'orchestrateur (chromadb-client). Réutilise
`orchestrator/roleplay.py` sans le modifier.
"""

import argparse
import time


from factory.roleplay.session import Session

# doc_id de retrieval de la narratrice (clé des chunks `judith::voix`, …). Le nom
# servi au modèle est « la narratrice » : cf. le docstring, le firewall
# d'indexation scrubbe « Judith » du texte de la fiche.
DOC_ID = "judith"
NOM = "la narratrice"

# Les trois jeux, verbatim. Une entrée = une interview = trois questions posées
# dans l'ordre, dans un seul et même contexte.
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


def jouer_interview(numero: int, questions: list[str], *,
                    temperature: float, keep_turns: int) -> dict:
    """Joue une interview de bout en bout et rend son bilan.

    Une seule `Session` pour les trois questions : le contexte est partagé à
    l'intérieur, isolé à l'extérieur (`rappeler=False`).
    """
    print(f"\n{'=' * 70}\nINTERVIEW {numero} — {len(questions)} questions\n{'=' * 70}")

    session = Session(DOC_ID, nom=NOM, keep_turns=keep_turns, rappeler=False)

    for i, question in enumerate(questions, 1):
        t0 = time.monotonic()
        reponse = session.say(question, temperature=temperature)
        dt = time.monotonic() - t0
        print(f"\n[Q{i}] {question}")
        print(f"[{NOM}, {dt:.0f}s] {reponse}")

    # close() force une dernière fonte (résumé) puis écrit le Markdown ;
    # indexer=False → rien n'entre dans la collection `sessions`.
    chemin = session.close(indexer=False)

    total = sum(m["wall_s"] for m in session.metrics)
    ctx_max = max((m["ctx_need"] for m in session.metrics), default=0.0)
    if session.warnings:
        print(f"\n⚠ Interview {numero} — {len(session.warnings)} alerte(s) :")
        for w in session.warnings:
            print(f"    {w}")
    print(f"\n→ Interview {numero} écrite : {chemin}"
          f"  ({len(session.metrics)} appels, {total:.0f}s, ctx_need max {ctx_max:.2f})")

    return {
        "numero": numero,
        "chemin": chemin,
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
        Session(DOC_ID, nom=NOM, rappeler=False)  # valide la fiche AVANT de jouer
    except ValueError as exc:
        raise SystemExit(
            f"Fiche « {DOC_ID} » introuvable dans la collection Chroma. "
            f"Vérifier que la bible est indexée (collection `auteur`, chunks "
            f"{DOC_ID}::voix …) et que Chroma répond.\n  → {exc}")

    bilans = []
    for numero, questions in enumerate(INTERVIEWS, 1):
        bilans.append(jouer_interview(
            numero, questions,
            temperature=args.temperature, keep_turns=args.keep_turns))

    print(f"\n{'=' * 70}\nBILAN — trois interviews de {NOM}\n{'=' * 70}")
    total_alertes = sum(len(b["warnings"]) for b in bilans)
    for b in bilans:
        marque = f"  ⚠ {len(b['warnings'])} alerte(s)" if b["warnings"] else ""
        print(f"  Interview {b['numero']} : {b['chemin']}{marque}")
    print(f"\n  {total_alertes} alerte(s) au total, "
          f"{sum(b['wall_s'] for b in bilans):.0f}s cumulées.")
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
