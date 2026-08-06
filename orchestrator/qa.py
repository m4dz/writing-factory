#!/usr/bin/env python3
"""Rôle QA/lint — modèle distinct du modèle auteur (LOCAL).

Tranché au benchmark : Qwen 2.5 7B pour les tâches où nemo échoue en
génération créative — réécrire les fuites d'anglais, et vérifier la cohérence
au format strict. Qwen est d'un autre lignage (pas la tendance au leak de
nemo), rapide (~28 tok/s), et discipliné sur le format.

Cette phase tourne APRÈS toute la génération : Ollama swappe nemo → Qwen une
seule fois. On évite tout embedding ici (la dérivation de faits lit les fiches
par id déterministe, pas par similarité) pour ne pas rappeler nomic-embed.
"""

import os
import re

from llm import chat
from retrieval import character_context

QA_MODEL = os.environ.get("QA_MODEL", "qwen2.5:7b-instruct")

# --- Réparation linguistique -------------------------------------------------

_REPAIR_SYS = (
    "Tu es correcteur linguistique. Tu réécris le texte en français en "
    "corrigeant TOUT passage qui n'est pas en français (mot ou phrase). Tu ne "
    "changes NI le sens, NI le style, NI l'ordre, NI la ponctuation des "
    "dialogues. Tu rends UNIQUEMENT le texte corrigé, rien d'autre."
)


def repair(text: str) -> tuple[str, dict]:
    """Réécrit un passage en corrigeant les fuites de langue (texte→texte)."""
    # Marge : la version FR peut être un peu plus longue que l'original.
    budget = min(2000, max(600, int(len(text) / 3) + 200))
    return chat(_REPAIR_SYS, text, model=QA_MODEL, temperature=0.2,
                num_predict=budget)


# --- Cohérence fait par fait -------------------------------------------------

_FACTS_SYS = (
    "Tu extrais des FAITS VÉRIFIABLES de fiches de personnages : ce que chaque "
    "personnage sait ou ignore, les faits établis du passé, les contraintes. "
    "Tu rends une liste, un fait par ligne, préfixé « - », sans commentaire. "
    "Maximum 6 faits, les plus structurants."
)

_CHECK_SYS = (
    "Tu es un VÉRIFICATEUR FACTUEL, pas un critique littéraire. Interdiction "
    "absolue de commenter la qualité, de suggérer des améliorations ou de "
    "réécrire quoi que ce soit. Tu vérifies mécaniquement des faits, une ligne "
    "par fait, format EXACT :\n"
    "FAIT n : OUI — <preuve dans le texte>\n"
    "FAIT n : NON — <ce que le texte dit et qui contredit>\n\n"
    "EXEMPLE —\n"
    "FAITS :\n1. Marie ignore que Paul ment.\n2. Il pleut sur la ville.\n"
    "--- CHAPITRE ---\nMarie sourit à Paul, pleine de confiance. Le soleil "
    "inondait la place.\n"
    "RÉPONSE ATTENDUE :\n"
    "FAIT 1 : OUI — Marie reste confiante, rien n'indique qu'elle sait.\n"
    "FAIT 2 : NON — le texte dit que le soleil inondait la place.\n\n"
    "Maintenant, traite les faits réels ci-dessous de la même façon."
)


def derive_facts(characters: list[str]) -> tuple[list[str], dict]:
    """Dérive les faits structurants depuis les fiches (fetch par id, no embed)."""
    ctx = "\n\n".join(character_context(c) for c in characters if character_context(c))
    text, m = chat(_FACTS_SYS, ctx, model=QA_MODEL, temperature=0.1,
                   num_predict=400)
    facts = [
        re.sub(r"^\s*[-*]\s*", "", line).strip()
        for line in text.splitlines()
        if line.strip().startswith(("-", "*"))
    ]
    return [f for f in facts if f], m


def check_facts(facts: list[str], chapter: str) -> tuple[str, dict]:
    """Vérifie TOUS les faits en un appel numéroté (protocole validé au
    benchmark : un seul appel groupé = format tenu, contrairement au
    fait-par-fait qui dérive vers la critique d'atelier)."""
    numbered = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(facts))
    user = f"FAITS :\n{numbered}\n\n--- CHAPITRE ---\n{chapter}"
    text, m = chat(_CHECK_SYS, user, model=QA_MODEL, temperature=0.0,
                   num_predict=700)
    return text.strip(), m
