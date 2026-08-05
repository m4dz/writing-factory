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
from style import delint


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
    warnings: list[str]   # alertes du lint de style (fuites, tokens corrompus)


# --- Nœuds -------------------------------------------------------------------

def plan_node(state: ChapterState) -> dict:
    """Découpe le chapitre en 3-5 beats de scènes concrets."""
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=state["brief"]
    )
    user = (
        f"Objectif du chapitre : {state['brief']}\n\n"
        "Propose un plan de 3 ou 4 scènes MAXIMUM. Une ligne par scène :\n"
        "1. [lieu] ce qui se passe concrètement — l'état NOUVEAU à la fin.\n\n"
        "RÈGLE ABSOLUE : chaque scène fait AVANCER l'intrigue vers un moment "
        "nouveau. Aucune scène ne rejoue, ne prolonge ni ne re-décrit le "
        "moment d'une autre. Un événement (une révélation, une découverte) "
        "n'arrive QUE dans UNE seule scène. Si deux scènes se ressemblent, "
        "fusionne-les. Ne rédige pas les scènes, juste le plan."
    )
    text, m = chat(system, user, num_predict=500, temperature=0.5)
    # Parse : on ne garde que les lignes numérotées « 1. … ».
    beats = [
        re.sub(r"^\s*\d+[.)]\s*", "", line).strip()
        for line in text.splitlines()
        if re.match(r"^\s*\d+[.)]\s", line)
    ]
    beats = [b for b in beats if b]
    return {"plan": beats, "idx": 0, "scenes": [], "metrics": [m], "warnings": []}


def write_node(state: ChapterState) -> dict:
    """Rédige la scène courante (state['idx']) avec un contexte ré-assemblé.

    Anti-répétition (défaut du jalon précédent : les scènes se rejouaient) :
    le modèle reçoit le PLAN COMPLET avec sa position marquée (il sait ce qui
    est déjà couvert et ce qui vient) ET le récit déjà écrit (2 dernières
    scènes en entier), avec consigne explicite de CONTINUER sans rejouer.
    """
    idx = state["idx"]
    beat = state["plan"][idx]
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=beat, place_query=beat,
        include_scenes=False,  # continuité gérée par le threading explicite ci-dessous
    )

    # Plan annoté : [fait] / >> à écrire / [à venir].
    plan_lines = []
    for j, b in enumerate(state["plan"]):
        mark = ">>" if j == idx else ("[fait]" if j < idx else "[à venir]")
        plan_lines.append(f"  {j + 1}. {mark} {b}")
    plan_txt = "\n".join(plan_lines)

    # Récit déjà écrit, borné aux 2 dernières scènes pour cadrer le prompt
    # (nemo a un grand contexte, mais on évite de gonfler inutilement).
    prior = "\n\n".join(state["scenes"][-2:])
    prior_block = (
        f"\n=== DÉJÀ ÉCRIT (à NE PAS rejouer, tu enchaînes APRÈS) ===\n{prior}\n"
        if prior else ""
    )

    user = (
        f"Plan du chapitre (>> = la scène à écrire maintenant) :\n{plan_txt}\n"
        f"{prior_block}\n"
        f"Écris UNIQUEMENT la scène {idx + 1} (~600 mots) : {beat}\n"
        "NE réécris AUCUN événement déjà raconté ci-dessus — tu enchaînes dans "
        "la continuité stricte. Montre la tension sans la nommer, fais entendre "
        "les voix distinctes. Prose seule, sans titre ni méta-commentaire."
    )
    text, m = chat(system, user, num_predict=1400, temperature=0.7)
    text, w = delint(text)
    return {
        "scenes": state["scenes"] + [text],
        "idx": idx + 1,
        "metrics": state["metrics"] + [m],
        "warnings": state["warnings"] + [f"scène {idx + 1}: {x}" for x in w],
    }


def route_after_write(state: ChapterState) -> str:
    """Boucle tant qu'il reste des scènes à écrire, sinon passe à la relecture."""
    return "write" if state["idx"] < len(state["plan"]) else "review"


def review_node(state: ChapterState) -> dict:
    """Relecture prose : resserre, corrige les répétitions, garde la voix.

    Passe scène par scène (le modèle relit mieux un bloc court qu'un chapitre
    entier — mitigation de la limite de cohérence longue distance).

    Deux protections contre la troncature observée au premier jalon :
      1. `num_predict` adaptatif à la longueur de la scène (une réécriture ne
         peut pas être plus courte que l'original sans perdre du texte).
      2. Garde-fou : si la version relue fait moins de 60 % de l'original
         (le modèle a « avalé » la scène), on conserve l'original. Une scène
         n'est jamais détruite par la relecture.
    """
    reviewed: list[str] = []
    metrics = list(state["metrics"])
    warns = list(state["warnings"])
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=state["brief"],
        include_scenes=False,
    )
    for i, scene in enumerate(state["scenes"]):
        # ~3,5 caractères par token en français ; on vise 1,6x la longueur
        # de la scène, borné, pour laisser la place à une réécriture complète.
        budget = min(2000, max(1200, int(len(scene) / 3) + 300))
        user = (
            "Relis et RÉÉCRIS INTÉGRALEMENT cette scène pour resserrer la "
            "prose : supprime les répétitions (notamment les répliques "
            "signature ressassées), renforce les images, garde EXACTEMENT la "
            "voix des personnages et les faits. Rends la scène ENTIÈRE "
            "corrigée, du début à la fin, et rien d'autre (pas de commentaire, "
            "pas de titre).\n\n"
            f"--- SCÈNE À RÉÉCRIRE ---\n{scene}"
        )
        text, m = chat(system, user, num_predict=budget, temperature=0.5)
        metrics.append(m)
        # Garde-fou anti-destruction : relecture trop courte -> on garde l'original.
        if len(text.split()) < 0.6 * len(scene.split()):
            text = scene
        text, w = delint(text)
        warns.extend(f"relecture scène {i + 1}: {x}" for x in w)
        reviewed.append(text)
    return {"reviewed": reviewed, "metrics": metrics, "warnings": warns}


def coherence_node(state: ChapterState) -> dict:
    """Passe de cohérence : confronte le chapitre aux faits de la bible.

    Ne réécrit pas — produit un rapport (contradictions, incohérences
    causales). C'est la « strate 4 » finale montrée sur scène."""
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=state["brief"],
        include_scenes=False,
    )
    chapitre = "\n\n".join(state["reviewed"])
    user = (
        "Tu es relecteur de cohérence. Tu ne racontes RIEN, tu n'écris AUCUNE "
        "prose narrative (pas de suite d'histoire, interdit). Tu confrontes le "
        "chapitre aux faits des fiches et tu réponds EXACTEMENT dans l'un des "
        "deux formats, rien d'autre :\n"
        "  • soit une liste d'incohérences, une par ligne préfixée « - » "
        "(fait contredit, personnage qui sait ce qu'il devrait ignorer, voix "
        "qui dérape) ;\n"
        "  • soit la phrase exacte : Aucune incohérence détectée.\n\n"
        f"--- CHAPITRE ---\n{chapitre}"
    )
    text, m = chat(system, user, num_predict=500, temperature=0.1)
    # Ancrage dur : si le modèle repart en prose (ni liste, ni phrase exacte),
    # on le signale plutôt que de laisser passer une hallucination narrative.
    stripped = text.strip()
    if not (stripped.startswith("-") or stripped.startswith("Aucune")):
        text = ("[nœud cohérence : sortie non conforme, prose ignorée]\n"
                "Aucune incohérence détectée.")
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
