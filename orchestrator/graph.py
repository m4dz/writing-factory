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

from llm import chat, unload
from retrieval import assemble_system_prompt
from style import delint, ends_mid_sentence, trim_to_sentence
from qa import QA_MODEL, repair, derive_facts, check_facts, check_plan

# Une seule reprise du plan. La replanification coûte un rechargement de nemo
# (13 GB) : au-delà, on perdrait plus de temps de scène qu'on n'en sauverait, et
# un modèle qui rate deux fois la contrainte ne la comprendra pas à la troisième.
MAX_PLAN_ATTEMPTS = 2

# Une seule continuation par génération coupée. Monter `num_predict` ne résout
# rien — un modèle qui n'a pas fini à 1400 tokens remplira aussi bien 1800 :
# il occupe l'espace offert. La continuation, elle, ne coûte que quand le cas
# se produit (une scène sur quatre au run du 2026-08-06, ~50 s).
MAX_CONTINUATIONS = 1


# --- État du graphe ----------------------------------------------------------

class ChapterState(TypedDict):
    brief: str            # objectif du chapitre (entrée humaine)
    characters: list[str] # doc_ids des personnages présents
    facts: list[str]      # invariants dérivés de la bible (contraignent le plan)
    plan: list[str]       # beats de scènes (sortie du nœud plan)
    plan_report: str      # confrontation du plan aux faits, AVANT rédaction
    idx: int              # index de la scène en cours d'écriture
    scenes: list[str]     # prose brute, une entrée par scène
    reviewed: list[str]   # prose après relecture (nemo)
    repaired: list[str]   # prose après réparation linguistique (Qwen QA)
    coherence: str        # rapport de cohérence fait par fait (Qwen QA)
    metrics: list[dict]   # timing par appel LLM (compte à rebours / profilage)
    warnings: list[str]   # alertes du lint de style (fuites, tokens corrompus)


# --- Nœuds -------------------------------------------------------------------

def _recoller(debut: str, suite: str) -> str:
    """Recolle une continuation en supprimant le chevauchement.

    Le modèle recommence volontiers par la dernière phrase qu'il vient
    d'écrire, malgré la consigne : on cherche le plus long préfixe de la suite
    déjà présent dans la queue du début et on l'ôte.

    La jointure demande un peu de soin. Si la coupe est tombée en pleine phrase
    et que la suite ouvre une phrase NEUVE au lieu de finir la précédente
    (observé : « …dans un coin de la pièce Elle s'en approcha »), le fragment
    reste orphelin. On le ferme plutôt que de le supprimer — le supprimer
    coûterait une phrase entière de récit :
      * devant une réplique (tiret cadratin, guillemet), les points de
        suspension, qui sont la ponctuation française de la parole ou de la
        pensée interrompue. Un point donnerait « Il hésita, puis. — Tu mens » ;
      * devant une majuscule ordinaire, un point simple.
    """
    s = suite.lstrip()
    queue = debut[-800:]
    # Chevauchement EXACT, cherché au caractère près : un pas plus grossier
    # laisse un résidu de découpe au milieu du texte (« du marteau u qui »).
    # 30 caractères minimum pour ne pas confondre une coïncidence avec une
    # recopie.
    for k in range(min(len(queue), len(s)), 29, -1):
        if s.startswith(queue[-k:]):
            s = s[k:].lstrip()
            break

    d = debut.rstrip()
    if not ends_mid_sentence(d):
        return d + "\n\n" + s
    if s[:1] in "—–-«\"":
        return d + "…\n\n" + s
    if s[:1].isupper():
        return d + ". " + s
    return d + " " + s


def _generate_whole(system: str, user: str, *, num_predict: int,
                    temperature: float, label: str) -> tuple[str, list[dict], list[str]]:
    """Génère un texte ENTIER : relance si `num_predict` a coupé la génération.

    Ollama ne signale l'amputation que par `done_reason: "length"` — le texte
    revient coupé en plein mot, sans erreur. Observé au run du 2026-08-06 sur
    une scène (1400/1400 tokens) : la relecture a ensuite travaillé sur un
    texte tronqué, et la scène suivante a hérité d'un état narratif inachevé.

    Deux dispositifs, dans cet ordre : une continuation (le texte est rendu
    entier), puis en filet une coupe à la dernière phrase complète si le modèle
    dépasse encore. Le filet n'est jamais le premier recours : il rend une
    scène qui s'arrête tôt, donc sans l'état final que le plan lui demandait.
    """
    text, m = chat(system, user, num_predict=num_predict, temperature=temperature)
    metrics = [m]
    warns: list[str] = []

    for _ in range(MAX_CONTINUATIONS):
        if m.get("done_reason") != "length":
            break
        suite_user = (
            f"{user}\n\n=== CE QUI EST DÉJÀ ÉCRIT (fin du texte) ===\n"
            f"{text[-600:]}\n\n"
            "Ta génération a été coupée en cours de route. REPRENDS EXACTEMENT "
            "là où le texte s'arrête — sans le répéter, sans le résumer, sans "
            "recommencer — et TERMINE en quelques paragraphes. Écris seulement "
            "la suite."
        )
        suite, m = chat(system, suite_user,
                        num_predict=max(300, num_predict // 3),
                        temperature=temperature)
        metrics.append(m)
        text = _recoller(text, suite)
        warns.append(f"{label} : génération coupée, continuation demandée")

    if ends_mid_sentence(text):
        coupe = trim_to_sentence(text)
        if coupe != text:
            warns.append(f"{label} : fin coupée à la dernière phrase complète")
            text = coupe
        else:
            warns.append(f"{label} : texte encore amputé, aucune coupe propre "
                         "possible (à reprendre à la main)")
    return text, metrics, warns


def _parse_beats(text: str) -> list[str]:
    """Extrait les lignes numérotées « 1. … » d'une réponse de plan."""
    beats = [
        re.sub(r"^\s*\d+[.)]\s*", "", line).strip()
        for line in text.splitlines()
        if re.match(r"^\s*\d+[.)]\s", line)
    ]
    return [b for b in beats if b]


def _plan_user(brief: str, facts: list[str], feedback: str) -> str:
    """Prompt de planification, avec les invariants de la bible en contrainte."""
    contraintes = ""
    if facts:
        listing = "\n".join(f"  - {f}" for f in facts)
        contraintes = (
            "\nCONTRAINTES INVIOLABLES tirées de la bible du récit. Le plan ne "
            "doit RIEN prévoir qui les contredise — ni une révélation, ni un "
            f"aveu, ni une découverte qu'elles excluent :\n{listing}\n"
        )
    return (
        f"Objectif du chapitre : {brief}\n"
        f"{contraintes}\n"
        "Propose un plan de 3 ou 4 scènes MAXIMUM. Une ligne par scène :\n"
        "1. [lieu] ce qui se passe concrètement — l'état NOUVEAU à la fin.\n\n"
        "RÈGLE ABSOLUE : chaque scène fait AVANCER l'intrigue vers un moment "
        "nouveau. Aucune scène ne rejoue, ne prolonge ni ne re-décrit le "
        "moment d'une autre. Un événement (une révélation, une découverte) "
        "n'arrive QUE dans UNE seule scène. Si deux scènes se ressemblent, "
        "fusionne-les. Ne rédige pas les scènes, juste le plan."
        f"{feedback}"
    )


def _plan_feedback(violations: list[tuple[int, str, str]]) -> str:
    """Reproche adressé au planificateur : la contrainte violée, et où."""
    lignes = "\n".join(
        f"  - tu avais prévu « {citation} », ce qui contredit : {fait}"
        for _, fait, citation in violations
    )
    return (
        "\n\nTON PLAN PRÉCÉDENT ÉTAIT REFUSÉ. Il programmait des événements "
        f"interdits par la bible :\n{lignes}\n"
        "Refais le plan en atteignant l'objectif du chapitre AUTREMENT : garde "
        "la tension, mais n'organise pas ces événements-là."
    )


def plan_node(state: ChapterState) -> dict:
    """Dérive les invariants de la bible, puis planifie SOUS cette contrainte.

    L'ordre des modèles est dicté par la mémoire, pas par l'élégance : les
    faits sont dérivés par Qwen (4,8 GB) AVANT que nemo (13 GB) ne chauffe, et
    chaque bascule décharge le précédent. Les deux ensemble font 17,8 GB sur
    19,3 GB — la pression exacte qui a fait paniquer la machine.

    Pourquoi vérifier le plan ici plutôt que se fier au rapport de cohérence
    final : celui-ci arrive après quatorze minutes de rédaction. Il constate,
    il ne prévient pas, et sur scène on ne réécrit pas. Un plan tient en quatre
    lignes : le confronter coûte quelques secondes, le corriger coûte un
    rechargement de nemo — sans commune mesure avec un chapitre à jeter.
    """
    metrics: list[dict] = []
    warnings: list[str] = []

    facts, mf = derive_facts(state["characters"])
    metrics.append(mf)
    unload(QA_MODEL)  # place nette avant de charger nemo

    beats: list[str] = []
    rapport = "Plan non vérifié (aucun fait dérivé de la bible)."
    feedback = ""
    for attempt in range(1, MAX_PLAN_ATTEMPTS + 1):
        system = assemble_system_prompt(
            characters=state["characters"], scene_brief=state["brief"]
        )
        text, m = chat(system, _plan_user(state["brief"], facts, feedback),
                       num_predict=500, temperature=0.5)
        metrics.append(m)
        # Le plan passe au lint comme la prose : un token collé dans un beat
        # (« maisonly », observé au run du 2026-08-06) contamine ensuite le
        # brief de la scène, donc le prompt d'écriture. La réparation par Qwen
        # n'intervient qu'en fin de pipeline, bien trop tard pour un brief.
        text, w = delint(text)
        warnings.extend(f"plan (tentative {attempt}): {x}" for x in w)
        candidat = _parse_beats(text)
        # Un plan illisible n'est pas une violation : on garde le précédent
        # s'il existait, sinon on laisse la suite du graphe s'en apercevoir.
        if candidat:
            beats = candidat
        if not facts or not beats:
            break

        unload()  # nemo → Qwen pour la vérification
        violations, rapport, mv = check_plan(facts, beats)
        metrics.extend(mv)
        # Tracer la tentative : un plan refusé PUIS corrigé est le moment le
        # plus parlant du dispositif, et sans cette ligne le rapport final est
        # indiscernable d'un plan bon du premier coup.
        rapport = f"tentative {attempt}/{MAX_PLAN_ATTEMPTS} — {rapport}"
        if not violations or attempt == MAX_PLAN_ATTEMPTS:
            if violations:
                rapport += (
                    "\n  [replanification épuisée — le chapitre est écrit "
                    "malgré la contradiction, à arbitrer à la main]"
                )
            break
        warnings.append(
            f"plan (tentative {attempt}) refusé : "
            + "; ".join(f"contredit « {fait} »" for _, fait, _ in violations)
        )
        feedback = _plan_feedback(violations)
        unload(QA_MODEL)  # Qwen → nemo pour la reprise

    # L'écriture veut nemo seul : Qwen a pu rester chaud après la vérification.
    unload(QA_MODEL)
    return {
        "plan": beats, "facts": facts, "plan_report": rapport,
        "idx": 0, "scenes": [], "metrics": metrics, "warnings": warnings,
    }


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
    text, ms, wg = _generate_whole(system, user, num_predict=1400,
                                   temperature=0.7, label=f"scène {idx + 1}")
    text, w = delint(text)
    return {
        "scenes": state["scenes"] + [text],
        "idx": idx + 1,
        "metrics": state["metrics"] + ms,
        "warnings": state["warnings"] + wg
        + [f"scène {idx + 1}: {x}" for x in w],
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
        text, ms, wg = _generate_whole(system, user, num_predict=budget,
                                       temperature=0.5,
                                       label=f"relecture scène {i + 1}")
        metrics.extend(ms)
        warns.extend(wg)
        # Garde-fou anti-destruction : relecture trop courte -> on garde l'original.
        if len(text.split()) < 0.6 * len(scene.split()):
            text = scene
        text, w = delint(text)
        warns.extend(f"relecture scène {i + 1}: {x}" for x in w)
        reviewed.append(text)
    return {"reviewed": reviewed, "metrics": metrics, "warnings": warns}


def repair_node(state: ChapterState) -> dict:
    """Réparation linguistique (Qwen) : réécrit les fuites d'anglais laissées
    par nemo, phrase par phrase, sans toucher au sens ni au style.

    C'est ici qu'Ollama bascule du modèle auteur (nemo) au modèle QA (Qwen) —
    un seul swap pour toute la phase QA qui suit. On décharge nemo AVANT :
    nemo (13 GB) + Qwen (4,8 GB) chauds ensemble, c'est 17,8 GB sur 19,3 GB,
    exactement la pression mémoire qui a fait paniquer la machine. nemo n'a
    plus rien à produire à ce stade."""
    repaired: list[str] = []
    metrics = list(state["metrics"])
    warns = list(state["warnings"])
    if not unload():
        warns.append("QA : déchargement de nemo refusé par Ollama (co-résidence "
                     "nemo + Qwen, pression mémoire)")
    for i, scene in enumerate(state["reviewed"]):
        text, m = repair(scene)
        metrics.append(m)
        # Garde-fou : une réparation ne doit pas escamoter la scène.
        if len(text.split()) < 0.6 * len(scene.split()):
            text = scene
        # Re-lint pour tracer ce qui resterait (anglais tenace, tokens collés).
        text, w = delint(text)
        warns.extend(f"réparation scène {i + 1}: {x}" for x in w)
        repaired.append(text)
    return {"repaired": repaired, "metrics": metrics, "warnings": warns}


def coherence_node(state: ChapterState) -> dict:
    """Cohérence par FAITS (Qwen) : dérive les faits structurants des fiches,
    puis les vérifie SCÈNE PAR SCÈNE avant d'agréger.

    Le découpage par scène n'est pas cosmétique : sur le chapitre entier, Qwen
    bascule en critique d'atelier (suggestions, réécriture) et ne rend plus les
    verdicts. Sur une entrée courte, il tient le format. Et un fait n'est violé
    que si une scène le CONTREDIT — le non-mentionné n'est pas une faute.
    Les faits sont ceux DÉJÀ dérivés par le nœud de plan : mêmes invariants
    pour contraindre le plan et pour juger le résultat, sinon le rapport final
    sanctionnerait un chapitre au nom de règles que la planification n'a jamais
    reçues. Économie accessoire : un appel Qwen de moins.
    C'est la « strate 4 » finale montrée sur scène."""
    metrics = list(state["metrics"])

    facts = state.get("facts") or []
    if not facts:  # nœud de plan court-circuité (test unitaire, reprise)
        facts, mf = derive_facts(state["characters"])
        metrics.append(mf)
    if not facts:
        return {"coherence": "Aucun fait dérivé de la bible.", "metrics": metrics}

    rapport, mc = check_facts(facts, state["repaired"])
    metrics.extend(mc)
    return {"coherence": rapport, "metrics": metrics}


# --- Assemblage du graphe ----------------------------------------------------

def build_graph():
    g = StateGraph(ChapterState)
    g.add_node("plan", plan_node)
    g.add_node("write", write_node)
    g.add_node("review", review_node)
    g.add_node("repair", repair_node)
    g.add_node("coherence", coherence_node)

    g.add_edge(START, "plan")
    g.add_edge("plan", "write")
    g.add_conditional_edges("write", route_after_write, ["write", "review"])
    g.add_edge("review", "repair")
    g.add_edge("repair", "coherence")
    g.add_edge("coherence", END)
    return g.compile()
