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
from retrieval import world_context

QA_MODEL = os.environ.get("QA_MODEL", "qwen2.5:7b-instruct")

# Vocabulaire de PRODUCTION, interdit dans les faits dérivés (item 3).
VOCAB_PILOTAGE = re.compile(
    r"\b(verdict impos[ée]|relecture blanche|grade|ratio|chapitre\s*\d|"
    r"r[ée]gime\s*\d|marche des explications|objets actifs|chaleur|"
    r"table de pilotage|s[ée]ances)\b", re.IGNORECASE)

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


# --- Cohérence : faits → questions de violation → réponses par scène ---------
#
# Trois échecs successifs ont dessiné le protocole qui suit :
#
#   1. Vérifier les faits sur le CHAPITRE entier (~2000 mots) fait basculer
#      Qwen en critique d'atelier : il suggère des réécritures au lieu de
#      rendre des verdicts. → découper par SCÈNE (entrée courte).
#   2. Demander OUI/NON sur un fait range le « non mentionné » dans NON :
#      faux positifs sur presque tous les faits. → une étiquette ABSENT aide,
#      mais ne suffit pas.
#   3. Classer un fait ABSTRAIT (surtout négatif : « X ignore Y », « X n'avoue
#      jamais ») reste hors de portée d'un 7B : il a lu l'aveu complet de Kael
#      et l'a classé CONFORME au fait « Élara ignore ». C'est une tâche
#      d'inférence (entailment), pas de lecture.
#
# D'où le protocole retenu : on convertit d'abord chaque fait en QUESTION
# D'ÉVÉNEMENT dont la réponse OUI signale la violation (« Le texte montre-t-il
# Élara découvrant que… ? »). Répondre « ce texte montre-t-il X ? » est de la
# lecture, pas de l'inférence — un 7B y arrive. Chaque OUI doit être appuyé par
# une citation, vérifiée ensuite dans le texte par le code (garde-fou contre
# les citations paraphrasées ou recopiées depuis le fait lui-même).

_FACTS_SYS = (
    "Tu extrais des FAITS VÉRIFIABLES de fiches de personnages : ce que chaque "
    "personnage sait ou ignore, les faits établis du passé, les contraintes de "
    "caractère durables. Tu rends une liste, un fait par ligne, préfixé « - », "
    "sans commentaire. Maximum 6 faits, les plus structurants.\n\n"
    "N'EXTRAIS PAS ce qui a vocation à CHANGER pendant le chapitre : la "
    "position courante dans le récit (« vient d'arriver à… »), l'objectif "
    "immédiat, l'état émotionnel du moment. Ce ne sont pas des invariants : le "
    "chapitre est précisément là pour les faire évoluer.\n\n"
    "EXEMPLES à NE PAS extraire : « Marie vient d'arriver au village », "
    "« Marie cherche à ouvrir le coffre », « Marie est tendue ».\n"
    "EXEMPLES à extraire : « Marie ignore que Paul l'a trahie », « Marie a "
    "perdu sa sœur dans l'incendie », « Marie refuse toujours de porter une "
    "arme »."
)

_QUESTIONS_SYS = (
    "Tu transformes des FAITS d'une bible de roman en QUESTIONS de "
    "vérification. Pour chaque fait, écris UNE question fermée qui décrit "
    "l'ÉVÉNEMENT CONCRET qui violerait ce fait — une question à laquelle on "
    "répond OUI seulement si le texte MONTRE cet événement.\n"
    "Format : une ligne par fait, « n. <question> », rien d'autre.\n\n"
    "EXEMPLE —\nFAITS :\n1. Marie ignore que Paul ment.\n"
    "2. Paul n'avoue jamais directement sa faute.\n3. Il pleut sur la ville.\n"
    "RÉPONSE :\n"
    "1. Le texte montre-t-il Marie découvrant ou apprenant que Paul ment ?\n"
    "2. Le texte montre-t-il Paul avouant directement sa faute ?\n"
    "3. Le texte décrit-il un temps sec ou ensoleillé ?"
)

_ANSWER_SYS = (
    "Tu réponds à des questions de vérification sur un COURT EXTRAIT de roman. "
    "Tu n'es pas critique littéraire : aucun commentaire, aucune suggestion. "
    "Une ligne par question, format EXACT :\n"
    "Qn : OUI — « citation littérale de l'extrait »\n"
    "Qn : NON\n\n"
    "RÈGLES : réponds OUI uniquement si l'extrait MONTRE explicitement ce que "
    "décrit la question, ENTIÈREMENT — les personnes nommées dans la question "
    "doivent être celles de l'extrait, et l'événement doit être accompli, pas "
    "pressenti. Un indice, un soupçon, une découverte partielle, une allusion "
    "ou une menace = NON. Quand tu réponds OUI, recopie la phrase de l'extrait "
    "qui le montre. Dans tous les autres cas : NON, sans citation."
)

_CONFIRM_SYS = (
    "Tu es un vérificateur SÉVÈRE. On te donne une question et un extrait de "
    "roman. Tu réponds par UN SEUL MOT : OUI ou NON.\n"
    "OUI seulement si l'extrait montre l'événement ENTIER décrit par la "
    "question : les bonnes personnes, l'action accomplie, explicitement dans "
    "le texte. Un indice, un soupçon, une intention, une action seulement "
    "ressemblante : NON. En cas de doute : NON."
)

_ANSWER_RE = re.compile(r"Q\s*(\d+)\s*[:.\-–—]?\s*(OUI|NON)\b[\s:.\-–—]*(.*)", re.I)
# Citation exigée pour un OUI : « … », " … " ou “ … ”.
_QUOTE_RE = re.compile(r"[«\"“]\s*(.+?)\s*[»\"”]")



# FAITS DE MONDE NÉGATIFS (bloc D, étage C). La 5e configuration M4 de B′3 — la
# mémoire qui se RÉÉCRIT pour rejoindre le texte : un dîner fabriqué avec
# « elle », des rires, une présence — a traversé toute la chaîne sans détection.
# `coherence` a déclaré le fait « séparation définitive » TENU en face de « nous
# avons ri hier soir ».
#
# La raison est structurelle : les faits dérivés sont POSITIFS (ce qui est), et
# une question de violation bâtie sur un fait positif ne sait pas voir ce qui ne
# devrait pas être. Un fait négatif explicite se convertit, lui, en question
# d'événement dont le OUI vaut violation — exactement le protocole qui marche
# depuis la session 1.
FAITS_NEGATIFS = [
    "Personne d'autre n'entre dans la maison.",
    "Aucun repas n'est partagé, aucune conversation n'a lieu.",
    "Elle ne sort pas de la maison.",
]

def derive_facts(characters: list[str]) -> tuple[list[str], dict]:
    """Dérive les faits structurants depuis les fiches (fetch par id, no embed)."""
    ctx = "\n\n".join(world_context(c) for c in characters if world_context(c))
    text, m = chat(_FACTS_SYS, ctx, model=QA_MODEL, temperature=0.1,
                   num_predict=400)
    facts = [
        re.sub(r"^\s*[-*]\s*", "", line).strip()
        for line in text.splitlines()
        if line.strip().startswith(("-", "*"))
    ]
    # Filtre de PILOTAGE : un fait qui parle de la fabrication du chapitre
    # n'est pas un fait du monde. Servis au planificateur, ces pseudo-faits
    # l'ont fait raisonner en formulaire (mode constaté sur tout l'étage B).
    facts = [f for f in facts if f and not VOCAB_PILOTAGE.search(f)]
    # Les faits négatifs sont AJOUTÉS, jamais dérivés : un modèle qui résume des
    # fiches énonce ce qui est, pas ce qui est exclu.
    return facts + FAITS_NEGATIFS, m


def _parse_questions(text: str, questions: list[str], indices: list[int]) -> None:
    """Range les lignes « n. question » dans `questions` (numérotation locale
    du prompt → indices réels passés dans `indices`). Modifie en place."""
    for line in text.splitlines():
        hit = re.match(r"\s*(\d+)\s*[.)]\s*(.+)", line)
        if not hit:
            continue
        pos = int(hit.group(1)) - 1
        if 0 <= pos < len(indices) and not questions[indices[pos]]:
            questions[indices[pos]] = hit.group(2).strip()


def derive_questions(facts: list[str]) -> tuple[list[str], list[dict]]:
    """Convertit chaque fait en question dont le OUI vaut violation.

    Retourne une liste alignée sur `facts`. Le modèle saute parfois un fait en
    fin de liste : on repasse une fois sur les manquants (appel court) plutôt
    que de laisser un fait sans vérification.
    """
    metrics: list[dict] = []
    questions = [""] * len(facts)
    indices = list(range(len(facts)))
    numbered = "\n".join(f"{i + 1}. {facts[i]}" for i in indices)
    text, m = chat(_QUESTIONS_SYS, f"FAITS :\n{numbered}", model=QA_MODEL,
                   temperature=0.1, num_predict=500)
    metrics.append(m)
    _parse_questions(text, questions, indices)

    manquants = [i for i, q in enumerate(questions) if not q]
    if manquants:
        numbered = "\n".join(f"{k + 1}. {facts[i]}" for k, i in enumerate(manquants))
        text, m = chat(_QUESTIONS_SYS, f"FAITS :\n{numbered}", model=QA_MODEL,
                       temperature=0.1, num_predict=300)
        metrics.append(m)
        _parse_questions(text, questions, manquants)
    return questions, metrics


def _norm(s: str) -> str:
    """Normalise pour comparer une citation au texte source."""
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip().lower()


def _sourced(detail: str, scene: str) -> str | None:
    """Retourne la citation SI elle figure vraiment dans la scène, sinon None.

    Garde-fou programmatique : le modèle recopie parfois le fait au lieu du
    texte, ou paraphrase. Un signalement non sourcé n'est pas une violation.
    """
    q = _QUOTE_RE.search(detail)
    if not q:
        return None
    frag = q.group(1).strip()
    if len(frag) < 12:          # citation trop courte = non discriminante
        return None
    return frag if _norm(frag)[:60] in _norm(scene) else None


def _ask(questions: list[str], texte: str, system: str, label: str) -> tuple[dict[int, str], dict]:
    """Pose le questionnaire de violation contre UN texte court.

    Retourne {n° de question: citation brute} pour les seuls OUI — dict vide
    si le texte est propre OU si le vérificateur a dérivé (distingué par
    l'appelant via la métrique `repondues`).
    """
    posees = [(i + 1, q) for i, q in enumerate(questions) if q]
    qblock = "\n".join(f"Q{n} : {q}" for n, q in posees)
    user = f"QUESTIONS :\n{qblock}\n\n--- {label} ---\n{texte}"
    text, m = chat(system, user, model=QA_MODEL, temperature=0.0,
                   num_predict=400)
    hits: dict[int, str] = {}
    repondues: set[int] = set()
    for line in text.splitlines():
        hit = _ANSWER_RE.search(line)
        if not hit:
            continue
        n = int(hit.group(1))
        if n in repondues:
            continue
        repondues.add(n)
        if hit.group(2).upper() == "OUI":
            hits[n] = hit.group(3).strip()
    m["repondues"] = len(repondues)
    return hits, m


def check_scene(questions: list[str], scene: str) -> tuple[dict[int, str], dict]:
    """Répond aux questions de violation contre UNE scène de prose."""
    return _ask(questions, scene, _ANSWER_SYS, "EXTRAIT")


def _confirm(question: str, texte: str,
             system: str = _CONFIRM_SYS) -> tuple[bool, dict]:
    """Contre-appel sur un OUI : une seule question, réponse en un mot.

    Le questionnaire groupé dilue l'attention et produit des OUI complaisants
    (« comptant mentalement les pierres » lu comme une délégation de tâche).
    Reposée seule et en mode sévère, la même question est tranchée nettement.
    Un OUI non confirmé n'est pas une violation.
    """
    user = f"QUESTION : {question}\n\n--- EXTRAIT ---\n{texte}"
    text, m = chat(system, user, model=QA_MODEL, temperature=0.0,
                   num_predict=8)
    return bool(re.search(r"\bOUI\b", text, re.I)), m


def check_facts(facts: list[str], scenes: list[str]) -> tuple[str, list[dict]]:
    """Vérifie les faits scène par scène et agrège en un rapport de chapitre.

    Un fait est CONTREDIT dès qu'une scène montre l'événement de violation AVEC
    une citation retrouvée dans le texte. Les OUI non sourcés sont relégués en
    signalements à vérifier à la main ; les scènes où le vérificateur n'a rien
    rendu d'exploitable sont listées plutôt que comptées comme propres.
    """
    metrics: list[dict] = []
    questions, mq = derive_questions(facts)
    metrics.extend(mq)
    if not any(questions):
        return "Aucune question de vérification dérivée des faits.", metrics

    violations: dict[int, list[tuple[int, str]]] = {}
    doutes: list[str] = []
    muettes: list[int] = []

    for i, scene in enumerate(scenes, 1):
        hits, m = check_scene(questions, scene)
        metrics.append(m)
        if not m.get("repondues"):
            muettes.append(i)
            continue
        for n, detail in hits.items():
            citation = _sourced(detail, scene)
            if not citation:
                doutes.append(f"    fait {n}, scène {i} : "
                              f"{detail or '(OUI sans citation)'} "
                              f"[citation introuvable dans la scène]")
                continue
            confirme, mc = _confirm(questions[n - 1], scene)
            metrics.append(mc)
            if confirme:
                violations.setdefault(n, []).append((i, citation))
            else:
                doutes.append(f"    fait {n}, scène {i} : « {citation} » "
                              f"[non confirmé au contre-appel]")

    lignes: list[str] = []
    for n, fait in enumerate(facts, 1):
        if not questions[n - 1]:
            lignes.append(f"FAIT {n} : NON VÉRIFIÉ (pas de question) — {fait}")
        elif n in violations:
            ou = ", ".join(f"scène {i}" for i, _ in violations[n])
            lignes.append(f"FAIT {n} : CONTREDIT ({ou}) — {fait}")
            lignes.extend(f"    → scène {i} : « {c} »" for i, c in violations[n])
        else:
            lignes.append(f"FAIT {n} : tenu — {fait}")

    if doutes:
        lignes.append("")
        lignes.append("[signalements écartés faute de citation vérifiable :]")
        lignes.extend(doutes)
    if muettes:
        lignes.append("")
        lignes.append("[scènes sans réponse exploitable (dérive du "
                      "vérificateur) : "
                      + ", ".join(str(i) for i in muettes) + "]")
    return "\n".join(lignes), metrics


# --- Vérification du PLAN, AVANT d'écrire -------------------------------------
#
# La cohérence par faits arrive après la rédaction : elle CONSTATE, elle ne
# prévient pas. Or un plan qui contredit la bible condamne d'avance les quatorze
# minutes d'écriture qui suivent — et sur scène, on ne réécrit pas.
#
# Constaté au run du 2026-08-06 : le plan a programmé « Élara découvre les
# détournements de Kael » alors qu'un fait de la bible dit « Kael redoute
# qu'Élara découvre les registres ». Formulé comme une crainte de Kael, le fait
# n'était pas techniquement violé et le rapport final a validé — un coup de
# chance de formulation, pas un filet.
#
# Le protocole est le même que pour les scènes (faits → questions de violation
# → LECTURE), appliqué à un texte de quatre lignes : deux appels Qwen, quelques
# secondes. La différence tient au régime du texte lu : un plan ANNONCE des
# événements, il ne les met pas en scène. « Le texte montre-t-il… » devient
# « le plan prévoit-il… ».

_PLAN_ANSWER_SYS = (
    "Tu lis un PLAN DE CHAPITRE : une ligne par scène, chacune résumant les "
    "événements PRÉVUS. Tu n'es pas critique littéraire : aucun commentaire, "
    "aucune suggestion. Une ligne par question, format EXACT :\n"
    "Qn : OUI — « citation littérale d'une ligne du plan »\n"
    "Qn : NON\n\n"
    "RÈGLES : réponds OUI uniquement si une ligne du plan PRÉVOIT "
    "explicitement l'événement décrit par la question, avec les personnes "
    "nommées dans la question. Un événement seulement possible, sous-entendu, "
    "ou simplement ressemblant = NON. Quand tu réponds OUI, recopie la ligne "
    "du plan. Dans tous les autres cas : NON, sans citation."
)

_CONFIRM_PLAN_SYS = (
    "Tu es un vérificateur SÉVÈRE. On te donne une question et un plan de "
    "chapitre. Tu réponds par UN SEUL MOT : OUI ou NON.\n"
    "OUI seulement si le plan prévoit explicitement l'événement ENTIER décrit "
    "par la question : les bonnes personnes, l'action annoncée noir sur blanc. "
    "Un sous-entendu, une possibilité, une action ressemblante : NON. En cas "
    "de doute : NON."
)


def check_plan(facts: list[str],
               beats: list[str]) -> tuple[list[tuple[int, str, str]], str, list[dict]]:
    """Confronte un plan de scènes aux faits de la bible AVANT rédaction.

    Retourne (violations, rapport, métriques) où chaque violation est
    (n° de fait, fait, ligne du plan fautive). Les mêmes garde-fous que sur la
    prose s'appliquent — citation retrouvée dans le plan, puis contre-appel
    sévère : un plan légitime qui « ressemble » à une violation ne doit pas
    déclencher une replanification, elle coûte un rechargement de nemo.
    """
    metrics: list[dict] = []
    if not facts or not beats:
        return [], "Plan non vérifié (pas de faits ou pas de plan).", metrics

    questions, mq = derive_questions(facts)
    metrics.extend(mq)
    if not any(questions):
        return [], "Plan non vérifié (aucune question dérivée des faits).", metrics

    plan_txt = "\n".join(f"{i + 1}. {b}" for i, b in enumerate(beats))
    hits, m = _ask(questions, plan_txt, _PLAN_ANSWER_SYS, "PLAN")
    metrics.append(m)
    if not m.get("repondues"):
        return [], "Plan non vérifié (le vérificateur a dérivé).", metrics

    violations: list[tuple[int, str, str]] = []
    doutes: list[str] = []
    for n, detail in hits.items():
        if not 1 <= n <= len(facts):
            continue
        citation = _sourced(detail, plan_txt)
        if not citation:
            doutes.append(f"    fait {n} : {detail or '(OUI sans citation)'} "
                          "[citation introuvable dans le plan]")
            continue
        confirme, mc = _confirm(questions[n - 1], plan_txt, _CONFIRM_PLAN_SYS)
        metrics.append(mc)
        if confirme:
            violations.append((n, facts[n - 1], citation))
        else:
            doutes.append(f"    fait {n} : « {citation} » "
                          "[non confirmé au contre-appel]")

    lignes = [f"{len(facts)} faits confrontés au plan."]
    for n, fait, citation in violations:
        lignes.append(f"  PLAN CONTREDIT le fait {n} — {fait}")
        lignes.append(f"    → « {citation} »")
    if not violations:
        lignes.append("  aucune contradiction : le plan respecte la bible.")
    if doutes:
        lignes.append("  [signalements écartés :]")
        lignes.extend(doutes)
    return violations, "\n".join(lignes), metrics
