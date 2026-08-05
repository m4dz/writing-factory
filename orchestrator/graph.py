#!/usr/bin/env python3
"""Orchestrateur « mode auteur » (LangGraph).

Pipeline montré sur scène (strate 4 du talk) :

    plan de scènes → écriture scène par scène → relecture → cohérence

C'est un graphe SÉQUENTIEL avec une boucle sur les scènes. Le contrôle de
flux est déterministe (LangGraph), la créativité est déléguée au modèle à
chaque nœud. Le contexte est ré-assemblé depuis la bible à chaque scène
(RAG dynamique, cf. retrieval.py), jamais figé.
"""

import re
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from llm import chat
from retrieval import assemble_system_prompt


# --- État du graphe ----------------------------------------------------------

class ChapterState(TypedDict):
    brief: str            # objectif du chapitre (entrée humaine)
    characters: list[str] # doc_ids des personnages présents
    plan: list[str]       # beats de scènes (sortie du nœud plan)
    idx: int              # index de la scène en cours d'écriture
    scenes: list[str]     # prose brute, une entrée par scène
    reviewed: list[str]   # prose après relecture
    coherence: str        # rapport de cohérence
    metrics: list[dict]   # timing par appel LLM (compte à rebours / profilage)


# --- Nœuds -------------------------------------------------------------------

def plan_node(state: ChapterState) -> dict:
    """Découpe le chapitre en 3-5 beats de scènes concrets."""
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=state["brief"]
    )
    user = (
        f"Objectif du chapitre : {state['brief']}\n\n"
        "Propose un plan de 3 à 5 scènes. Une ligne par scène, format :\n"
        "1. [lieu] tension/enjeu — ce qui se passe concrètement.\n"
        "Sois concret et resserré. Ne rédige PAS les scènes, juste le plan."
    )
    text, m = chat(system, user, num_predict=500, temperature=0.6)
    # Parse : on ne garde que les lignes numérotées « 1. … ».
    beats = [
        re.sub(r"^\s*\d+[.)]\s*", "", line).strip()
        for line in text.splitlines()
        if re.match(r"^\s*\d+[.)]\s", line)
    ]
    beats = [b for b in beats if b]
    return {"plan": beats, "idx": 0, "scenes": [], "metrics": [m]}


def write_node(state: ChapterState) -> dict:
    """Rédige la scène courante (state['idx']) avec un contexte ré-assemblé."""
    beat = state["plan"][state["idx"]]
    system = assemble_system_prompt(
        characters=state["characters"],
        scene_brief=beat,
        place_query=beat,
    )
    # Rappel des scènes déjà écrites : continuité immédiate sans tout recharger.
    precedent = ""
    if state["scenes"]:
        tail = state["scenes"][-1][-600:]
        precedent = f"\nFin de la scène précédente (pour enchaîner) :\n…{tail}\n"
    user = (
        f"Écris la scène suivante (~600 mots) du chapitre.\n"
        f"Beat à rendre : {beat}\n{precedent}\n"
        "Montre la tension sans la nommer. Fais entendre les voix distinctes. "
        "N'écris que la prose de la scène, sans titre ni méta-commentaire."
    )
    text, m = chat(system, user, num_predict=1000, temperature=0.85)
    return {
        "scenes": state["scenes"] + [text],
        "idx": state["idx"] + 1,
        "metrics": state["metrics"] + [m],
    }


def route_after_write(state: ChapterState) -> str:
    """Boucle tant qu'il reste des scènes à écrire, sinon passe à la relecture."""
    return "write" if state["idx"] < len(state["plan"]) else "review"


def review_node(state: ChapterState) -> dict:
    """Relecture prose : resserre, corrige les répétitions, garde la voix.

    Passe scène par scène (le modèle relit mieux un bloc court qu'un chapitre
    entier — mitigation de la limite de cohérence longue distance)."""
    reviewed: list[str] = []
    metrics = list(state["metrics"])
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=state["brief"]
    )
    for i, scene in enumerate(state["scenes"]):
        user = (
            "Relis et RÉÉCRIS cette scène pour resserrer la prose : supprime "
            "les répétitions (notamment les répliques signature ressassées), "
            "renforce les images, garde EXACTEMENT la voix des personnages et "
            "les faits. Rends uniquement la version corrigée, rien d'autre.\n\n"
            f"--- SCÈNE {i + 1} ---\n{scene}"
        )
        text, m = chat(system, user, num_predict=1000, temperature=0.5)
        reviewed.append(text)
        metrics.append(m)
    return {"reviewed": reviewed, "metrics": metrics}


def coherence_node(state: ChapterState) -> dict:
    """Passe de cohérence : confronte le chapitre aux faits de la bible.

    Ne réécrit pas — produit un rapport (contradictions, incohérences
    causales). C'est la « strate 4 » finale montrée sur scène."""
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=state["brief"]
    )
    chapitre = "\n\n".join(state["reviewed"])
    user = (
        "Tu es relecteur de cohérence. Confronte le chapitre ci-dessous aux "
        "faits des fiches. Liste UNIQUEMENT les contradictions ou incohérences "
        "causales (fait de la bible contredit, personnage qui sait ce qu'il "
        "devrait ignorer, voix qui dérape). Si tout est cohérent, réponds "
        "« Aucune incohérence détectée. » Format : liste courte.\n\n"
        f"--- CHAPITRE ---\n{chapitre}"
    )
    text, m = chat(system, user, num_predict=500, temperature=0.3)
    return {"coherence": text, "metrics": state["metrics"] + [m]}


# --- Assemblage du graphe ----------------------------------------------------

def build_graph():
    g = StateGraph(ChapterState)
    g.add_node("plan", plan_node)
    g.add_node("write", write_node)
    g.add_node("review", review_node)
    g.add_node("coherence", coherence_node)

    g.add_edge(START, "plan")
    g.add_edge("plan", "write")
    g.add_conditional_edges("write", route_after_write, ["write", "review"])
    g.add_edge("review", "coherence")
    g.add_edge("coherence", END)
    return g.compile()
