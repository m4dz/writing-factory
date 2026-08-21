#!/usr/bin/env python3
"""Orchestrateur « mode auteur » (LangGraph).

Pipeline montré sur scène (strate 4 du talk) :

    plan d'entrées → écriture entrée par entrée → relecture → cohérence

C'est un graphe SÉQUENTIEL avec une boucle sur les entrées. Le contrôle de
flux est déterministe (LangGraph), la créativité est déléguée au modèle à
chaque nœud. Le contexte est ré-assemblé depuis la bible à chaque entrée
(RAG dynamique, cf. retrieval.py), jamais figé.

L'unité de composition est l'ENTRÉE DATÉE de carnet : L'Involontaire est un
journal, et les quotas de la fiche de style se comptent par entrée. Le champ
`rag` de l'état commande le branchement du retrieval — c'est l'unique variable
qui sépare les deux étages de la session 4, et elle vit dans l'état pour qu'on
ne puisse pas la changer par mégarde entre deux runs.
"""

import difflib
import os
import re
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

import progress
from llm import AUTHOR_MODEL, chat, unload
from retrieval import STYLE_RELECTURE, assemble_system_prompt
from style import delint, ends_mid_sentence, trim_to_sentence
from qa import QA_MODEL, repair, derive_facts, check_facts, check_plan
from gestes import (approche_valide, assembler, composer_glissement,
                    valider_accumulation)

# Modèle des micro-nœuds. nemo par défaut, et non Qwen : les nœuds tournent DANS
# la boucle d'écriture, nemo chaud — un appel Qwen y coûterait deux bascules par
# entrée (mesurées à 139-222 s dans `plan_node` en session 4). Surtout,
# `accumulate` écrit le marqueur le plus audible du style et sa phrase reste
# dans le chapitre : c'est de la voix, pas de la QA. Paramétrable pour que
# l'alternative reste mesurable en un run.
MODELE_GESTES = os.environ.get("MODELE_GESTES", AUTHOR_MODEL)
TEMP_GESTES = float(os.environ.get("TEMP_GESTES", "0.3"))

# L'unité de composition est l'ENTRÉE DATÉE de carnet, plus la scène. Le roman
# est un journal : ce que le plan découpe, ce sont des soirs. Les quotas de la
# fiche (accumulation, physiologie, couperet) se comptent par entrée — les
# laisser sur « scène » ferait compter la machine et la grille sur des unités
# différentes.
MOTS_PAR_ENTREE = (450, 600)

# Une seule reprise du plan. La replanification coûte un rechargement de nemo
# (13 GB) : au-delà, on perdrait plus de temps de scène qu'on n'en sauverait, et
# un modèle qui rate deux fois la contrainte ne la comprendra pas à la troisième.
MAX_PLAN_ATTEMPTS = 2

# Une seule continuation par génération coupée. Monter `num_predict` ne résout
# rien — un modèle qui n'a pas fini à 1400 tokens remplira aussi bien 1800 :
# il occupe l'espace offert. La continuation, elle, ne coûte que quand le cas
# se produit (une scène sur quatre au run du 2026-08-06, ~50 s).
MAX_CONTINUATIONS = 1

# Deux tentatives pour l'accumulation, comme le protocole le fixe.
MAX_TENTATIVES_GESTE = 2


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
    rag: bool             # étage A (False) ou B (True) — l'unique variable
    entrees_attendues: int  # 1 = brief mono-entrée, le plan est court-circuité
    prefixe: str          # ancre de citation, POSÉE PAR LE CODE (item 5)
    jour_depart: str      # « Mardi » — ancre de la séquence d'en-têtes
    numero_depart: int    # 12 — les dates suivantes se dérivent, consécutives
    micro_noeuds: bool    # étage C : accumulate + glisse actifs
    objets_actifs: str    # matériau du chapitre, source du fait matériel
    verdict: str          # terme du chapitre — REPÈRE d'épissure de l'accumulation
    meteo_depart: str     # météo de la 1re entrée, quand le plan est court-circuité
    accumulation: str     # phrase produite par accumulate, mise de côté
    gestes: list[dict]    # un jeu de gestes par entrée, posé après repair


# --- Nœuds -------------------------------------------------------------------


# --- En-têtes composés par le CODE (bloc B) ---------------------------------
#
# Le plan n'émet plus de texte d'en-tête. B′C avait produit « Lundi 2, nuageux. »
# — virgule au lieu du point : détection cassée, et avec elle le point de
# bascule audio de `lire_chapitre.py`. Un format que la scène dépend de ne se
# demande pas à un modèle, il se compose.
#
# Les DATES ne sont même pas demandées : elles se DÉRIVENT d'une ancre (jour de
# semaine + numéro de départ, donnés par le brief). B′C avait produit
# [8, 7, 7, 7, 7, 9, 10, 7] — des dates qui reculent et se répètent. Dérivées,
# elles sont consécutives par construction, et la cohérence jour ↔ date que le
# lint vérifie devient vraie par construction plutôt que par chance.
#
# Seule la MÉTÉO vient du plan : la coder en dur ferait revenir le même temps à
# chaque run, et on remplacerait une liturgie par une autre.
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
                 "Dimanche"]


def entete(jour_depart: str, numero_depart: int, decalage: int,
           meteo: str) -> str:
    """« Mardi 12. Ciel couvert. » — format canonique, composé, jamais demandé."""
    i = JOURS_SEMAINE.index(jour_depart.capitalize())
    jour = JOURS_SEMAINE[(i + decalage) % 7]
    meteo = (meteo or "Temps calme").strip().rstrip(".")
    return f"{jour} {numero_depart + decalage}. {meteo[0].upper()}{meteo[1:]}."


# La météo demandée au plan, en champ isolé : `1. [Ciel couvert] ce qu'elle…`
METEO_DU_BEAT = re.compile(r"^\s*\[([^\]]{2,40})\]\s*(.*)$")

# Un en-tête daté émis PAR LE MODÈLE, où que ce soit dans sa génération. Le code
# est propriétaire du format : il en compose un par entrée, donc tout en-tête
# produit par le modèle est parasite par définition. C1 en a inventé un second
# (« Vendredi 15. Pluie fine. ») dans une entrée censée être unique, et le lint
# découpait deux entrées là où il n'y en avait qu'une.
ENTETE_PARASITE = re.compile(
    r"^[ \t]*(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)[ \t]+"
    r"\d{1,2}[.,][^\n]{0,40}\n+", re.MULTILINE | re.IGNORECASE)

# Les POINTS DE SUSPENSION du modèle. La fiche est explicite : ils n'existent
# nulle part ailleurs que comme marque du glissement — « c'est leur seul
# emploi ». Le code est propriétaire de ce marqueur comme il l'est des en-têtes,
# donc tout « … » produit par le modèle est parasite par la même logique. Sur
# C2, les DEUX occurrences venaient de lui (« une, deux, trois... trois
# assiettes », « depuis... depuis qu'elle est partie ») alors que le geste
# composé avait été abandonné : M1 tombait à 2 sans qu'un seul glissement
# existe. On les remplace par la ponctuation que le contexte demande.
# Deux formes, dans cet ordre. Le marqueur PORTAIT souvent une répétition
# (« depuis… depuis son départ », « trois… trois assiettes ») : le retirer seul
# laissait le mot doublé, donc du texte cassé à la place d'un défaut de style.
# On absorbe donc la répétition avec lui, et à défaut on retombe sur une virgule
# — la ponctuation que l'hésitation demandait.
SUSPENSION_REPETEE = re.compile(
    r"\b(\w+)\s*(?:…|\.\.\.)\s*\1\b", re.IGNORECASE)
SUSPENSION_PARASITE = re.compile(r"\s*(?:…|\.\.\.)\s*")


def separer_meteo(beat: str) -> tuple[str, str]:
    """Sépare la météo du corps du beat. Rend ('', beat) si absente."""
    m = METEO_DU_BEAT.match(beat)
    return (m.group(1).strip(), m.group(2).strip()) if m else ("", beat)


def _tag(metrics: list[dict], noeud: str) -> list[dict]:
    """Étiquette des métriques du nœud qui les a produites.

    Le livrable de session demande les durées PAR NŒUD — c'est sur elles que se
    calcule la marge des 28 minutes de la keynote. Sans étiquette, la liste des
    appels ne dit que le total, et un nœud qui dérape reste invisible.
    """
    for m in metrics:
        m.setdefault("noeud", noeud)
    return metrics


def _retirer_reprise_approximative(prefixe: str, suite: str) -> str:
    """Retire du début de `suite` une reprise APPROXIMATIVE du préfixe.

    `_recoller` ne sait retirer qu'un chevauchement EXACT. Or le défaut mesuré
    en B′1 n'est pas une recopie, c'est une RECOMPOSITION : « Je les ai
    laissées » pour « Je l'ai laissée ». Sans ce filtre, la concaténation rend
    l'ancre juste du préfixe SUIVIE de la version fautive du modèle — un
    doublon, dont l'une des deux moitiés est fausse.

    On compare le premier passage cité de la suite au dernier passage cité du
    préfixe : au-delà de 70 % de similarité, c'est la même phrase mal recopiée.
    """
    debut = suite.lstrip()
    # L'EN-TÊTE d'abord. Le modèle réémet son propre « Mardi 12. Ciel
    # couvert. » — le brief le lui demandait encore — et le préfixe du code
    # venait s'ajouter devant : deux en-têtes, deux ancres. Le filtre ne
    # regardait que le passage cité.
    for _ in range(2):
        m_tete = re.match(
            r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d{1,2}[.,]"
            r"[^\n]{0,40}\n+", debut, re.IGNORECASE)
        if not m_tete:
            break
        debut = debut[m_tete.end():].lstrip()
    suite = debut

    cites_prefixe = re.findall(r"[«\"][^»\"]{20,}[»\"]", prefixe)
    if not cites_prefixe:
        return suite
    ancre = cites_prefixe[-1]
    m = re.match(r"[«\"][^»\"]{20,}[»\"]", debut)
    if not m:
        return suite
    ratio = difflib.SequenceMatcher(None, m.group(0), ancre).ratio()
    return debut[m.end():].lstrip() if ratio > 0.70 else suite


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
    text, m = chat(system, user, num_predict=num_predict, temperature=temperature,
                   on_token=progress.token_sink())
    metrics = [m]
    warns: list[str] = []

    for _ in range(MAX_CONTINUATIONS):
        if m.get("done_reason") != "length":
            break
        progress.note(f"{label} : génération coupée à {num_predict} tokens, "
                      "continuation demandée")
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
                        temperature=temperature, on_token=progress.token_sink())
        metrics.append(m)
        text = _recoller(text, suite)
        warns.append(f"{label} : génération coupée, continuation demandée")

    if ends_mid_sentence(text):
        coupe = trim_to_sentence(text)
        if coupe != text:
            # Dire CE QU'ON RETIRE, pas seulement qu'on a retiré. Au run du
            # 2026-08-06, le filet a tiré sur deux scènes dont aucune n'avait
            # été coupée par `num_predict` (nemo émet parfois son EOS en pleine
            # phrase) : sans l'extrait, impossible de distinguer un fragment
            # pendant légitimement supprimé d'une vraie fin de scène mal
            # reconnue par la détection de ponctuation.
            retire = text[len(coupe):].strip()
            warns.append(
                f"{label} : fin coupée à la dernière phrase complète, "
                f"{len(retire)} caractères retirés — « {retire[:80]} »"
            )
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
    # La consigne de format ouvre ET ferme le prompt. Au premier essai elle
    # n'était qu'en fin de message, derrière un brief long et très détaillé :
    # nemo a RÉDIGÉ le chapitre au lieu de le planifier — trois entrées de
    # prose complète, avec des éléments inventés (une voix, un intrus). Un
    # brief qui ressemble à une consigne d'écriture se fait exécuter comme
    # telle si rien ne le contredit des deux côtés.
    return (
        "Tu es un PLANIFICATEUR, pas un rédacteur. Tu ne produis QUE des "
        "lignes numérotées. Tu n'écris AUCUNE prose, AUCUN dialogue, AUCUNE "
        "entrée de carnet.\n\n"
        f"Objectif du chapitre : {brief}\n"
        f"{contraintes}\n"
        "Le chapitre est un carnet. Découpe-le en ENTRÉES DATÉES, une par "
        "soir. **Respecte le nombre d'entrées que l'objectif impose** : s'il "
        "dit « entrée unique », ton plan fait UNE ligne ; s'il dit trois "
        "entrées, il en fait trois. Jamais plus de trois.\n\n"
        "Format EXACT, une ligne par entrée, rien d'autre. Entre crochets, la "
        "météo du jour en deux mots ; puis le contenu :\n"
        "1. [Ciel couvert] ce qu'elle relit, ce qu'elle constate — l'état "
        "NOUVEAU à la fin.\n"
        "2. [Pluie fine] …\n\n"
        "N'écris AUCUN en-tête daté : les dates sont posées ailleurs.\n"
        "RÈGLE ABSOLUE : chaque entrée fait AVANCER d'un cran. Aucune entrée "
        "ne rejoue ni ne re-décrit ce qu'une autre a déjà noté. N'invente "
        "aucun élément que l'objectif ne fournit pas.\n\n"
        "Rends uniquement les lignes numérotées."
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
    rag = state.get("rag", True)

    # COURT-CIRCUIT MONO-ENTRÉE (item 10). Planifier une entrée unique est
    # dégénéré : le modèle rédige au lieu de découper, et on se replie sur le
    # brief. En étage B, ce détour coûtait 139 à 222 secondes — pour rien.
    if state.get("entrees_attendues", 0) == 1:
        progress.phase("Plan", "court-circuité (brief mono-entrée)")
        return {
            "plan": [state["brief"]], "facts": [],
            "plan_report": "plan court-circuité — brief mono-entrée (item 10)",
            "idx": 0, "scenes": [], "metrics": [], "warnings": [],
        }

    # Sans RAG, les faits n'ont pas de source : `derive_facts` lit les fiches
    # via Chroma. Toute la chaîne de contrainte (vérification du plan, rapport
    # de cohérence) est donc inerte à l'étage A — par construction, pas par
    # accident. L'écart A → B portera cette variable EN PLUS de la matière
    # servie à l'écriture : à garder en tête à la lecture des grilles.
    if not rag:
        facts: list[str] = []
        warnings.append(
            "étage A (rag=False) : aucun fait dérivé — plan non contraint et "
            "rapport de cohérence inerte, par construction"
        )
        progress.note("sans RAG : ni invariants, ni contrôle du plan")
    else:
        progress.phase("Invariants de la bible", "(Qwen)")
        facts, mf = derive_facts(state["characters"])
        metrics.extend(_tag([mf], "plan/faits"))
        progress.note(f"{len(facts)} faits dérivés, ils contraignent le plan")
        unload(QA_MODEL)  # place nette avant de charger nemo

    beats: list[str] = []
    rapport = "Plan non vérifié (aucun fait dérivé de la bible)."
    feedback = ""
    for attempt in range(1, MAX_PLAN_ATTEMPTS + 1):
        progress.phase("Plan d'entrées",
                       f"(nemo, tentative {attempt}/{MAX_PLAN_ATTEMPTS})")
        # Le plan est une structure, pas de la prose : il reçoit le préambule
        # et la règle du récit, pas le contrat de style — servir *Narration*
        # et *Interdits* à un planificateur gonfle le prompt sans rien cadrer.
        system = assemble_system_prompt(
            characters=state["characters"], scene_brief=state["brief"],
            rag=rag, style=(), include_scenes=False,
        )
        text, m = chat(system, _plan_user(state["brief"], facts, feedback),
                       num_predict=500, temperature=0.5,
                       on_token=progress.token_sink())
        metrics.extend(_tag([m], "plan"))
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
        progress.phase("Contrôle du plan contre la bible", "(Qwen)")
        violations, rapport, mv = check_plan(facts, beats)
        metrics.extend(_tag(mv, "plan/controle"))
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
        refus = "; ".join(f"contredit « {fait} »" for _, fait, _ in violations)
        warnings.append(f"plan (tentative {attempt}) refusé : {refus}")
        progress.note(f"PLAN REFUSÉ — {refus}. Replanification.")
        feedback = _plan_feedback(violations)
        unload(QA_MODEL)  # Qwen → nemo pour la reprise

    # Filet : un plan illisible ne doit pas faire tomber le graphe. `write_node`
    # indexe `plan[idx]` et lèverait un IndexError — une génération de chapitre
    # perdue parce que le planificateur a mal formaté sa réponse. Le brief lui
    # même fait alors office d'unique entrée : c'est le comportement juste pour
    # un brief mono-entrée, et le moins mauvais pour les autres.
    if not beats:
        beats = [state["brief"]]
        warnings.append(
            "plan sans ligne numérotée — repli sur une entrée unique tirée du "
            "brief. Attendu sur un brief mono-entrée, où planifier est "
            "dégénéré : le modèle rédige au lieu de découper, et le brief fait "
            "lui-même office de beat"
        )
        progress.note("plan non découpé : le brief fait office d'entrée unique")

    # L'écriture veut nemo seul : Qwen a pu rester chaud après la vérification.
    # Sans RAG, Qwen n'a jamais été chargé — rien à décharger.
    if rag:
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
    progress.phase("Écriture", f"entrée {idx + 1}/{len(state['plan'])} (nemo)",
                   i=idx + 1, n=len(state["plan"]))
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=beat,
        include_scenes=False,  # continuité gérée par le threading explicite ci-dessous
        rag=state.get("rag", True),
    )

    # Plan annoté : [fait] / >> à écrire / [à venir].
    plan_lines = []
    for j, b in enumerate(state["plan"]):
        mark = ">>" if j == idx else ("[fait]" if j < idx else "[à venir]")
        plan_lines.append(f"  {j + 1}. {mark} {b}")
    plan_txt = "\n".join(plan_lines)

    # CONTINUITÉ PAR ANCRE (item 4). On n'injecte plus les deux dernières
    # entrées pleines : montrer des entrées entières faisait recopier des
    # paragraphes d'une entrée à l'autre — AC produisait huit en-têtes dont un
    # répété cinq fois. La continuité passe désormais par l'ÉTAT NARRATIF, déjà
    # servi dans le prompt système, et par le plan annoté ci-dessus qui dit ce
    # qui est fait. Une ancre décrit où l'on en est ; un texte complet invite à
    # le continuer mot pour mot.
    prior_block = ""

    lo, hi = MOTS_PAR_ENTREE
    # PRÉFIXAGE PAR LE CODE (item 5) : l'en-tête et la citation ancre ne sont
    # pas DEMANDÉS au modèle, ils lui sont DONNÉS déjà écrits — il continue.
    # A3 avait altéré l'ancre et corrompu les beats 2-3 qui en dépendaient ;
    # une consigne n'empêche pas une altération, un texte déjà posé si.
    # PRÉFIXAGE PAR CONCATÉNATION RÉELLE, plus par consigne. La version
    # précédente disait « recopie-le à l'identique » : c'était une INSTRUCTION,
    # donc B′1 a pu l'altérer — et l'a fait, au pluriel (« Je les ai laissées »
    # pour « Je l'ai laissée »). Si l'ancre a pu bouger, c'est qu'elle était
    # servie en consigne. Désormais le code écrit ce début et le modèle ne fait
    # que continuer : l'ancre devient inaltérable par construction.
    # L'en-tête est COMPOSÉ ici, jamais demandé, et concaténé avec l'ancre de
    # citation quand le brief en fournit une. La météo vient du plan ; la date
    # se dérive de l'ancre de séquence, donc les entrées d'un chapitre sont
    # consécutives sans qu'on ait à le vérifier.
    meteo, beat = separer_meteo(beat)
    jour_depart = state.get("jour_depart") or "Mardi"
    numero_depart = state.get("numero_depart") or 12
    tete = entete(jour_depart, numero_depart, idx,
                  meteo or (state.get("meteo_depart") if idx == 0 else ""))
    ancre = state.get("prefixe") or ""
    prefixe = f"{tete}\n\n{ancre}" if ancre else tete
    bloc_prefixe = (
        "L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :\n"
        f"---\n{prefixe}\n---\n"
        "Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète "
        "ni l'en-tête ni la citation.\n"
        if prefixe else
        "Elle s'ouvre par son en-tête : jour de la semaine, numéro, point, "
        "météo en deux mots, point. Jamais le mois, jamais l'année.\n"
    )
    user = (
        f"Plan du chapitre (>> = l'entrée à écrire maintenant) :\n{plan_txt}\n"
        f"{prior_block}\n"
        f"Écris UNIQUEMENT l'entrée {idx + 1} ({lo}-{hi} mots) : {beat}\n"
        f"{bloc_prefixe}"
        "NE réécris AUCUN événement déjà noté ci-dessus — tu enchaînes dans la "
        "continuité stricte. Montre la tension sans la nommer. Prose seule, "
        "sans titre ni méta-commentaire.\n"
        # CONSIGNE DE MASSE (bloc B). Les runs plafonnent à 185-366 mots : le
        # squelette se coche, il ne se remplit pas — et le verdict oral du
        # 2026-08-19 attribue à ce manque l'absence de voix. On ne demande pas
        # « plus long », on dit OÙ la longueur se prend.
        "La reconstruction occupe au moins la moitié de l'entrée — la soirée "
        "entière, du retour à la cuisine au coucher, avant le verdict."
        # « fais entendre les voix distinctes » a disparu : une seule voix,
        # aucun dialogue. La consigne poussait vers ce que la fiche interdit.
    )
    text, ms, wg = _generate_whole(system, user, num_predict=1400,
                                   temperature=0.7, label=f"entrée {idx + 1}")
    # La concaténation elle-même. `_recoller` retire le chevauchement au
    # caractère près si le modèle a redonné l'en-tête ou l'ancre malgré la
    # consigne — on ne veut ni doublon, ni ancre recomposée.
    # Le code est PROPRIÉTAIRE du format d'en-tête : il en compose un par
    # entrée. Tout en-tête daté que le modèle produit est donc parasite par
    # définition — C1 en a inventé un second (« Vendredi 15. Pluie fine. »)
    # dans une entrée censée être unique, et le lint découpait deux entrées là
    # où il n'y en avait qu'une. On les retire, sans le redemander au modèle :
    # une consigne de plus se serait ajoutée à celle qu'il vient d'ignorer.
    text, repetees = SUSPENSION_REPETEE.subn(r"\1", text)
    text, isolees = SUSPENSION_PARASITE.subn(", ", text)
    suspensions = repetees + isolees
    if suspensions:
        wg.append(f"entrée {idx + 1} : {suspensions} point(s) de suspension "
                  "produit(s) par le modèle, retiré(s) — le marqueur est "
                  "réservé au glissement, que le code compose")
    text, retires = ENTETE_PARASITE.subn("", text)
    if retires:
        wg.append(f"entrée {idx + 1} : {retires} en-tête(s) daté(s) produit(s) "
                  "par le modèle, retiré(s) — le code compose les en-têtes")
    if prefixe:
        text = _recoller(prefixe, _retirer_reprise_approximative(prefixe, text))
    text, w = delint(text)
    return {
        "scenes": state["scenes"] + [text],
        "idx": idx + 1,
        "metrics": state["metrics"] + _tag(ms, f"write/{idx + 1}"),
        "warnings": state["warnings"] + wg
        + [f"entrée {idx + 1}: {x}" for x in w],
    }



# --- Micro-nœuds d'assemblage (étage C) --------------------------------------
#
# Le reproche ne MONTRE aucun texte d'exemple. La session 3 a mesuré qu'un
# étalon montré se recopie caractère pour caractère, et `valider_accumulation`
# le détecte. On décrit le mouvement, on chiffre la contrainte, on ancre dans
# les objets de l'entrée.
_ACC_CONSIGNE = """Voici une entrée de carnet.

Écris UNE SEULE PHRASE qui reprenne, dans l'ordre, les faits de la soirée que \
cette entrée raconte : le retour, les gestes, les objets, les heures — jusqu'à \
celui qui cloche, sur lequel la phrase s'achève.

Contraintes, vérifiées :
- une seule phrase : AUCUN point, aucun point-virgule à l'intérieur ;
- **au moins DOUZE étapes**, chacune séparée par une simple virgule — l'heure \
du retour, un geste, un objet, une pièce, un autre geste, et ainsi de suite \
jusqu'au coucher ;
- pas de « et » ni de « puis » pour les relier : la virgule seule ;
- puis la rupture (« sauf une, une seule ») et l'étape qui cloche ;
- entre douze et vingt étapes : au-delà, c'est un emballement, pas une spirale ;
- uniquement des faits DE CETTE ENTRÉE, aucun objet ni lieu nouveau.

Rends la phrase seule, rien d'autre."""

_GLI_CONSIGNE = """Voici une entrée de carnet.

Ne RECOPIE RIEN de cette entrée — ni son en-tête, ni ses phrases.

Écris deux choses, sur deux lignes :
1. une phrase où la narratrice commence à s'approcher du POURQUOI ou du OÙ du \
départ de celle qui est partie — elle s'interrompt d'elle-même, tu laisses la \
phrase inachevée, sans ponctuation finale ;
2. un fait matériel très court sur un objet de la maison ({objets}) : ce qu'elle \
voit, son état, un compte. Déclaratif, six mots au plus.

Rends exactement deux lignes, rien d'autre."""


def accumulate_node(state: ChapterState) -> dict:
    """Produit la phrase d'accumulation. Le CODE la valide et la placera.

    Quatre sessions ont établi qu'elle ne s'obtient ni par la fiche (trois
    formulations) ni par une boucle de reproche (jamais une authentique). Elle
    est donc assemblée : le modèle fournit la matière, le code la forme.
    """
    if not state.get("micro_noeuds") or not state["scenes"]:
        return {}
    entree = state["scenes"][-1]
    metrics, warns, phrase = [], [], ""
    for essai in range(1, MAX_TENTATIVES_GESTE + 1):
        progress.phase("Accumulation",
                       f"entrée {len(state['scenes'])} (essai {essai})")
        txt, m = chat(_ACC_CONSIGNE, entree, model=MODELE_GESTES,
                      temperature=TEMP_GESTES, num_predict=300)
        metrics.append(m)
        candidat = " ".join(txt.strip().split())
        # Compter des ÉTAPES est une opération que le modèle sait faire ;
        # compter des MOTS non — il rendait 48 mots pour un plancher de 60,
        # deux fois de suite. Le code, lui, continue de vérifier en mots : la
        # consigne vise ce qui est atteignable, la garde mesure ce qui compte.
        ok, raison = valider_accumulation(
            candidat, dernier_essai=(essai == MAX_TENTATIVES_GESTE))
        if ok:
            phrase = candidat
            if raison:
                warns.append(f"accumulation entrée {len(state['scenes'])} : "
                             f"{raison}")
            break
        warns.append(f"accumulation entrée {len(state['scenes'])}, essai "
                     f"{essai} : {raison}")
    if not phrase:
        warns.append(f"accumulation entrée {len(state['scenes'])} : ABANDONNÉE "
                     f"après {MAX_TENTATIVES_GESTE} essais")
    return {"accumulation": phrase,
            "metrics": state["metrics"] + _tag(metrics, "accumulate"),
            "warnings": state["warnings"] + warns}


def glisse_node(state: ChapterState) -> dict:
    """Produit le glissement, puis ASSEMBLE les deux gestes dans l'entrée.

    L'assemblage vit ici, dans le second nœud, et non dans chacun : les deux
    positions doivent se calculer sur le texte ORIGINAL. Si `accumulate` avait
    déjà inséré sa phrase, les offsets du glissement porteraient sur un texte
    décalé et le geste atterrirait à côté.
    """
    if not state.get("micro_noeuds") or not state["scenes"]:
        return {}
    entree = state["scenes"][-1]
    objets = state.get("objets_actifs") or "le cahier, le carnet, l'égouttoir"
    glissement, warns, metrics = "", [], []
    # DEUX TENTATIVES, comme `accumulate`. Le modèle a rendu une poubelle trois
    # fois sur trois au premier câblage — en réémettant l'en-tête de l'entrée
    # qu'on lui donnait à lire. Un seul essai transformait ce travers en zéro
    # glissement, or M1 est bloquant à l'étage C.
    for essai in range(1, MAX_TENTATIVES_GESTE + 1):
        progress.phase("Glissement",
                       f"entrée {len(state['scenes'])} (essai {essai})")
        txt, m = chat(_GLI_CONSIGNE.format(objets=objets), entree,
                      model=MODELE_GESTES, temperature=TEMP_GESTES,
                      num_predict=160)
        metrics.append(m)
        lignes = [l.strip(" -–—123.").strip() for l in txt.strip().splitlines()
                  if l.strip()]
        if len(lignes) < 2:
            warns.append(f"glissement entrée {len(state['scenes'])}, essai "
                         f"{essai} : moins de deux lignes exploitables")
            continue
        ok, raison = approche_valide(lignes[0])
        if ok:
            glissement = composer_glissement(lignes[0], lignes[1])
            break
        warns.append(f"glissement entrée {len(state['scenes'])}, essai "
                     f"{essai} : approche rejetée — {raison}")
    if False:
        # `approche_valide` était ÉCRITE et JAMAIS APPELÉE — un lint fantôme de
        # ma main, une heure après avoir gravé le principe. D'où, au second run
        # C encore, un « Mardi 12. Ciel couvert… » composé en fin d'entrée : le
        # validateur existait, le code ne le consultait pas.
        pass

    # Les fragments sont MIS DE CÔTÉ, pas insérés ici. Posés dans `scenes`, ils
    # traversaient ensuite `review` (« resserre la prose ») et `repair` — qui
    # réécrivent l'entrée entière et dissolvaient l'accumulation : une phrase de
    # soixante mots est précisément ce qu'une consigne de resserrement casse. Le
    # geste se pose donc sur le texte FINAL, dans `poser_gestes`.
    gestes = list(state.get("gestes") or [])
    gestes.append({"accumulation": state.get("accumulation") or "",
                   "glissement": glissement})
    return {"gestes": gestes, "accumulation": "",
            "metrics": state["metrics"] + _tag(metrics, "glisse"),
            "warnings": state["warnings"] + warns}


def poser_gestes_node(state: ChapterState) -> dict:
    """Insère les gestes dans le texte FINAL, après relecture et réparation.

    C'est le seul endroit où ils survivent : en amont, `review` et `repair`
    réécrivent l'entrée et emportent l'accumulation avec le reste. Les gestes
    sont des artefacts COMPOSÉS par le code — les soumettre à une passe de
    réécriture revenait à demander au modèle de défaire ce qu'on venait de
    construire.
    """
    if not state.get("micro_noeuds"):
        return {}
    gestes = state.get("gestes") or []
    entrees_finales = state.get("repaired") or state.get("reviewed") or []
    if not gestes or not entrees_finales:
        return {}
    progress.phase("Pose des gestes", f"{len(gestes)} entrée(s)")
    sorties, warns = [], []
    for i, entree in enumerate(entrees_finales):
        g = gestes[i] if i < len(gestes) else {}
        texte, notes = assembler(entree, g.get("accumulation") or "",
                                 g.get("glissement") or "",
                                 state.get("verdict") or "")
        sorties.append(texte)
        warns += [f"assemblage entrée {i + 1} : {n}" for n in notes]
        if not (g.get("accumulation") or "").strip():
            warns.append(f"assemblage entrée {i + 1} : aucune accumulation à "
                         "poser")
    return {"repaired": sorties, "warnings": state["warnings"] + warns}


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
        include_scenes=False, rag=state.get("rag", True),
        style=STYLE_RELECTURE, epistemique=False,
    )
    for i, scene in enumerate(state["scenes"]):
        progress.phase("Relecture",
                       f"entrée {i + 1}/{len(state['scenes'])} (nemo)",
                       i=i + 1, n=len(state["scenes"]))
        # ~3,5 caractères par token en français ; on vise 1,6x la longueur
        # de la scène, borné, pour laisser la place à une réécriture complète.
        budget = min(2000, max(1200, int(len(scene) / 3) + 300))
        user = (
            "Relis et RÉÉCRIS INTÉGRALEMENT cette entrée de carnet pour "
            "resserrer la prose : supprime les répétitions, renforce les "
            "images, garde EXACTEMENT la voix et les faits, et conserve "
            "l'en-tête daté tel quel. Rends l'entrée ENTIÈRE corrigée, du "
            "début à la fin, et rien d'autre (pas de commentaire, pas de "
            "titre).\n\n"
            f"--- ENTRÉE À RÉÉCRIRE ---\n{scene}"
        )
        text, ms, wg = _generate_whole(system, user, num_predict=budget,
                                       temperature=0.5,
                                       label=f"relecture entrée {i + 1}")
        metrics.extend(_tag(ms, f"review/{i + 1}"))
        warns.extend(wg)
        # Garde-fou anti-destruction : relecture trop courte -> on garde
        # l'original. Il était SILENCIEUX : une réécriture qui resserrait fort
        # était annulée en bloc sans que rien ne le dise, et un travail de style
        # visant la concision disparaissait sans trace. On le fait parler.
        avant, apres = len(scene.split()), len(text.split())
        if apres < 0.6 * avant:
            warns.append(
                f"relecture entrée {i + 1}: garde-fou 60 % déclenché "
                f"({apres} mots contre {avant}, soit {apres / max(avant, 1):.0%}) "
                "— relecture REJETÉE, original conservé"
            )
            text = scene
        text, w = delint(text)
        warns.extend(f"relecture entrée {i + 1}: {x}" for x in w)
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
    progress.phase("Bascule des modèles", "nemo déchargé, Qwen prend la main")
    if not unload():
        warns.append("QA : déchargement de nemo refusé par Ollama (co-résidence "
                     "nemo + Qwen, pression mémoire)")
        progress.note("déchargement de nemo REFUSÉ — pression mémoire")
    for i, scene in enumerate(state["reviewed"]):
        progress.phase("Réparation linguistique",
                       f"entrée {i + 1}/{len(state['reviewed'])} (Qwen)",
                       i=i + 1, n=len(state["reviewed"]))
        text, m = repair(scene)
        metrics.extend(_tag([m], f"repair/{i + 1}"))
        # Garde-fou : une réparation ne doit pas escamoter l'entrée. Bavard
        # pour la même raison que celui de la relecture.
        avant, apres = len(scene.split()), len(text.split())
        if apres < 0.6 * avant:
            warns.append(
                f"réparation entrée {i + 1}: garde-fou 60 % déclenché "
                f"({apres} mots contre {avant}, soit {apres / max(avant, 1):.0%}) "
                "— réparation REJETÉE, texte relu conservé"
            )
            text = scene
        # Re-lint pour tracer ce qui resterait (anglais tenace, tokens collés).
        text, w = delint(text)
        warns.extend(f"réparation entrée {i + 1}: {x}" for x in w)
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
    progress.phase("Cohérence par faits", "(Qwen)")

    facts = state.get("facts") or []
    # Sans RAG, il n'y a pas de bible à interroger : re-dériver ici irait
    # chercher Chroma et ferait tomber tout le run sur un conteneur éteint.
    # Le nœud est INERTE à l'étage A, par construction — c'est la seconde
    # variable de l'écart A → B, et elle doit se lire dans le rapport plutôt
    # que se manifester en trace d'appel.
    if not facts and state.get("rag", True):
        # Plan court-circuité (test unitaire, reprise) : on redérive.
        facts, mf = derive_facts(state["characters"])
        metrics.extend(_tag([mf], "coherence/faits"))
    if not facts:
        return {
            "coherence": ("Aucun fait dérivé de la bible — cohérence inerte "
                          "(étage A, rag=False)." if not state.get("rag", True)
                          else "Aucun fait dérivé de la bible."),
            "metrics": metrics,
        }

    rapport, mc = check_facts(facts, state["repaired"])
    metrics.extend(_tag(mc, "coherence"))
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
    g.add_node("accumulate", accumulate_node)
    g.add_node("glisse", glisse_node)
    g.add_edge("plan", "write")
    # Les gestes s'assemblent DANS la boucle, une passe par entrée : ils
    # travaillent sur une entrée close, pas sur un chapitre.
    g.add_edge("write", "accumulate")
    g.add_edge("accumulate", "glisse")
    g.add_conditional_edges("glisse", route_after_write, ["write", "review"])
    g.add_edge("review", "repair")
    # Les gestes se posent APRÈS la réparation, sur le texte final — et donc
    # AVANT la cohérence, qui doit juger le chapitre tel qu'il sera lu.
    g.add_node("poser_gestes", poser_gestes_node)
    g.add_edge("repair", "poser_gestes")
    g.add_edge("poser_gestes", "coherence")
    g.add_edge("coherence", END)
    return g.compile()
