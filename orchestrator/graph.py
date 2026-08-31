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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "outillage"))

import progress
from lint_style import (ENTETE_ENTREE, MACHINERIE,  # noqa: E402
                        MARQUES, META_TERMES, interdits_materiels)
from llm import AUTHOR_MODEL, chat, unload
from retrieval import STYLE_RELECTURE, assemble_system_prompt
from style import delint, ends_mid_sentence, sentence_ends, trim_to_sentence
from qa import QA_MODEL, repair, derive_facts, check_facts, check_plan
from gestes import (assembler, composer_glissement, passage_valide,
                    position_frontiere, tirer_approche,
                    valider_accumulation)
from lint_style import paragraphes_redits  # noqa: E402

# Modèle des micro-nœuds. nemo par défaut, et non Qwen : les nœuds tournent DANS
# la boucle d'écriture, nemo chaud — un appel Qwen y coûterait deux bascules par
# entrée (mesurées à 139-222 s dans `plan_node` en session 4). Surtout,
# `accumulate` écrit le marqueur le plus audible du style et sa phrase reste
# dans le chapitre : c'est de la voix, pas de la QA. Paramétrable pour que
# l'alternative reste mesurable en un run.
MODELE_GESTES = os.environ.get("MODELE_GESTES", AUTHOR_MODEL)
# Passe d'assemblage : pruning DÉTERMINISTE du résidu diffus (journée dehors,
# présence, récursion, tell de résolution) que le best-of-N ne rattrape pas
# quand TOUS les variants le portent. La piste cross-modèle Qwen a été falsifiée
# et écartée : Qwen coupe le bon (éditeur) et ne détecte pas la sortie oblique
# (détecteur, « NON » sur « le départ, la réunion, la départementale, le garage »
# — le nœud cohérence a le même angle mort). Le code, lui, matche sans ambiguïté.
ASSEMBLAGE_ACTIF = os.environ.get("ASSEMBLAGE", "1") != "0"
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
    segments: bool        # session 6 : `write` en trois appels — LA variable mesurée
    reconstruction: str   # le segment du milieu, contexte propre d'accumulate
    entrees_spec: list    # plan d'entrées explicite — le ch. 7 en a deux le MÊME jour
    plan_impose: list     # un beat par entrée, découpé du brief : le plan ne se demande pas
    chute_posee: str      # dernière ligne imposée au mot près — posée par le code
    prompts_servis: list  # (segment, prompt) — livrable, et mesure de la recopie
    entete_pose: str      # l'en-tête composé pour l'entrée courante — re-tamponné
    ancre_posee: str      # l'ancre de citation posée — re-tamponnée après repair
    graine: int           # tirage du glissement, consigné au frontmatter du run
    chapitre: int         # numéro du chapitre — scope des interdits matériels
    approches_tirees: list[str]  # jamais deux fois la même dans un chapitre


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
# Le numéro est OPTIONNEL : le modèle produit aussi « Samedi. Beau temps. »,
# un en-tête sans date qui a traversé tous les filtres et s'est retrouvé sous
# celui du code, dans le texte lu par la voix clonée. Le code est propriétaire
# du format ; une imitation approximative reste une imitation.
ENTETE_PARASITE = re.compile(
    # ⚠ PAS de `re.IGNORECASE` global : il rendrait la classe [A-Z] sensible aux
    # minuscules, et c'est précisément la majuscule de la météo qui distingue un
    # en-tête d'une phrase ouvrant sur un jour. L'insensibilité est limitée aux
    # noms de jours, par un groupe en ligne.
    r"^[ \t]*(?i:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)"
    r"(?:"
    # avec numéro : la forme complète, celle que le code compose
    r"[ \t]+\d{1,2}[.,][^\n]{0,40}"
    # SANS numéro : « Samedi. Beau temps. » — un en-tête sans date, qui a
    # traversé tous les filtres et s'est retrouvé dans le texte lu par la voix
    # clonée. Reconnu par la majuscule de la météo et la fin de ligne.
    r"|[.,][ \t]*[A-ZÀÂÇÉÈÊËÎÏÔÛÙÜŒ][^\n,]{1,28}\."
    r")[ \t]*\n+", re.MULTILINE)

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
                    temperature: float, label: str,
                    continuer: bool = True) -> tuple[str, list[dict], list[str]]:
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

    for _ in range(MAX_CONTINUATIONS if continuer else 0):
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
    # COURT-CIRCUIT SUR PLAN FOURNI. Quand le brief porte déjà un beat par
    # entrée (`plan_impose`), planifier n'ajoute rien et peut tout défaire : au
    # premier tirage du chapitre 7, le nœud n'a produit aucune ligne numérotée
    # sur un brief en prose formatée, et le repli a donné le brief ENTIER à
    # chaque entrée — les deux ont donc reçu la consigne décrivant les deux.
    # Planifier ce qui est déjà écrit, c'est offrir l'occasion de le défaire.
    if state.get("plan_impose"):
        progress.phase("Plan", f"fourni par le brief "
                               f"({len(state['plan_impose'])} entrées)")
        return {
            "plan": list(state["plan_impose"]), "facts": [],
            "plan_report": "plan FOURNI par le brief — nœud court-circuité "
                           "(structure imposée, un beat par entrée)",
            "idx": 0, "scenes": [], "metrics": [], "warnings": [],
        }

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

    # LE PLAN D'ENTRÉES FAIT LOI SUR LE NOMBRE (micro-lot, correctif CH7).
    #
    # `entrees_spec` décrit une structure imposée par le brief — deux entrées du
    # même jour pour le chapitre 7. Le nœud de plan, lui, n'en savait rien : il
    # a rendu QUATRE beats, et les entrées 3 et 4, hors spec, sont retombées sur
    # les dates dérivées (« Lundi 16 », « Mardi 17 »). Un chapitre de 2281 mots
    # là où le brief en demande deux entrées, et une structure de scène détruite
    # — la bascule se pose sur le second en-tête, elle aurait ouvert l'audio sur
    # une entrée qui n'existe pas au brief.
    #
    # Quand la structure est donnée, elle n'est pas négociable : on coupe. Et on
    # le DIT — un plan tronqué en silence se relit comme un plan obéi.
    spec = state.get("entrees_spec") or []
    if spec and len(beats) != len(spec):
        warnings.append(
            f"plan à {len(beats)} entrée(s) contre {len(spec)} imposée(s) par "
            f"le brief — tronqué. Beats écartés : "
            f"{[b[:60] for b in beats[len(spec):]] or 'aucun'}")
        progress.note(f"plan ramené de {len(beats)} à {len(spec)} entrées")
        beats = beats[:len(spec)]
        while len(beats) < len(spec):
            beats.append(state["brief"])

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
    # La fiche de CETTE entrée, lue en tête du nœud : elle commande l'en-tête,
    # la citation, la cible de mots et le découpage. Vide hors chapitre 7 —
    # tout le reste du pipeline est alors inchangé.
    spec = state.get("entrees_spec") or []
    fiche = spec[idx] if idx < len(spec) else {}
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

    lo, hi = fiche.get("mots") or MOTS_PAR_ENTREE  # cible propre à l'entrée
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
    # PLAN D'ENTRÉES EXPLICITE (session 7) — le brief le fournit, au lieu que le
    # code le dérive. Sans lui, rien ne change : les dates se dérivent comme
    # depuis la session 5, et les chapitres 1-6 et 8-11 sont inchangés.
    #
    # Il existe pour le CHAPITRE 7, qui demande DEUX ENTRÉES DU MÊME JOUR
    # (« Samedi 14. » deux fois : l'après-midi et la nuit de l'anniversaire).
    # Trois dispositifs s'y opposaient, tous construits délibérément :
    #   · `entete()` dérive `numero_depart + idx` — l'entrée 2 sortait
    #     « Dimanche 15 », et la structure du chapitre était impossible ;
    #   · `entetes_coherents` refuse deux en-têtes identiques ;
    #   · les 450-600 mots en trois segments contre « entrée 1 : DEUX PHRASES ».
    # L'enjeu n'est pas cosmétique : la bascule audio se place sur le SECOND
    # en-tête normalisé. Pas d'en-tête conforme, pas de coïncidence scénique.
    jour_depart = state.get("jour_depart") or "Mardi"
    numero_depart = state.get("numero_depart") or 12
    if fiche.get("jour"):
        tete = entete(fiche["jour"], fiche["numero"], 0,
                      fiche.get("meteo") or meteo or "")
    else:
        tete = entete(jour_depart, numero_depart, idx,
                      meteo or (state.get("meteo_depart") if idx == 0 else ""))
    # La citation d'ancre devient un champ de l'entrée : au chapitre 7, l'entrée
    # 1 NE CITE PAS (« première entorse au rituel, premier signal ») et l'entrée
    # 2 s'ouvre sur [CIT-2]. Servir la même ancre aux deux détruirait le signal.
    ancre = (fiche.get("citation") if "citation" in fiche
             else state.get("prefixe") or "")
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
    # --- LA VARIABLE MESURÉE DE LA SESSION 6 ------------------------------
    # Un seul appel traitait cinq beats : le modèle écrivait un paragraphe par
    # beat et s'arrêtait. La masse vit dans UN beat — la reconstruction — et
    # elle n'avait jamais eu d'appel à elle. On décompose, ce qui est le
    # principe qui vient de gagner l'accumulation, appliqué un cran plus haut.
    #
    # Hors étage S6, la branche d'origine reste intacte À L'OCTET PRÈS : c'est
    # par elle que tout le pipeline a été chronométré, et l'habillage d'un
    # étage ne doit jamais rejouer la validation d'un autre.
    reconstruction = ""
    # Le PROMPT SERVI est conservé : c'est un livrable de la méthode du
    # mouvement (« dump du prompt servi »), et c'est aussi ce qui permet de
    # mesurer la recopie — le contrôle qui manquait au tirage 6.
    prompts_servis: list[tuple[str, str]] = []
    if fiche.get("beats"):
        # CAP-CODE STRUCTUREL (entrée 2, v5). Chaque beat est un appel court,
        # servi SEUL (pas le mouvement entier — cf. `_prompt_beat`), borné en
        # phrases ET en tokens par le code. Le texte déjà écrit devient le
        # préfixe du beat suivant (doctrine du préfixage), et `_recoller`
        # absorbe une reprise. Le glissement et la chute restent posés en aval
        # par `poser_gestes_node` : rien de neuf dans le pipeline des gestes.
        text, ms, wg = "", [], []
        # FIX RACINE : voix servie SANS les étapes verdict/couperet (cf.
        # `_VOIX_VERDICT`). Réassignation locale — les autres branches sont en
        # `elif`, et le tail commun n'utilise pas `system` pour générer.
        system = _VOIX_VERDICT.sub("", system)
        beats = fiche["beats"]
        premier_nom = beats[0][0]
        for nom, num_predict, phrases_max, consigne in beats:
            est_premier = (nom == premier_nom)
            deja = f"{prefixe}\n\n{text}".strip() if prefixe else text.strip()
            bloc = (
                "L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris "
                f"PAS :\n---\n{deja}\n---\n"
                "Écris uniquement CE QUI SUIT, en enchaînant directement. Ne "
                "répète rien de ce qui précède.\n" if deja else "")
            beat_user = _prompt_beat(consigne, bloc)
            prompts_servis.append((nom, beat_user))
            # BEST-OF-N par beat. Les échecs de nemo sont CORRÉLÉS (il résout /
            # redémarre dans tous les tirages, différemment) : on tire N
            # variants et le code garde celui qui porte le MOINS de défauts
            # nommés (`_scorer_beat`). La sélection est une lecture déterministe,
            # pas un juge de goût — falsifiable, donc digne de confiance.
            variantes = []
            for k in range(BEATS_N):
                progress.phase("Écriture",
                               f"entrée {idx + 1} — {nom} ({k + 1}/{BEATS_N})",
                               i=idx + 1, n=len(state["plan"]))
                seg, m, w = _generate_whole(
                    system, beat_user, num_predict=num_predict, temperature=0.7,
                    label=f"entrée {idx + 1}/{nom}#{k + 1}", continuer=False)
                seg, wn = _nettoyer_segment(seg, f"entrée {idx + 1}/{nom}#{k + 1}")
                seg, wb = _borner_en_phrases(seg, phrases_max, idx, "")
                sc, defauts = _scorer_beat(seg, est_premier,
                                           state.get("chapitre") or 2)
                variantes.append({"score": sc, "k": k, "seg": seg,
                                  "defauts": defauts, "m": m, "w": w + wn + wb})
            # Meilleur score ; à égalité, le premier tiré (stable, rejouable).
            variantes.sort(key=lambda v: (-v["score"], v["k"]))
            gagnant = variantes[0]
            seg = gagnant["seg"]
            wg += gagnant["w"]
            wg.append(
                f"entrée {idx + 1}/{nom} : best-of-{BEATS_N} — variant "
                f"{gagnant['k'] + 1} retenu (score {gagnant['score']}, "
                + (", ".join(gagnant["defauts"]) if gagnant["defauts"]
                   else "propre")
                + ") ; rejetés : "
                + " ; ".join(f"#{v['k'] + 1} score {v['score']}"
                             for v in variantes[1:]))
            text = _recoller(text, seg) if text else seg
            # Métriques de TOUS les variants — les jetons rejetés sont dépensés
            # (doctrine 5 : aucun chiffre sans son horloge).
            ms += [dict(m2, beat=nom, variant=v["k"])
                   for v in variantes for m2 in v["m"]]
        # L'accumulation prend l'entrée entière pour contexte : elle est courte.
        reconstruction = text
    elif fiche.get("segments", state.get("segments")):
        text, ms, wg = "", [], []
        for nom, num_predict, mots_cible, consigne in SEGMENTS:
            progress.phase("Écriture", f"entrée {idx + 1}/"
                           f"{len(state['plan'])} — {nom}",
                           i=idx + 1, n=len(state["plan"]))
            # Le texte déjà écrit devient le PRÉFIXE du segment suivant :
            # doctrine du préfixage étendue, sans mécanisme nouveau. La
            # continuité est garantie par construction, et `_recoller` absorbe
            # la reprise si le modèle redonne la fin malgré la consigne.
            deja = f"{prefixe}\n\n{text}".strip() if prefixe else text.strip()
            bloc = (
                "L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris "
                f"PAS :\n---\n{deja}\n---\n"
                "Écris uniquement CE QUI SUIT, en enchaînant directement. Ne "
                "répète rien de ce qui précède.\n" if deja else "")
            matiere = (_matiere_reconstruction(state)
                       if nom == "reconstruction" else "")
            stations = "\n".join(
                f"  {k}. {lieu}" for k, lieu in
                enumerate(STATIONS.get(state.get("chapitre") or 2, ()), 1))
            if fiche.get("mouvement"):
                # Méthode du mouvement : le brief porte tout, les consignes de
                # segment ne portent plus que la POSITION dans la trajectoire.
                seg_user = _prompt_mouvement(
                    fiche, mots_cible, POSITION_TRAJECTOIRE[nom], bloc)
            else:
                seg_user = (
                    f"Plan du chapitre (>> = l'entrée à écrire maintenant) :\n"
                    f"{plan_txt}\n\n"
                    f"Ce que l'entrée {idx + 1} raconte : {beat}\n\n"
                    f"{bloc}\n"
                    + consigne.format(mots=mots_cible, matiere=matiere,
                                    stations=stations) + "\n"
                    "Prose seule, sans titre, sans en-tête, sans "
                    "méta-commentaire. Montre la tension sans la nommer."
                )
            prompts_servis.append((nom, seg_user))
            seg, m, w = _generate_whole(
                system, seg_user, num_predict=num_predict, temperature=0.7,
                label=f"entrée {idx + 1}/{nom}")
            # Les filtres propriétaires du code s'appliquent AU SEGMENT, avant
            # qu'il devienne le préfixe du suivant : un en-tête réémis en tête
            # de la reconstruction serait recopié par la fermeture, qui le lit
            # comme du texte légitime déjà écrit.
            seg, wn = _nettoyer_segment(seg, f"entrée {idx + 1}/{nom}")
            wg += w + wn
            if nom == "reconstruction":
                reconstruction = seg.strip()
            text = _recoller(text, seg) if text else seg
            ms += [dict(m2, segment=nom) for m2 in m]
    else:
        # `num_predict` DÉRIVÉ DE LA CIBLE quand le brief en donne une.
        #
        # Le modèle occupe l'espace offert — mesuré trois fois (l'accumulation à
        # 214 mots sans plafond, la scène à 1400/1400, et ici l'entrée 1 du
        # chapitre 7 à 471 mots là où le brief en demande DEUX PHRASES). Offrir
        # 1400 tokens pour soixante mots, c'est demander soixante mots et en
        # autoriser six cents : la consigne dit une chose, le budget en dit une
        # autre, et c'est le budget qui gagne.
        # LA MÉTHODE DU MOUVEMENT VAUT AUSSI SANS DÉCOUPAGE. Quand la fiche
        # porte un mouvement, l'appel unique reçoit le même ordre de service —
        # sinon on retomberait sur le prompt de cases que la méthode remplace,
        # et la comparaison ne porterait plus sur le seul nombre d'appels.
        if fiche.get("mouvement"):
            user = _prompt_mouvement(
                fiche, f"{lo} à {hi} mots",
                "Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.",
                bloc_prefixe)
            prompts_servis.append(("entrée entière", user))
        budget = (int(hi * 1.6) + 40 if fiche.get("mots") else 1400)
        # PAS DE CONTINUATION quand la brièveté est VOULUE. La continuation
        # existe contre l'amputation accidentelle — un texte coupé en plein mot
        # à 1400 tokens. Sur une entrée bornée à soixante mots, `done_reason:
        # length` est le résultat DEMANDÉ, et relancer défait la borne : le
        # tirage précédent est reparti pour 300 tokens et a rendu 314 mots.
        # On coupe à la dernière phrase complète, ce que `_generate_whole` fait
        # déjà en filet.
        best_of = fiche.get("best_of")
        if best_of:
            # BEST-OF-N sur l'entrée ENTIÈRE (entrée 1). On SCORE la version
            # bornée à `phrases_max` — ce qui est réellement servi — via le
            # scorer nommé par `critere`. Même principe que les beats : la
            # sélection est une lecture déterministe, pas un juge de goût.
            phr = fiche.get("phrases_max")
            cont = not fiche.get("mots")
            cands = []
            for k in range(best_of):
                progress.phase("Écriture",
                               f"entrée {idx + 1} ({k + 1}/{best_of})",
                               i=idx + 1, n=len(state["plan"]))
                t, m, w = _generate_whole(
                    system, user, num_predict=budget, temperature=0.7,
                    label=f"entrée {idx + 1}#{k + 1}", continuer=cont)
                # Nettoyer l'en-tête parasite AVANT de scorer : sinon la borne à
                # deux phrases capture « Samedi 14. Beau temps. » (deux fins de
                # phrase) au lieu du corps, et les trois variants scorent pareil
                # — la sélection ne discrimine plus (mesuré au run précédent).
                t_propre = ENTETE_PARASITE.sub("", t).strip()
                a_scorer = (_borner_en_phrases(t_propre, phr, idx, "")[0]
                            if phr else t_propre)
                sc, defauts = (_scorer_entree1(a_scorer)
                               if fiche.get("critere") == "effacement-anniversaire"
                               else (0, []))
                cands.append({"score": sc, "k": k, "t": t, "m": m, "w": w,
                              "def": defauts})
            cands.sort(key=lambda c: (-c["score"], c["k"]))
            g = cands[0]
            text, wg = g["t"], list(g["w"])
            wg.append(
                f"entrée {idx + 1} : best-of-{best_of} — variant {g['k'] + 1} "
                f"retenu (score {g['score']}, "
                + (", ".join(g["def"]) if g["def"] else "propre")
                + ") ; rejetés : "
                + " ; ".join(f"#{c['k'] + 1} score {c['score']}"
                             for c in cands[1:]))
            ms = [dict(m2, variant=c["k"]) for c in cands for m2 in c["m"]]
        else:
            text, ms, wg = _generate_whole(
                system, user, num_predict=budget, temperature=0.7,
                label=f"entrée {idx + 1}", continuer=not fiche.get("mots"))
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

    # LES VÉTOS SUR LE TEXTE DE SCÈNE (lot orthogonal du chapitre 7).
    #
    # Jusqu'ici les interdits matériels et les marques n'étaient bloquants que
    # DANS `accumulate` : ils vivaient donc dans le texte d'écriture, où rien ne
    # les relançait. Sur un chapitre qui monte sur scène, le décor générique
    # n'est pas un défaut de style, c'est un objet qui n'existe pas — et une
    # marque déposée date le texte et le sort du monde clos de la maison.
    #
    # Une seule relance, comme partout ailleurs : au-delà, on garde et on crie.
    text, wv = _vetos_de_scene(text, idx, state, tentative=1)
    wg += wv

    # BORNE EN PHRASES quand le brief en pose une. La borne en mots a divisé
    # l'entrée 1 du chapitre 7 par cinq sans jamais compter les phrases : huit
    # produites là où le brief en demande deux, et c'est l'entrée que le
    # locuteur lit à voix nue. Une contrainte de scène se compte dans l'unité
    # de la scène.
    if fiche.get("phrases_max"):
        text, wp = _borner_en_phrases(text, fiche["phrases_max"], idx, prefixe)
        wg += wp

    text, w = delint(text)
    return {
        "scenes": state["scenes"] + [text],
        "idx": idx + 1,
        # Le segment de reconstruction est mis de côté pour `accumulate` : c'est
        # LUI qui devient son contexte, plus l'entrée entière. Le découpage rend
        # cette matière identifiable sans avoir à la deviner dans le texte.
        "reconstruction": reconstruction,
        # Ce que le code a COMPOSÉ pour cette entrée, mis de côté pour le
        # tampon de `poser_gestes_node` : lui seul peut le reposer à l'identique
        # après que la réparation l'a réécrit.
        "entete_pose": tete,
        "ancre_posee": ancre,
        "chute_posee": fiche.get("chute", ""),
        "prompts_servis": (state.get("prompts_servis") or []) + prompts_servis,
        "metrics": state["metrics"] + _tag(ms, f"write/{idx + 1}"),
        "warnings": state["warnings"] + wg
        + [f"entrée {idx + 1}: {x}" for x in w],
    }



# --- `write` en trois segments (session 6, §1) --------------------------------
#
# Trois appels séquentiels, chacun préfixé du précédent. Le découpage n'ajoute
# aucun mécanisme : il réemploie le préfixage par concaténation réelle, déjà
# éprouvé sur l'en-tête et l'ancre. Ce qu'il change, c'est le RAPPORT DE FORCE
# entre les beats — la reconstruction cesse d'être un beat parmi cinq et devient
# une tâche narrative nourrie, avec sa propre matière servie.
#
# Aucune de ces consignes ne nomme un terme d'atelier : c'est notre propre
# squelette servi qui avait fait sortir « Couperet : » en texte sur C2 et C3.
# Une assertion le vérifie plus bas — la relecture ne suffit pas, elle a déjà
# laissé passer le cas.
# LES CONSIGNES SONT EN FAITS, PLUS EN INTENTIONS (session 7).
#
# « Elle rétablit sa soirée » nomme ce que le personnage DÉCIDE de faire, et le
# modèle rend la décision en texte : « Je décide de rétablir ma soirée », « Je
# décide de refaire le fil de ma soirée ». Mesuré ×3 sur « je décide de » à la
# session 6 (sept occurrences sur S6-1, six sur S6-3), et les occurrences sont
# DISPERSÉES dans l'entrée — ce n'est donc pas la couture des segments, c'est la
# forme de la consigne. Une consigne qui décrit une intention produit un
# personnage qui décrit ses intentions.
#
# On ne demande donc plus une intention, on donne des FAITS et des LIEUX.
_SEG_OUVERTURE = """Écris seulement le DÉBUT de l'entrée, {mots}.

Le soir, le cahier ouvert : la phrase relue, l'écart entre ce qu'elle lit et \
ce dont elle se souvient, la chaise repoussée.

ARRÊTE-TOI AU SEUIL DE LA CUISINE. N'écris pas ce qu'elle y trouve."""

# LES STATIONS (session 7). Le plancher de masse devient mécanique : on ne
# demande plus « raconte longuement » — une consigne de longueur que le modèle
# lit comme un ton —, on donne des lieux à traverser. Une station traversée est
# un paragraphe ; six stations font une reconstruction.
#
# Aucune station ne fait revenir la narratrice de l'extérieur : elle travaille à
# la table du séjour. C'est par cette porte que « je suis revenue du travail »
# entrait (S6-3, C3), alors qu'elle ne sort pas.
_SEG_RECONSTRUCTION = """Écris maintenant le MILIEU de l'entrée, {mots} — \
c'est la partie la plus longue, et de loin.

Sa soirée, heure par heure, station par station. Chaque station tient en \
quelques lignes : l'heure, ce qu'elle a dans les mains, ce qu'elle voit.

{stations}

Un relevé, pas un résumé : aucune station n'est sautée, aucune n'est résumée \
en une proposition. Les heures sont écrites.

CHAQUE STATION SE FERME SUR UN FAIT — jamais sur un commentaire, jamais sur \
une question, jamais sur ce qu'elle en pense. Le relevé enchaîne sans \
récapituler : on passe à la station suivante, c'est tout.

{matiere}
Aucun verdict ici, aucune conclusion : ce segment ne fait que relever."""

_SEG_FERMETURE = """Écris la FIN de l'entrée, {mots}.

Le verdict, dans ses mots. Puis une ligne du corps, sans cause. Puis une \
phrase brève, qui referme.

LA DERNIÈRE LIGNE REFERME, ELLE NE CONSOLE PAS : aucune promesse au \
lendemain, aucune adresse à personne, aucun réconfort. Elle constate et \
s'arrête."""

# Le programme du jour — les stations du chapitre 2. Elles viennent de la table
# de pilotage côté PERÇU : ce sont les lieux d'une soirée ordinaire chez elle.
STATIONS = {
    # CHAPITRE 7 — la journée de l'anniversaire, entrée 2 (la nuit).
    #
    # Chaque station est l'ÉTAT CONSTATÉ d'un objet qu'elle avait entrepris
    # d'effacer. La contradiction est donc dans la matière, pas dans la
    # consigne : le brief porte déjà l'intention (« chaque geste d'effacement
    # dont elle se souvient d'avoir décidé est contredit par l'état de la
    # maison »), et la répéter ici en langue d'intention ferait revenir « je
    # décide de » — le défaut que ce même lot vient d'éteindre. Les stations
    # ne disent que ce qui EST.
    7: ("la table du séjour, la boîte ouverte, les photos étalées",
        "le salon, l'enceinte allumée, la musique qui tourne",
        "la cuisine, le plat au four, l'odeur",
        "la table, deux couverts mis",
        "le cahier ouvert, la ligne relue",
        "la lampe, la fin de la journée"),
    2: ("la table du séjour, le cahier refermé",
        "la cuisine, l'égouttoir",
        "le dîner, l'assiette",
        "la vaisselle, l'eau",
        "la relecture de l'entrée de la veille",
        "la lampe éteinte, le couloir"),
}

# (nom, num_predict, mots visés, consigne)
#
# `num_predict` est dimensionné segment par segment plutôt que laissé à 1400
# pour tous : offrir l'espace de l'entrée entière à l'ouverture, c'est l'inviter
# à écrire l'entrée entière — le modèle occupe l'espace offert, mesuré deux fois
# (l'accumulation à 214 mots sans plafond, la scène à 1400/1400).
SEGMENTS = (
    ("ouverture", 300, "80 à 120 mots", _SEG_OUVERTURE),
    ("reconstruction", 800, "250 à 350 mots", _SEG_RECONSTRUCTION),
    ("fermeture", 260, "60 à 100 mots", _SEG_FERMETURE),
)


# --- LA MÉTHODE DU MOUVEMENT (2026-08-27) -----------------------------------
#
# Le prompt cesse de décrire des cases à traverser. Il déclare un MOUVEMENT à
# accomplir, des directives de PROSE, une MATIÈRE disponible — dans cet ordre,
# et l'ordre fait partie de la méthode : l'intention avant la matière.
#
# Ce qui a rendu ce changement nécessaire se mesure. Le tirage 6 du chapitre 7
# s'ouvre sur « Le soir, le cahier ouvert : la phrase relue, l'écart entre ce
# que je lis et ce dont je me souviens, la chaise repoussée » — c'est la
# consigne d'ouverture, RECOPIÉE, à 0,94 de similarité. Sur les runs du
# chapitre 2 elle ne dépasse pas 0,37 : elle y décrit le rituel du chapitre et
# se fond. Au chapitre 7 elle est étrangère, donc le modèle l'a transcrite.
#
# C'est la leçon de la session 3 (« ce qui est montré se recopie ») retournée
# contre notre propre correctif : la session 6 avait écrit les consignes « en
# faits, plus en intentions » pour tuer les « je décide de ». Devenues de la
# prose, elles se sont fait recopier. Une consigne doit être une INSTRUCTION,
# reconnaissable comme telle.
POSITION_TRAJECTOIRE = {
    "ouverture": "Tu écris le DÉBUT de cette trajectoire.",
    "reconstruction": "Tu écris la SUITE de cette trajectoire — c'est la partie "
                      "la plus longue, et de loin.",
    "fermeture": "Tu écris la FIN de cette trajectoire.",
}


def _sans_machinerie(directive: str) -> str:
    """Retire d'une directive servie la clause qui parle de notre machinerie.

    Le brief est écrit pour deux lecteurs à la fois : l'implémenteur et le
    modèle. « Rien ne se résout… : la dernière ligne est posée d'office par le
    code » — la première moitié est une directive de prose, la seconde une note
    d'implémentation. Servir la seconde apprend au modèle qu'un code pose des
    lignes derrière lui, et c'est exactement ce que le firewall des méta-termes
    existe pour empêcher.
    """
    morceaux = re.split(r"\s*(?:—|:)\s*", directive)
    gardes = [m for m in morceaux if not MACHINERIE.search(m)]
    if len(gardes) == len(morceaux):
        return directive
    return (" : ".join(gardes) if gardes else "").rstrip(" :,;") + "."


BEATS_N = int(os.environ.get("BEATS_N", "3"))

# CRITÈRES DE SÉLECTION d'un variant de beat (best-of-N). Contrôles de LECTURE,
# déterministes et falsifiables — jamais un juge de goût (doctrine 3 : compter
# n'est pas lire). On ne note pas la prose ; on REJETTE des défauts nommés que
# dix tirages ont rendus récurrents. Le variant retenu porte le moins de défauts.
_BEAT_RESOUT = re.compile(
    r"je\s+me\s+(?:souviens|rappelle)\s+(?:soudain|maintenant|enfin|"
    r"à\s+nouveau|de\s+tout|de\s+chaque|bien|parfaitement)"
    r"|(?:cela|ça)\s+me\s+revient"
    r"|\bverdict\s*:\s*\w"
    r"|(?:m'a\s+jou\w+\s+un|me\s+joue\s+(?:des?|un))\s+tours?"
    r"|je\s+n'ai\s+pas\s+rêvé"
    r"|j'ai\s+bien\s+(?:mis|fait|noté)", re.IGNORECASE)
_BEAT_DISMISS = re.compile(
    r"je\s+(?:dois|ai\s+dû)\s+me\s+tromper|je\s+me\s+suis\s+trompée"
    r"|machinalement|sans\s+(?:y\s+penser|réfléchir)"
    r"|oubli[ée]\s+de\s+(?:le\s+)?noter|me\s+résous\s+à\s+croire"
    r"|j'avais\s+(?:simplement|juste)\s+oublié"
    r"|j'ai\s+dû\s+m'endormir|je\s+me\s+suis\s+endormie", re.IGNORECASE)
# RÉCURSION MÉTAFICTION : le beat re-lit la ligne du beat précédent (« je relis
# la phrase que j'ai écrite hier soir : "…" ») ou reprend le gabarit « je relève
# un détail qui me trouble » — nouvelle forme de litanie (v14). On distingue de
# la relève légitime (« la phrase que je viens de recopier »), qui n'est pas un
# ré-emprunt au passé.
_BEAT_RECURSION = re.compile(
    r"je\s+relis\s+(?:la|cette|ma|une|l')\s*(?:phrase|entrée)\s+"
    r"(?:d'hier|que\s+j'ai\s+[ée]crite?)"
    r"|je\s+rel[èe]ve\s+un\s+d[ée]tail\s+qui\s+me\s+trouble", re.IGNORECASE)
_BEAT_REVEIL = re.compile(
    r"je\s+me\s+suis\s+(?:réveillée|levée)|à\s+mon\s+réveil", re.IGNORECASE)
_BEAT_PRESENCE = re.compile(
    r"\b(?:un\s+bruit|une\s+sonnerie|des\s+pas|une\s+voix|quelqu'un"
    r"|un\s+mouvement\s+qui\s+n'|surprendre)\b", re.IGNORECASE)
_BEAT_DOUTE = re.compile(
    r"je\s+ne\s+me\s+(?:souviens|rappelle)\s+pas|aucun\s+souvenir"
    r"|sans\s+(?:m'en\s+souvenir|le\s+savoir)", re.IGNORECASE)


def _scorer_beat(variant: str, est_premier: bool,
                 chapitre: int = 2) -> tuple[int, list[str]]:
    """Note un variant de beat par contrôles de lecture. Plus haut = mieux.

    Falsifié dans les deux sens (doctrine 4) : il DOIT rejeter les paragraphes
    de résolution / présence / redémarrage / récursion / décor interdit des
    tirages v8–v14 et ACCEPTER le doute ouvert. Le redémarrage (réveil) n'est un
    défaut que HORS premier beat.
    """
    defauts: list[str] = []
    score = 0
    if _BEAT_RESOUT.search(variant):
        score -= 10
        defauts.append("résout (souvenir retrouvé / verdict rendu)")
    if _BEAT_DISMISS.search(variant):
        score -= 4
        defauts.append("congédie (je dois me tromper / je me suis endormie)")
    if not est_premier and _BEAT_REVEIL.search(variant):
        score -= 5
        defauts.append("redémarre (réveil déjà servi)")
    if _BEAT_PRESENCE.search(variant):
        score -= 5
        defauts.append("présence perçue")
    if _BEAT_RECURSION.search(variant):
        score -= 6
        defauts.append("récursion (re-lit sa propre ligne / gabarit répété)")
    # DÉCOR INTERDIT : le détecteur existe déjà (`interdits_materiels`), on le
    # BRANCHE dans la sélection. Un beat qui nomme la télévision, le
    # lave-vaisselle, le sac à main… ne doit jamais gagner (v14 : il a gagné).
    interdits = interdits_materiels(variant, chapitre)
    if interdits:
        score -= 8
        defauts.append(f"décor interdit ({len(interdits)})")
    if _BEAT_DOUTE.search(variant):
        score += 3
    return score, defauts


# CRITÈRE de l'entrée 1 (best-of-N sur le chemin entrée-entière). L'entrée lue
# à voix nue doit nommer l'EFFACEMENT DE L'ANNIVERSAIRE (photos rangées, musique
# supprimée, plat écarté), pas dériver vers un rangement générique (le cahier,
# le grenier) — dérive mesurée aux tirages v7/v9/v11. On score la version
# BORNÉE À DEUX PHRASES : c'est ce qui est réellement servi ; l'effacement en
# phrase 3+ est coupé et ne compte pas.
_E1_EFFACEMENT = re.compile(
    r"\b(photos?|playlist|musique|le\s+plat|anniversaire|couverts?)\b",
    re.IGNORECASE)
_E1_DERIVE = re.compile(
    r"ranger\s+le\s+(?:cahier|grenier)|le\s+grenier|dans\s+un\s+album"
    r"|le\s+cahier\s+ailleurs", re.IGNORECASE)


def _scorer_entree1(variant: str) -> tuple[int, list[str]]:
    """Note l'entrée 1 (résolution d'effacement). Falsifié dans les deux sens."""
    defauts: list[str] = []
    score = 0
    if _E1_EFFACEMENT.search(variant):
        score += 3
    else:
        score -= 3
        defauts.append("ne nomme pas l'effacement de l'anniversaire")
    if _E1_DERIVE.search(variant):
        score -= 5
        defauts.append("dérive (cahier / grenier / album)")
    return score, defauts


# FIX RACINE (xp C5, 2026-08-31) : le squelette de voix servi finit par
# « 5. verdict de correction … 7. couperet ». L'xp a mesuré que c'est CE
# squelette (pas le modèle) qui force la résolution du doute — 12/12 tirages
# tiennent le doute quand on ne le sert pas. On l'ampute des étapes 5 et 7 DANS
# LE PROMPT SERVI AUX BEATS du corps, jamais dans la fiche (le squelette reste
# la voix canonique ailleurs). La chute « Constat » reste posée par le code en
# dernier ; l'étape 6 (notation physiologique) est gardée — c'est le beat-corps.
_VOIX_VERDICT = re.compile(
    r"^\s*(?:5\. Le verdict de correction|7\. Le couperet)[^\n]*\n?",
    re.MULTILINE)


_BEAT_SUFFIXE = (
    "Prose seule, en français uniquement, sans en-tête, sans titre, sans "
    "méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi "
    "de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », "
    "pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu "
    "ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — "
    "surtout, elle ne se retourne pas en certitude rassurante. Rien ne se "
    "produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui "
    "agit — tu constates seulement des états trouvés, des choses déplacées ou "
    "laissées, sans surprendre personne."
)


def _prompt_beat(consigne: str, bloc: str) -> str:
    """Assemble le prompt d'UN beat — cap-code structurel de l'entrée 2 (v5).

    Ne sert QUE ce beat et le véto commun, JAMAIS le mouvement entier. Le mode
    segments re-servait `_prompt_mouvement` à chaque segment (intention +
    quatre directives + matière + vétos) avec une simple ligne de position :
    chaque segment tentait donc tout l'arc — c'est la cause mesurée des « trois
    arcs ». Ici chaque appel ne reçoit que sa propre tâche, courte, et le code
    borne la génération en phrases. Le spiral « je vais tout noter » de v5 n'a
    plus d'appel où s'écrire : le beat du doute s'arrête sur sa question, et la
    chute est posée en aval.

    Même garde d'entrée que `_prompt_mouvement` : l'assemblage servi ne doit
    porter aucun terme d'atelier ni de machinerie.
    """
    prompt = "\n\n".join(b for b in (consigne.strip(), bloc.strip(),
                                     _BEAT_SUFFIXE) if b)
    fuites = sorted({m.group(0).lower() for m in META_TERMES.finditer(prompt)}
                    | {m.group(0).lower() for m in MACHINERIE.finditer(prompt)}
                    | set(re.findall(r"\b[\w-]+\.md\b", prompt)))
    assert not fuites, (f"le prompt de beat porte des termes d'atelier ou de "
                        f"machinerie : {fuites}")
    return prompt


def _prompt_mouvement(fiche: dict, mots_cible: str, position: str,
                      bloc_prefixe: str) -> str:
    """Assemble le prompt d'une entrée sous méthode du mouvement.

    Ordre STRICT : intention → trajectoire → matière → vétos. Rien avant
    l'intention ; la matière ne vient qu'après le comportement de la prose,
    parce qu'elle est à disposition et non à cocher.
    """
    blocs = [f"MOUVEMENT À ACCOMPLIR — {fiche['mouvement']}"]
    if fiche.get("trajectoire"):
        blocs.append("COMPORTEMENT DE LA PROSE :\n"
                     + "\n".join(f"  - {_sans_machinerie(d)}"
                                   for d in fiche["trajectoire"]))
    if fiche.get("matiere"):
        blocs.append("MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce "
                     "mouvement, jamais une liste à épuiser :\n"
                     + "\n".join(f"  - {_sans_machinerie(m)}"
                                   for m in fiche["matiere"]))
    forme = fiche.get("forme") or {}
    vetos = [f"Longueur visée : {mots_cible}."]
    if forme.get("verdict") == "absent":
        vetos.append("Aucun verdict ne se rend : la dernière ligne en tient "
                     "lieu, et elle est déjà écrite ailleurs.")
    if forme.get("accumulation") == "absente":
        vetos.append("Pas de phrase-récapitulatif.")
    if fiche.get("vetos"):
        vetos.append(fiche["vetos"])
    # Le libellé aussi est servi : « VÉTOS » est un mot de notre atelier. Ce
    # que le modèle doit lire, c'est ce que le texte ne fait pas.
    blocs.append("CE QUE LE TEXTE NE FAIT PAS :\n"
                 + "\n".join(f"  - {v}" for v in vetos))
    blocs.append(bloc_prefixe.strip() if bloc_prefixe else "")
    blocs.append(position + "\nProse seule, sans titre, sans en-tête, sans "
                 "méta-commentaire.")
    prompt = "\n\n".join(b for b in blocs if b)

    # LA GARDE D'ENTRÉE, sur le prompt ASSEMBLÉ et non sur ses morceaux : c'est
    # l'assemblage qui est servi. Elle a déjà attrapé « matériau » (session 6)
    # et `fiche-romane.md` (session 7) ; élargie à la machinerie, elle attrape
    # les neuf termes que le §5 du brief servait tels quels.
    fuites = sorted({m.group(0).lower() for m in META_TERMES.finditer(prompt)}
                    | {m.group(0).lower() for m in MACHINERIE.finditer(prompt)}
                    | set(re.findall(r"\b[\w-]+\.md\b", prompt)))
    assert not fuites, (f"le prompt servi porte des termes d'atelier ou de "
                        f"machinerie : {fuites}")
    return prompt


def _matiere_reconstruction(state: ChapterState) -> str:
    """La matière propre de l'appel de reconstruction.

    ⚠ Le protocole dit « la micro-scène du chapitre (grade, objet, événement) —
    depuis la table de pilotage ». Pris au mot, cela lit
    `bible/profond/chronologie-partie-double.md`, dont la colonne « Événement
    réel payeur » est LA COLONNE RÉELLE de la partie double : la vérité que tout
    le firewall existe pour cacher au modèle auteur. Inoffensive par coïncidence
    au chapitre 2, elle dit « *ce genre de veuve* écrit » au chapitre 3.

    C'est l'erreur exacte de la session 5, où la traduction diégétique lisait
    cette colonne et sortait « le journal prescrit ». On passe donc par les deux
    fonctions qui savent déjà où regarder : `lire_table` (qui SAUTE cette
    colonne, commentaire à l'appui) et `lire_ancres`, qui lit l'Ancre du bloc
    [VALEURS] — l'événement tel que la narratrice le PERÇOIT.

    Les interdits matériels sont servis en CATÉGORIES, jamais en instances.
    Nommer « télévision » et « sac à main » pour les interdire, c'est les
    montrer, et le projet a mesuré trois fois que ce qui est montré se recopie.
    Ce qui tient l'interdit est le validateur d'`accumulate`, bloquant ; le
    prompt ne fait que préparer le terrain — en donnant du mobilier RÉEL, parce
    que le nœud inventait faute d'en avoir.
    """
    ch = state.get("chapitre") or 2
    objets = state.get("objets_actifs") or ""
    lignes = []
    try:
        from build_etat_narratif import lire_ancres, lire_table
        table, ancres = lire_table().get(ch) or {}, lire_ancres()
        objets = objets or table.get("objets", "")
        if ancres.get(ch):
            lignes.append(f"Où elle en est ce soir : {ancres[ch]}.")
        if table.get("marche"):
            lignes.append(f"Ce par quoi elle explique l'écart : "
                          f"{table['marche']}.")
    except Exception as exc:                       # pragma: no cover
        # Un échec de lecture ne doit pas coûter l'entrée : on écrit sans cette
        # matière, en le DISANT. Un contexte silencieusement amputé est ce qui a
        # produit le manuscrit intérieur de B′C.
        progress.note(f"matière de reconstruction indisponible ({exc}) — "
                      "l'appel se fait sans elle")
    if objets:
        lignes.append(f"Dans cette maison, ce soir : {objets}.")
    lignes.append(
        "Elle travaille chez elle et ne sort pas ce soir-là ; personne d'autre "
        "n'entre ; il n'y a aucun écran dans cette maison, et rien qui vienne "
        "d'un magasin. Tout ce qu'elle touche est déjà là.")
    return "\n".join(lignes) + "\n"


def _vetos_de_scene(text: str, idx: int, state: ChapterState,
                    tentative: int) -> tuple[str, list[str]]:
    """Signale le décor générique et les marques dans le texte d'écriture.

    On SIGNALE sans réécrire : contrairement à l'en-tête ou à l'ancre, le code
    n'est pas propriétaire de ces phrases — retirer « l'enceinte Bluetooth »
    laisserait un trou dans une phrase qu'il faudrait recoudre, et recoudre de
    la prose est exactement ce qu'on refuse de faire depuis six sessions.
    L'avertissement nomme l'objet et cite l'extrait ; le véto vit dans la grille.
    """
    warns: list[str] = []
    ch = state.get("chapitre") or 2
    for extrait in interdits_materiels(text, ch):
        warns.append(f"entrée {idx + 1} : VÉTO décor — {extrait[:110]}")
    for m in MARQUES.finditer(text):
        a = max(0, m.start() - 40)
        warns.append(f"entrée {idx + 1} : VÉTO marque déposée — "
                     f"« {' '.join(text[a:m.end() + 30].split())} »")
    return text, warns


def _borner_en_phrases(text: str, maxi: int, idx: int,
                       prefixe: str) -> tuple[str, list[str]]:
    """Coupe l'entrée à `maxi` phrases APRÈS le préfixe, sur une fin de phrase.

    Le préfixe (en-tête, ancre) n'est pas compté : il est posé par le code, il
    n'appartient pas au texte que le brief borne.
    """
    corps = text[len(prefixe):] if prefixe and text.startswith(prefixe) else text
    fins = sentence_ends(corps)
    if len(fins) <= maxi:
        return text, []
    coupe = fins[maxi - 1]
    retire = corps[coupe:].strip()
    return (text[:len(text) - len(corps)] + corps[:coupe].rstrip(),
            [f"entrée {idx + 1} : bornée à {maxi} phrase(s) — "
             f"{len(fins) - maxi} retirée(s), à partir de "
             f"« {' '.join(retire.split())[:80]}… »"])


def _nettoyer_segment(seg: str, label: str) -> tuple[str, list[str]]:
    """Retire du segment les marqueurs dont le CODE est propriétaire.

    Appliqué segment par segment, et non seulement sur l'entrée assemblée : un
    en-tête réémis en tête de la reconstruction deviendrait le préfixe de la
    fermeture, qui le lirait comme du texte légitime déjà écrit et enchaînerait
    dessus. Le code propriétaire d'un marqueur doit le nettoyer partout — et
    « partout » inclut les états intermédiaires.
    """
    warns: list[str] = []
    seg, repetees = SUSPENSION_REPETEE.subn(r"\1", seg)
    seg, isolees = SUSPENSION_PARASITE.subn(", ", seg)
    if repetees + isolees:
        warns.append(f"{label} : {repetees + isolees} point(s) de suspension "
                     "produit(s) par le modèle, retiré(s) — le marqueur est "
                     "réservé au glissement, que le code compose")
    seg, retires = ENTETE_PARASITE.subn("", seg)
    if retires:
        warns.append(f"{label} : {retires} en-tête(s) daté(s) produit(s) par le "
                     "modèle, retiré(s) — le code compose les en-têtes")
    return seg.strip(), warns


# LA GARDE D'ENTRÉE EST LE LINT DE SORTIE. Le détecteur qui attrape « Couperet »
# dans le texte est celui qui aurait dû interdire de le servir.
for _nom, _, _, _consigne in SEGMENTS:
    _fuites = sorted({m.group(0).lower() for m in META_TERMES.finditer(_consigne)})
    assert not _fuites, (f"consigne du segment « {_nom} » : termes d'atelier "
                         f"servis au modèle — {_fuites}")


# --- Micro-nœuds d'assemblage (étage C) --------------------------------------
#
# Le reproche ne MONTRE aucun texte d'exemple. La session 3 a mesuré qu'un
# étalon montré se recopie caractère pour caractère, et `valider_accumulation`
# le détecte. On décrit le mouvement, on chiffre la contrainte, on ancre dans
# les objets de l'entrée.
# LA CHUTE EST IMPOSÉE (session 6, §3.1). « celui qui cloche » laissait le
# modèle choisir l'anomalie, et il en choisissait une à lui — un robinet resté
# ouvert (C1). L'anomalie du chapitre est un fait du roman, pas une trouvaille
# de fin de phrase : elle se donne, comme le verdict et le fait imposé.
_CHUTE_IMPOSEE = {
    2: "l'assiette",
    # Chapitre 7 : la chute tombe sur un objet du quatuor, celui que le brief
    # rend le plus contradictoire — elle a décidé de supprimer la playlist, et
    # la musique tourne.
    7: "la playlist qui tourne encore",
}

_ACC_CONSIGNE = """Voici la partie d'une entrée de carnet où la narratrice \
rétablit sa soirée.

Écris UNE SEULE PHRASE qui reprenne, dans l'ordre, les faits de cette soirée : \
le retour, les gestes, les objets, les heures — jusqu'à celui qui cloche, sur \
lequel la phrase s'achève.

L'étape qui cloche, imposée : {chute}. La phrase finit sur elle.
Les objets de cette maison, les seuls : {objets}.

Contraintes, vérifiées :
- une seule phrase : AUCUN point, aucun point-virgule à l'intérieur ;
- **au moins DOUZE étapes**, chacune séparée par une simple virgule — l'heure \
du retour, un geste, un objet, une pièce, un autre geste, et ainsi de suite \
jusqu'au coucher ;
- pas de « et » ni de « puis » pour les relier : la virgule seule ;
- puis la rupture (« sauf une, une seule ») et l'étape qui cloche ;
- entre douze et vingt étapes : au-delà, c'est un emballement, pas une spirale ;
- uniquement des faits DE CE TEXTE, aucun objet ni lieu nouveau ;
- l'absente ne se qualifie JAMAIS au masculin — ni « mari », ni « lui », ni \
« il » : la maison a été partagée avec une femme. Mais la phrase n'a besoin \
que de SES gestes à elle ; l'absente n'a pas à y figurer ;
- des ÉTAPES, pas des états d'âme : ce qu'elle fait et ce qu'elle touche, \
jamais ce qu'elle ressent ni ce qu'elle conclut.

Rends la phrase seule, rien d'autre."""

# La consigne du glissement a été RETIRÉE, pas commentée : le geste ne se
# demande plus au modèle, il se prend en banque (cf. `glisse_node`). Une
# consigne morte laissée en place se relit un jour comme une consigne active.



def _gestes_permis(state: ChapterState) -> bool:
    """Cette entrée accueille-t-elle les gestes signatures ?

    Le chapitre 7 le décide par entrée : l'entrée 1 tient en deux phrases,
    elle n'a la place ni d'une accumulation ni d'un glissement. Au tirage
    précédent, l'accumulation y a été épissée quand même — 471 mots au lieu de
    deux phrases, et c'est par elle que « les courses » et « la télévision »
    sont entrés dans le chapitre.
    """
    spec = state.get("entrees_spec") or []
    idx = len(state["scenes"]) - 1
    if idx < 0 or idx >= len(spec):
        return True
    return bool(spec[idx].get("gestes", True))


def accumulate_node(state: ChapterState) -> dict:
    """Produit la phrase d'accumulation. Le CODE la valide et la placera.

    Quatre sessions ont établi qu'elle ne s'obtient ni par la fiche (trois
    formulations) ni par une boucle de reproche (jamais une authentique). Elle
    est donc assemblée : le modèle fournit la matière, le code la forme.
    """
    if not state.get("micro_noeuds") or not state["scenes"]:
        return {}
    if not _gestes_permis(state):
        return {}
    # LE CONTEXTE EST LE SEGMENT DE RECONSTRUCTION, plus l'entrée entière.
    # `accumulate` était devenu le canal de famine de l'étage C : il ne recevait
    # que l'entrée et une consigne de forme, donc quand la reconstruction était
    # mince il inventait les étapes manquantes depuis ses priors — télévision et
    # messages (C1), « revenue du travail » (C3), sac à main et barquette (CC).
    # Le monde générique de nemo, chassé de `write` par le RAG, rentrait par ici.
    # Le découpage de `write` rend ce segment identifiable sans le deviner.
    entree = state.get("reconstruction") or state["scenes"][-1]
    consigne = _ACC_CONSIGNE.format(
        objets=state.get("objets_actifs") or "le cahier, l'assiette, l'égouttoir",
        chute=_CHUTE_IMPOSEE.get(state.get("chapitre") or 2, "celui qui cloche"))
    metrics, warns, phrase = [], [], ""
    for essai in range(1, MAX_TENTATIVES_GESTE + 1):
        progress.phase("Accumulation",
                       f"entrée {len(state['scenes'])} (essai {essai})")
        txt, m = chat(consigne, entree, model=MODELE_GESTES,
                      temperature=TEMP_GESTES, num_predict=300)
        metrics.append(m)
        candidat = " ".join(txt.strip().split())
        # L'accumulation est un AUTRE nœud, posé APRÈS le `delint` du write —
        # les collages « j'aiallumé » y survivaient. On nettoie ici, avant la
        # validation (pour que le compte de mots porte sur le texte corrigé).
        candidat, _ = delint(candidat)
        # Compter des ÉTAPES est une opération que le modèle sait faire ;
        # compter des MOTS non — il rendait 48 mots pour un plancher de 60,
        # deux fois de suite. Le code, lui, continue de vérifier en mots : la
        # consigne vise ce qui est atteignable, la garde mesure ce qui compte.
        ok, raison = valider_accumulation(
            candidat, dernier_essai=(essai == MAX_TENTATIVES_GESTE),
            chapitre=state.get("chapitre") or 2)
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
    """Compose le glissement DEPUIS LA BANQUE, puis met les gestes de côté.

    LE GESTE A QUITTÉ LE MODÈLE (session 6, §2). Onze runs, trois modes d'échec
    distincts, zéro glissement : la difficulté n'est pas la longueur mais la
    NATURE de la demande — approcher un sujet puis s'interrompre est un geste de
    sens, pas de forme. La matière est donc écrite main, dans `BANQUE_GLISSEMENT`,
    et le code choisit, coupe et colle. C'est la doctrine des citations du
    cahier, étendue : ce qu'il y a de plus intime dans le roman est déjà écrit.

    Ce nœud ne fait plus AUCUN appel au modèle. Il en reste un nœud parce que
    l'assemblage doit vivre après `accumulate` : les deux positions se calculent
    sur le texte ORIGINAL, et si `accumulate` avait déjà inséré sa phrase, les
    offsets du glissement porteraient sur un texte décalé.
    """
    if not state.get("micro_noeuds") or not state["scenes"]:
        return {}
    if not _gestes_permis(state):
        # L'entrée n'accueille pas de geste : on pousse un jeu VIDE pour que
        # l'indexation de `gestes` reste alignée sur celle des entrées. Sans ce
        # jeu vide, les gestes de l'entrée 2 seraient posés dans l'entrée 1.
        gestes = list(state.get("gestes") or [])
        gestes.append({})
        return {"gestes": gestes, "accumulation": ""}
    warns: list[str] = []
    spec = state.get("entrees_spec") or []
    idx = len(state["scenes"]) - 1
    fiche = spec[idx] if 0 <= idx < len(spec) else {}

    # PASSAGE RÉDIGÉ (méthode du mouvement) : le brief le fournit entier, avec
    # sa frontière. Plus de suture approche + « … » + fait — l'interruption
    # porte l'approche et le retour au matériel EST la découverte suivante.
    # Les deux formes cohabitent : la banque reste pour les chapitres non
    # migrés, et c'est la présence du champ qui tranche.
    if fiche.get("glissement", {}).get("texte"):
        passage = fiche["glissement"]["texte"]
        ok, raison = passage_valide(passage)
        if not ok:
            warns.append(f"glissement entrée {idx + 1} : passage REFUSÉ par "
                         f"son validateur — {raison}")
            passage = ""
        gestes = list(state.get("gestes") or [])
        gestes.append({"accumulation": state.get("accumulation") or "",
                       "glissement": passage,
                       "frontiere": fiche["glissement"].get("position", ""),
                       "reconstruction": state.get("reconstruction") or "",
                       "entete": state.get("entete_pose") or "",
                       "ancre": state.get("ancre_posee") or "",
                       "chute": state.get("chute_posee") or ""})
        return {"gestes": gestes, "accumulation": "",
                "warnings": state["warnings"] + warns}

    tirees = list(state.get("approches_tirees") or [])
    approche, fait = tirer_approche(state.get("chapitre") or 2, tirees,
                                   state.get("graine") or 0)
    glissement = ""
    if approche:
        progress.phase("Glissement", f"entrée {len(state['scenes'])} (banque)")
        # Le fait matériel se prend dans les objets actifs quand le chapitre en
        # donne d'autres que celui de la banque — la variation reste possible
        # sans que la forme dépende du modèle.
        glissement = composer_glissement(approche, fait)
        tirees.append(approche)
    else:
        warns.append(f"glissement entrée {len(state['scenes'])} : aucune "
                     "approche disponible en banque pour ce chapitre — M1 se "
                     "lit « non prévu », pas « manqué »")

    # Les fragments sont MIS DE CÔTÉ, pas insérés ici. Posés dans `scenes`, ils
    # traversaient ensuite `review` (« resserre la prose ») et `repair` — qui
    # réécrivent l'entrée entière et dissolvaient l'accumulation : une phrase de
    # soixante mots est précisément ce qu'une consigne de resserrement casse. Le
    # geste se pose donc sur le texte FINAL, dans `poser_gestes`.
    gestes = list(state.get("gestes") or [])
    gestes.append({"accumulation": state.get("accumulation") or "",
                   "glissement": glissement,
                   "reconstruction": state.get("reconstruction") or "",
                   "entete": state.get("entete_pose") or "",
                   "ancre": state.get("ancre_posee") or "",
                   "chute": state.get("chute_posee") or ""})
    return {"gestes": gestes, "accumulation": "", "approches_tirees": tirees,
            "warnings": state["warnings"] + warns}


# Un en-tête daté, même MAL FORMÉ — virgule au lieu du point, minuscule à la
# météo. C'est ce que le tampon doit reconnaître pour le remplacer plutôt que
# d'en ajouter un second à côté.
ENTETE_APPROCHANT = re.compile(
    r"^\s*(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d{1,2}"
    r"\s*[.,;:]?\s*\S", re.IGNORECASE)


def _retamponner(entree: str, *, tete: str, ancre: str) -> tuple[str, list[str]]:
    """Repose l'en-tête et l'ancre, exactement, en tête de l'entrée.

    Le code POSSÈDE ces deux marqueurs. Le préfixage par concaténation réelle
    (session 5) les rendait inaltérables pendant l'écriture — mais `review` et
    `repair` reçoivent l'entrée ENTIÈRE et la réécrivent, ancre comprise. Mesuré :
    0/3 verbatim à B′, 2/3 à l'étage C, ✗ sur S6-1, où les guillemets français
    étaient devenus droits.

    L'enjeu n'est pas typographique. `chapitre.py` et `lire_chapitre.py` placent
    la bascule audio sur l'en-tête normalisé : un en-tête réécrit, c'est une
    bascule perdue sur scène.

    On remplace le premier bloc s'il RESSEMBLE à ce qu'on repose (le modèle l'a
    altéré) ; on l'insère s'il a disparu.
    """
    notes: list[str] = []
    paras = [p for p in entree.split("\n\n") if p.strip()]

    def poser(attendu: str, reconnait, quoi: str) -> None:
        if not attendu:
            return
        for k, para in enumerate(paras[:3]):
            if para.strip() == attendu.strip():
                return                          # déjà exact, rien à faire
            if reconnait(para):
                if difflib.SequenceMatcher(None, para.strip(),
                                           attendu.strip()).ratio() > 0.55:
                    notes.append(f"{quoi} re-tamponné — le texte portait "
                                 f"« {' '.join(para.split())[:70]} »")
                    paras[k] = attendu
                    return
        # Disparu : on le repose en tête, dans l'ordre en-tête puis ancre.
        notes.append(f"{quoi} ABSENT après réparation — reposé par le code")
        paras.insert(0 if quoi == "en-tête" else min(1, len(paras)), attendu)

    # Le reconnaisseur d'en-tête accepte AUSSI la forme abîmée : `ENTETE_ENTREE`
    # exige le point, or c'est précisément la virgule que la réparation
    # introduit (B′C : « Lundi 2, nuageux. »). Ne reconnaître que la forme
    # correcte faisait INSÉRER le bon en-tête sans retirer le mauvais — deux
    # en-têtes, soit le défaut que ce tampon existe pour éteindre.
    poser(tete,
          lambda p: bool(ENTETE_ENTREE.match(p.strip()))
          or bool(ENTETE_APPROCHANT.match(p.strip())), "en-tête")
    poser(ancre, lambda p: re.match(r'^\s*[«"“]', p.strip()), "ancre")
    # L'ANCRE EN DOUBLE. Le code la pose en tête ; le modèle l'a parfois
    # recopiée juste après, en ouverture de son propre texte. Deux fois la même
    # citation à trois lignes d'intervalle se lit comme un bégaiement — et sur
    # le chapitre 7, c'est la ligne la plus chargée du roman.
    if ancre:
        noyau = " ".join(ancre.split()).strip('«»"“” ')
        garde, vue = [], False
        for para in paras:
            plat = " ".join(para.split()).strip('«»"“” ')
            if plat and (plat in noyau or noyau in plat):
                # La PREMIÈRE est l'ancre que le code vient de poser ; les
                # suivantes sont les recopies du modèle. Garder la première et
                # non « toutes sauf le premier paragraphe » : l'en-tête occupe
                # déjà l'index 0, et la version naïve retirait les DEUX copies.
                if vue:
                    notes.append("ancre recopiée par le modèle — doublon retiré")
                    continue
                vue = True
            garde.append(para)
        paras = garde
    return "\n\n".join(paras), notes


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
        # BORNES DE LA RECONSTRUCTION, retrouvées par RECHERCHE et non par
        # comptage d'offsets : entre la génération et ici, le texte a traversé
        # `review` puis `repair`, qui le réécrivent. Des offsets mémorisés
        # pointeraient à côté ; le début du segment, lui, survit assez pour être
        # retrouvé — et s'il ne survit pas, le repli lexical joue.
        recon = (g.get("reconstruction") or "").strip()
        bornes = None
        if recon:
            tete = " ".join(recon.split()[:6])
            # `debut`, PAS `i` : la version précédente écrasait l'index de la
            # boucle avec un offset de caractère, si bien que les avertissements
            # d'assemblage annonçaient « entrée 26 » sur un run d'UNE entrée
            # (relevé tel quel dans S6-2). Un message qui désigne la mauvaise
            # entrée envoie relire le mauvais texte.
            debut = entree.find(tete)
            if debut >= 0:
                bornes = (debut, debut + len(recon))

        # LE TAMPON (session 7). Le code est PROPRIÉTAIRE de l'en-tête et de
        # l'ancre : le préfixage les garantissait jusqu'à la fin de l'écriture,
        # mais `review` et `repair` repassent sur l'entrée entière et les
        # réécrivent — guillemets français devenus droits, 0/3 verbatim à B′,
        # ✗ sur S6-1. Ce nœud est le dernier à toucher le texte : il les repose.
        entree, notes_tampon = _retamponner(
            entree, tete=g.get("entete") or "", ancre=g.get("ancre") or "")

        # LA CHUTE, POSÉE PAR LE CODE quand le brief l'impose au mot près.
        #
        # « Constat : anniversaire. » est la dernière ligne du chapitre 7 et le
        # point de bascule du roman : le jour gagne en entrant dans son
        # vocabulaire. Le modèle l'a manquée TROIS fois sur trois — il referme
        # sur une ligne du corps et s'arrête là.
        #
        # Même raisonnement que pour l'en-tête et l'ancre : ce dont la scène
        # dépend au mot près ne se demande pas, il se compose. Et comme eux,
        # elle se pose EN DERNIER, après la réparation qui la réécrirait.
        chute = (g.get("chute") or "").strip()
        if chute and chute not in entree:
            entree = entree.rstrip() + "\n\n" + chute
            notes_tampon.append(f"chute imposée absente — posée par le code : "
                                f"« {chute} »")

        # LA FRONTIÈRE DÉCLARÉE prime sur le calcul d'offset : elle est un
        # lieu du récit, pas une position dans le texte. Si l'ancre est
        # introuvable, on le DIT et on retombe sur l'offset — un geste placé au
        # hasard est pire qu'un geste absent, mais un geste tu est pire encore.
        frontiere = None
        if g.get("frontiere") and g.get("glissement"):
            frontiere = position_frontiere(entree, g["frontiere"])
            if frontiere is None:
                warns.append(f"assemblage entrée {i + 1} : frontière « "
                             f"{g['frontiere'][:60]} » introuvable dans le "
                             "texte — repli sur le placement par offset")
        texte, notes = assembler(entree, g.get("accumulation") or "",
                                 g.get("glissement") or "",
                                 state.get("verdict") or "", bornes,
                                 frontiere=frontiere)

        # LE DÉDOUBLONNAGE, en dernier — après les gestes, pour que les
        # paragraphes composés soient dans le texte et donc explicitement
        # protégés. Falsifié sur S6-C : sans protection, les trois plus fortes
        # similarités du chapitre étaient l'en-tête, l'ancre et le glissement.
        proteges = tuple(x for x in (g.get("accumulation"), g.get("glissement"),
                                     g.get("ancre"), g.get("entete")) if x)
        for _, j, ratio, _ in reversed(paragraphes_redits(texte,
                                                          proteges=proteges)):
            paras = [p for p in texte.split("\n\n") if p.strip()]
            if j >= len(paras):
                continue
            retire = paras.pop(j)
            texte = "\n\n".join(paras)
            # Dire CE QU'ON RETIRE : la règle du filet de coupe depuis la
            # session 4. Un retrait muet est indistinguable d'un modèle qui
            # n'aurait rien écrit là.
            notes.append(f"paragraphe redit retiré ({ratio}) — « "
                         f"{' '.join(retire.split())[:90]}… »")

        sorties.append(texte)
        warns += [f"assemblage entrée {i + 1} : {n}"
                  for n in notes + notes_tampon]
        if not (g.get("accumulation") or "").strip():
            warns.append(f"assemblage entrée {i + 1} : aucune accumulation à "
                         "poser")
    return {"repaired": sorties, "warnings": state["warnings"] + warns}


def route_after_write(state: ChapterState) -> str:
    """Boucle tant qu'il reste des scènes à écrire, sinon passe à la relecture."""
    return "write" if state["idx"] < len(state["plan"]) else "review"


def _cible_entree(state: ChapterState, i: int) -> tuple[int, int]:
    """Fourchette de mots de l'entrée `i` — celle du brief si elle en donne une."""
    spec = state.get("entrees_spec") or []
    if i < len(spec) and spec[i].get("mots"):
        return tuple(spec[i]["mots"])
    return MOTS_PAR_ENTREE


def _coupe_acceptable(avant: int, apres: int, cible: tuple[int, int]) -> bool:
    """Une coupe qui RAPPROCHE de la cible est bonne, si profonde soit-elle.

    Le seuil des 60 % existe contre l'escamotage : une passe de réécriture ne
    doit pas faire disparaître l'entrée. Mais il ne regardait que la PROFONDEUR
    de la coupe, jamais sa DIRECTION — et il a coûté cher.

    Mesuré sur S6-C : `review` a taillé l'entrée 1 de 1033 à 495 mots et
    l'entrée 3 de 1567 à 709. Les deux visaient 450-600, les deux ont été
    rejetées (48 %, 45 %), et le chapitre est resté à 1008 mots par entrée.
    La relecture faisait exactement le travail qu'on lui demande — corriger une
    masse en excès — et le garde-fou l'en a empêchée deux fois.

    La règle devient : si le texte relu tombe DANS la cible, ou s'en approche
    sans la traverser par le bas, on accepte quelle que soit la profondeur. Le
    seuil ne s'applique plus qu'aux coupes qui éloignent — celles qui passent
    sous le plancher, qui sont l'escamotage que le garde-fou visait vraiment.
    """
    lo, hi = cible
    if apres >= lo:                 # dans la cible ou encore au-dessus
        return True
    if avant < lo:                  # déjà trop court : toute coupe éloigne
        return apres >= 0.6 * avant
    # La coupe est passée SOUS le plancher : acceptable seulement si elle a
    # moins éloigné qu'elle n'a rapproché.
    return (lo - apres) < (avant - hi) and apres >= 0.6 * avant


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
        # LA CIBLE DE CETTE ENTRÉE, pas celle du chapitre. Sur le ch. 7,
        # l'entrée 1 vise 25-60 mots : la relecture l'avait ramenée de 315 à
        # 156 — vers le brief — et le garde l'a rejetée en la comparant à
        # 450-600. Un garde-fou « conscient de la cible » qui lit la mauvaise
        # cible combat exactement ce qu'il est censé servir.
        cible = _cible_entree(state, i)
        if not _coupe_acceptable(avant, apres, cible):
            warns.append(
                f"relecture entrée {i + 1}: garde-fou déclenché "
                f"({apres} mots contre {avant}, soit {apres / max(avant, 1):.0%} "
                f"— hors cible {cible[0]}-{cible[1]}) "
                "— relecture REJETÉE, original conservé"
            )
            text = scene
        elif apres < 0.6 * avant:
            warns.append(
                f"relecture entrée {i + 1}: coupe profonde ACCEPTÉE "
                f"({apres} mots contre {avant}) — elle rapproche de la cible")
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
        # LA CIBLE DE CETTE ENTRÉE, pas celle du chapitre. Sur le ch. 7,
        # l'entrée 1 vise 25-60 mots : la relecture l'avait ramenée de 315 à
        # 156 — vers le brief — et le garde l'a rejetée en la comparant à
        # 450-600. Un garde-fou « conscient de la cible » qui lit la mauvaise
        # cible combat exactement ce qu'il est censé servir.
        cible = _cible_entree(state, i)
        if not _coupe_acceptable(avant, apres, cible):
            warns.append(
                f"réparation entrée {i + 1}: garde-fou déclenché "
                f"({apres} mots contre {avant}, soit {apres / max(avant, 1):.0%} "
                f"— hors cible {cible[0]}-{cible[1]}) "
                "— réparation REJETÉE, texte relu conservé"
            )
            text = scene
        elif apres < 0.6 * avant:
            warns.append(
                f"réparation entrée {i + 1}: coupe profonde ACCEPTÉE "
                f"({apres} mots contre {avant}) — elle rapproche de la cible")
        # Re-lint pour tracer ce qui resterait (anglais tenace, tokens collés).
        text, w = delint(text)
        warns.extend(f"réparation entrée {i + 1}: {x}" for x in w)
        repaired.append(text)
    return {"repaired": repaired, "metrics": metrics, "warnings": warns}


def _phrase_protegee(phrase: str) -> bool:
    """Phrases que la suppression ne touche JAMAIS, même si Qwen les signale :
    en-tête, citation du cahier, fragments de glissement (« … »), chute."""
    n = phrase.strip()
    return bool(re.match(r"[A-ZÉÈ][a-zé]+ \d+\.", n)   # en-tête « Samedi 14. »
                or "…" in n
                or n.startswith("Constat")
                or ("«" in n and "»" in n))            # citation entre guillemets


# PRUNING DÉTERMINISTE du résidu diffus. Qwen a été falsifié dans les deux
# rôles — éditeur (coupe le bon) ET détecteur (« NON » sur « le départ, la
# réunion, la départementale, le garage » : il ne relie pas une reconstruction
# oblique à une sortie). Le code, lui, matche les marqueurs sans ambiguïté. Une
# phrase qui touche UN motif est retirée en entier. Whack-a-mole, mais FIABLE.
_PRUNE_MOTIFS = {
    "sortie": re.compile(
        r"\b(r[ée]union|d[ée]partementale|au\s+travail|au\s+bureau|"
        r"le\s+garage|la\s+buanderie|le\s+d[ée]jeuner|le\s+trajet|"
        r"sept\s+heures\s+quarante|le\s+retour\s+par)\b", re.IGNORECASE),
    "présence": re.compile(
        r"\b(un\s+bruit|des\s+bruits|des\s+pas\b|une\s+sonnerie|quelqu'un|"
        r"une\s+voix|qui\s+rentrait|porter\s+mes\s+cl[ée]s|une?\s+invit[ée]e?)\b",
        re.IGNORECASE),
    # Même détection que le scorer : une seule regex, alignée par construction.
    "récursion": _BEAT_RECURSION,
    "résolution": re.compile(
        r"je\s+n'ai\s+pas\s+r[êe]v[ée]|ma\s+m[ée]moire\s+(?:m'a\s+jou|me\s+joue)"
        r"|je\s+me\s+souviens\s+(?:maintenant|soudain|enfin)"
        r"|tout\s+est\s+normal", re.IGNORECASE),
}


def _assembler_qwen(entree: str) -> tuple[str, list[str]]:
    """Pruning code du résidu diffus. Nom conservé pour l'appelant.

    Retire les phrases qui touchent un motif nommé (sortie / présence /
    récursion / résolution), protège en-tête/citation/glissement/chute, et
    refuse de retirer plus de la moitié (garde de sécurité — au pire, no-op).
    """
    paras_out, retirees = [], []
    for para in entree.split("\n\n"):
        gardees = []
        for ph in re.split(r"(?<=[.!?…»])\s+", para.strip()):
            if not ph.strip():
                continue
            motif = next((k for k, rx in _PRUNE_MOTIFS.items() if rx.search(ph)),
                        None)
            if motif and not _phrase_protegee(ph):
                retirees.append(f"[{motif}] " + " ".join(ph.split())[:45])
            else:
                gardees.append(ph.strip())
        if gardees:
            paras_out.append(" ".join(gardees))
    sortie = "\n\n".join(paras_out).strip()

    if not retirees:
        return entree, ["pruning : rien à retirer"]
    if len(sortie) < 0.5 * len(entree):
        return entree, [f"pruning : suppression > 50 % ({len(retirees)} "
                        "phrases) — REJETÉ, original conservé"]
    return sortie, [f"pruning : {len(retirees)} phrase(s) retirée(s) — "
                    + " | ".join(retirees)]


def assemble_node(state: ChapterState) -> dict:
    """Pruning déterministe du résidu diffus, sur les entrées en beats.

    Placé AVANT `poser_gestes`, sur le CORPS seul (`repaired`) : les gestes
    (glissement, chute, accumulation) ne sont pas encore posés, donc le pruning
    ne peut pas les toucher, et le code les pose propres sur le corps nettoyé.
    """
    if not ASSEMBLAGE_ACTIF or not state.get("micro_noeuds"):
        return {}
    entrees = state.get("repaired") or []
    spec = state.get("entrees_spec") or []
    if not entrees:
        return {}
    sorties, warns = list(entrees), []
    for i, entree in enumerate(entrees):
        fiche = spec[i] if i < len(spec) else {}
        if not fiche.get("beats"):        # seule l'entrée en beats est nettoyée
            continue
        progress.phase("Assemblage", f"entrée {i + 1} (Qwen)")
        sorties[i], w = _assembler_qwen(entree)
        warns += w
    return {"repaired": sorties, "warnings": state["warnings"] + warns}


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
    g.add_node("assemble", assemble_node)
    # AVANT poser_gestes : `repaired` est le CORPS seul, les gestes (glissement,
    # chute, accumulation) ne sont pas encore posés — Qwen ne peut donc pas les
    # abîmer, et le code les pose PROPRES sur le corps nettoyé. repair est déjà
    # Qwen : pas de swap nemo supplémentaire.
    g.add_edge("repair", "assemble")
    g.add_edge("assemble", "poser_gestes")
    g.add_edge("poser_gestes", "coherence")
    g.add_edge("coherence", END)
    return g.compile()
