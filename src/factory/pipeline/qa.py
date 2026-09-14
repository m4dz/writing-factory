#!/usr/bin/env python3
"""QA/lint role — a model distinct from the author model (LOCAL).

Settled at the benchmark (ADR-0008): Qwen 2.5 7B for the tasks where nemo
fails in creative generation — rewriting English leaks, checking coherence
in a strict format. Qwen is of another lineage (no leak tendency), fast
(~28 tok/s), disciplined in format.

This phase runs AFTER all generation: Ollama swaps nemo → Qwen once. No
embedding here (fact derivation reads the sheets by deterministic id, not by
similarity), so nomic-embed is never recalled.
"""

import re

from factory.infra.ollama import chat
from factory.retrieval.context import world_context
from factory.settings import settings

# PRODUCTION vocabulary, forbidden in derived facts (item 3).
PILOT_VOCAB = re.compile(
    r"\b(verdict impos[ée]|relecture blanche|grade|ratio|chapitre\s*\d|"
    r"r[ée]gime\s*\d|marche des explications|objets actifs|chaleur|"
    r"table de pilotage|s[ée]ances)\b", re.IGNORECASE)

# --- Language repair ---------------------------------------------------------

_REPAIR_SYS = (
    "Tu es correcteur linguistique. Tu réécris le texte en français en "
    "corrigeant TOUT passage qui n'est pas en français (mot ou phrase). Tu ne "
    "changes NI le sens, NI le style, NI l'ordre, NI la ponctuation des "
    "dialogues. Tu rends UNIQUEMENT le texte corrigé, rien d'autre."
)


def repair(text: str) -> tuple[str, dict]:
    """Rewrite a passage, fixing language leaks (text→text)."""
    # Margin: the FR version may be slightly longer than the original.
    budget = min(2000, max(600, int(len(text) / 3) + 200))
    return chat(_REPAIR_SYS, text, model=settings.qa_model, temperature=0.2,
                num_predict=budget)


# --- Coherence: facts → violation questions → per-scene answers --------------
#
# Protocol recorded in ADR-0010. Three failures shaped it: checking the whole
# chapter (~2000 words) turns Qwen into a workshop critic; a YES/NO per fact
# files « non mentionné » under NON; classifying an abstract, negative fact
# (« X ignore Y ») is entailment, beyond a 7B — it read Kael's full confession
# and classed it CONFORME to « Élara ignore ».
#
# Hence: each fact becomes an EVENT question whose OUI signals the violation
# (« Le texte montre-t-il Élara découvrant que… ? »). Answering « does this
# text show X? » is reading, not inference — a 7B manages it. Each OUI must
# carry a citation, then verified in the text by the code (guard against
# paraphrased citations or ones copied from the fact itself).

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
# Citation required with a OUI: « … », " … " or “ … ”.
_QUOTE_RE = re.compile(r"[«\"“]\s*(.+?)\s*[»\"”]")



# NEGATIVE WORLD FACTS (block D, stage C). The 5th M4 configuration of B′3 —
# memory REWRITING itself to join the text: a fabricated dinner with « elle »,
# laughter, a presence — crossed the whole chain undetected. `coherence`
# declared the fact « séparation définitive » HELD against
# « nous avons ri hier soir ».
#
# The reason is structural: derived facts are POSITIVE (what is), and a
# violation question built from a positive fact cannot see what should not
# be. An explicit negative fact converts into an event question whose OUI is
# a violation — the protocol that has worked since session 1 (ADR-0010).
NEGATIVE_FACTS = [
    "Personne d'autre n'entre dans la maison.",
    "Aucun repas n'est partagé, aucune conversation n'a lieu.",
    "Elle ne sort pas de la maison.",
]

def derive_facts(characters: list[str]) -> tuple[list[str], dict]:
    """Derive the structuring facts from the sheets (fetch by id, no embed)."""
    ctx = "\n\n".join(world_context(c) for c in characters if world_context(c))
    text, m = chat(_FACTS_SYS, ctx, model=settings.qa_model, temperature=0.1,
                   num_predict=400)
    facts = [
        re.sub(r"^\s*[-*]\s*", "", line).strip()
        for line in text.splitlines()
        if line.strip().startswith(("-", "*"))
    ]
    # PILOT filter: a fact about the chapter's manufacture is not a world fact.
    # Served to the planner, these pseudo-facts made it reason as a form
    # (mode observed across stage B).
    facts = [f for f in facts if f and not PILOT_VOCAB.search(f)]
    # Negative facts are ADDED, never derived: a model summarising sheets
    # states what is, not what is excluded (ADR-0010).
    return facts + NEGATIVE_FACTS, m


def _parse_questions(text: str, questions: list[str], indices: list[int]) -> None:
    """Store the « n. question » lines into `questions` (local prompt numbering
    → real indices passed in `indices`). Mutates in place."""
    for line in text.splitlines():
        hit = re.match(r"\s*(\d+)\s*[.)]\s*(.+)", line)
        if not hit:
            continue
        pos = int(hit.group(1)) - 1
        if 0 <= pos < len(indices) and not questions[indices[pos]]:
            questions[indices[pos]] = hit.group(2).strip()


def derive_questions(facts: list[str]) -> tuple[list[str], list[dict]]:
    """Convert each fact into a question whose OUI means violation.

    Returns a list aligned with `facts`. The model sometimes skips a fact at
    the end of the list: one more pass over the missing ones (short call)
    rather than leaving a fact unchecked.
    """
    metrics: list[dict] = []
    questions = [""] * len(facts)
    indices = list(range(len(facts)))
    numbered = "\n".join(f"{i + 1}. {facts[i]}" for i in indices)
    text, m = chat(_QUESTIONS_SYS, f"FAITS :\n{numbered}", model=settings.qa_model,
                   temperature=0.1, num_predict=500)
    metrics.append(m)
    _parse_questions(text, questions, indices)

    missing = [i for i, q in enumerate(questions) if not q]
    if missing:
        numbered = "\n".join(f"{k + 1}. {facts[i]}" for k, i in enumerate(missing))
        text, m = chat(_QUESTIONS_SYS, f"FAITS :\n{numbered}", model=settings.qa_model,
                       temperature=0.1, num_predict=300)
        metrics.append(m)
        _parse_questions(text, questions, missing)
    return questions, metrics


def _norm(s: str) -> str:
    """Normalise to compare a citation with the source text."""
    return re.sub(r"\s+", " ", s.replace("’", "'""'")).strip().lower()


def _sourced(detail: str, scene: str) -> str | None:
    """Return the citation IF it really appears in the scene, else None.

    Programmatic guard: the model sometimes copies the fact instead of the
    text, or paraphrases. An unsourced finding is not a violation (ADR-0010).
    """
    q = _QUOTE_RE.search(detail)
    if not q:
        return None
    frag = q.group(1).strip()
    if len(frag) < 12:          # too short a citation discriminates nothing
        return None
    return frag if _norm(frag)[:60] in _norm(scene) else None


def _ask(questions: list[str], excerpt: str, system: str, label: str) -> tuple[dict[int, str], dict]:
    """Ask the violation questionnaire against ONE short text.

    Returns {question number: raw citation} for the OUI answers only — empty
    dict when the text is clean OR the checker drifted (the caller tells them
    apart through the `repondues` metric).
    """
    asked = [(i + 1, q) for i, q in enumerate(questions) if q]
    qblock = "\n".join(f"Q{n} : {q}" for n, q in asked)
    user = f"QUESTIONS :\n{qblock}\n\n--- {label} ---\n{excerpt}"
    text, m = chat(system, user, model=settings.qa_model, temperature=0.0,
                   num_predict=400)
    hits: dict[int, str] = {}
    answered: set[int] = set()
    for line in text.splitlines():
        hit = _ANSWER_RE.search(line)
        if not hit:
            continue
        n = int(hit.group(1))
        if n in answered:
            continue
        answered.add(n)
        if hit.group(2).upper() == "OUI":
            hits[n] = hit.group(3).strip()
    m["repondues"] = len(answered)
    return hits, m


def check_scene(questions: list[str], scene: str) -> tuple[dict[int, str], dict]:
    """Answer the violation questions against ONE prose scene."""
    return _ask(questions, scene, _ANSWER_SYS, "EXTRAIT")


def _confirm(question: str, excerpt: str,
             system: str = _CONFIRM_SYS) -> tuple[bool, dict]:
    """Counter-call upon a OUI: a single question, one-word answer.

    The grouped questionnaire dilutes attention and yields complacent OUIs
    (« comptant mentalement les pierres » read as delegating a task). Asked
    alone in severe mode, the same question is settled cleanly. An unconfirmed
    OUI is not a violation (ADR-0010).
    """
    user = f"QUESTION : {question}\n\n--- EXTRAIT ---\n{excerpt}"
    text, m = chat(system, user, model=settings.qa_model, temperature=0.0,
                   num_predict=8)
    return bool(re.search(r"\bOUI\b", text, re.I)), m


def check_facts(facts: list[str], scenes: list[str]) -> tuple[str, list[dict]]:
    """Check the facts scene by scene and aggregate into a chapter report.

    A fact is CONTRADICTED as soon as a scene shows the violation event WITH
    a citation found in the text. Unsourced OUIs are demoted to findings to
    check by hand; scenes where the checker returned nothing usable are
    listed rather than counted as clean.
    """
    metrics: list[dict] = []
    questions, mq = derive_questions(facts)
    metrics.extend(mq)
    if not any(questions):
        return "Aucune question de vérification dérivée des faits.", metrics

    violations: dict[int, list[tuple[int, str]]] = {}
    doubts: list[str] = []
    silent: list[int] = []

    for i, scene in enumerate(scenes, 1):
        hits, m = check_scene(questions, scene)
        metrics.append(m)
        if not m.get("repondues"):
            silent.append(i)
            continue
        for n, detail in hits.items():
            quotation = _sourced(detail, scene)
            if not quotation:
                doubts.append(f"    fait {n}, scène {i} : "
                              f"{detail or '(OUI sans citation)'} "
                              f"[citation introuvable dans la scène]")
                continue
            confirmed, mc = _confirm(questions[n - 1], scene)
            metrics.append(mc)
            if confirmed:
                violations.setdefault(n, []).append((i, quotation))
            else:
                doubts.append(f"    fait {n}, scène {i} : « {quotation} » "
                              f"[non confirmé au contre-appel]")

    lines: list[str] = []
    for n, fact in enumerate(facts, 1):
        if not questions[n - 1]:
            lines.append(f"FAIT {n} : NON VÉRIFIÉ (pas de question) — {fact}")
        elif n in violations:
            where_txt = ", ".join(f"scène {i}" for i, _ in violations[n])
            lines.append(f"FAIT {n} : CONTREDIT ({where_txt}) — {fact}")
            lines.extend(f"    → scène {i} : « {c} »" for i, c in violations[n])
        else:
            lines.append(f"FAIT {n} : tenu — {fact}")

    if doubts:
        lines.append("")
        lines.append("[signalements écartés faute de citation vérifiable :]")
        lines.extend(doubts)
    if silent:
        lines.append("")
        lines.append("[scènes sans réponse exploitable (dérive du "
                      "vérificateur) : "
                      + ", ".join(str(i) for i in silent) + "]")
    return "\n".join(lines), metrics


# --- Checking the PLAN, BEFORE writing ---------------------------------------
#
# Fact coherence comes after writing: it OBSERVES, it does not prevent. A
# plan contradicting the bible condemns in advance the fourteen minutes of
# writing that follow — and onstage nothing gets rewritten.
#
# Seen at the 2026-08-06 run: the plan scheduled
# « Élara découvre les détournements de Kael » while a bible fact says
# « Kael redoute qu'Élara découvre les registres ». Phrased as Kael's fear,
# the fact was not technically violated and the final report passed — luck of
# wording, not a net.
#
# Same protocol as for scenes (facts → violation questions → READING), applied
# to a four-line text: two Qwen calls, a few seconds. The difference is the
# regime of the text read: a plan ANNOUNCES events, it does not stage them.
# « Le texte montre-t-il… » becomes « le plan prévoit-il… » (ADR-0010).

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
    """Confront a scene plan with the bible facts BEFORE writing.

    Returns (violations, report, metrics), each violation being (fact number,
    fact, offending plan line). The same guards as for prose apply — citation
    found in the plan, then severe counter-call: a legitimate plan that merely
    resembles a violation must not trigger a replan, which costs a reload of
    nemo.
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
    doubts: list[str] = []
    for n, detail in hits.items():
        if not 1 <= n <= len(facts):
            continue
        quotation = _sourced(detail, plan_txt)
        if not quotation:
            doubts.append(f"    fait {n} : {detail or '(OUI sans citation)'} "
                          "[citation introuvable dans le plan]")
            continue
        confirmed, mc = _confirm(questions[n - 1], plan_txt, _CONFIRM_PLAN_SYS)
        metrics.append(mc)
        if confirmed:
            violations.append((n, facts[n - 1], quotation))
        else:
            doubts.append(f"    fait {n} : « {quotation} » "
                          "[non confirmé au contre-appel]")

    lines = [f"{len(facts)} faits confrontés au plan."]
    for n, fact, quotation in violations:
        lines.append(f"  PLAN CONTREDIT le fait {n} — {fact}")
        lines.append(f"    → « {quotation} »")
    if not violations:
        lines.append("  aucune contradiction : le plan respecte la bible.")
    if doubts:
        lines.append("  [signalements écartés :]")
        lines.extend(doubts)
    return violations, "\n".join(lines), metrics
