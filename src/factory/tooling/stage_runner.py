#!/usr/bin/env python3
"""Session 4 — exécution des étages A et B par la pipeline LangGraph.

Contrairement aux sessions 1 à 3, qui frappaient Ollama en direct avec la fiche
entière en Modelfile, la session 4 passe par le graphe complet
(`plan → write → review → repair → coherence`). C'est la machine qu'on mesure,
plus le plafond du modèle.

Les deux étages ne diffèrent QUE par `rag` :
  - étage A : `rag=False`, aucun appel à Chroma ni au modèle d'embedding — le
    contexte narratif se limite au brief ;
  - étage B : `rag=True`, collections indexées.

Les briefs sont lus dans `experiments/reports/protocole-calibration-ch2.md` (§3 du protocole
de session pour la version 2) : ils ne sont pas recopiés ici, pour qu'un brief
modifié n'ait pas deux vérités.

Usage :
  python3 outillage/run_s4.py --etage A                 # A1-A3 + AC
  python3 outillage/run_s4.py --etage A --seulement A1
  python3 outillage/run_s4.py --etage B

Stdlib + le venv de l'orchestrateur (langgraph, chromadb).
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from factory.paths import REPO_ROOT as RACINE

from factory.eval.lint import META_TERMS, analyze
from factory.retrieval import context as retrieval
from factory.text import ends_mid_sentence
from factory.infra.preflight import PreflightError, preflight
# La spécification du chapitre 7 vit dans orchestrator/ch7.py — source unique
# partagée avec le chemin live de l'API (voir le module). NARRATRICE y est aussi
# (le doc_id de la narratrice vaut pour TOUS les étages, pas seulement le ch. 7).
from factory.chapter_spec.chapter7 import (
    NARRATOR, ENTRIES_CH7, beats_chapter_7, brief_chapter_7,
    VERDICT_CH7, OBJECTS_CH7,
)

# Le brief v2 du chapitre 2 — §3 du protocole de session, verbatim. Il vaut
# pour les runs SCORÉS des deux étages.
BRIEF_V2 = (
    "Chapitre 2, entrée unique du carnet, 450-600 mots. En-tête imposé, "
    "première ligne exacte : « Mardi 12. Ciel couvert. »\n"
    "Squelette, dans l'ordre : en-tête → citation → constat → reconstruction "
    "→ verdict → notation physiologique → couperet.\n"
    "Citation ancre, recopiée verbatim entre guillemets après l'en-tête : "
    "« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table "
    "jusqu'au matin. »\n"
    "Beats : 1. le rituel posé en une ou deux phrases — elle relit l'entrée "
    "de la veille du cahier, comme chaque soir. 2. La citation, puis le "
    "constat d'écart : sa mémoire dit une assiette, un dîner seule. 3. La "
    "vérification, perceptive : la cuisine, l'égouttoir — regarder, compter ; "
    "la vérification confirme l'entrée, pas sa mémoire. 4. La rationalisation "
    "argumentée : la fatigue, l'automatisme — et la spirale de reprise des "
    "faits dans l'ordre. 5. Verdict : erreur de relevé — la faute est à elle, "
    "pas au texte ; résolution de pointer plus précisément ; physiologie ; "
    "couperet.\n"
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.\n"
    "Interdits : aucun nom propre, aucun dialogue, aucune explication, "
    "« journal » et « journal intime » bannis, aucun terme réservé "
    "(la tierce, l'errata, le bon à tirer)."
)

# Objectif de chapitre pour AC/BC — hors score. Fourni par le propriétaire pour
# lever la contradiction entre le brief v2 (« entrée unique ») et le §4 du
# protocole (« le chapitre 2 complet, trois entrées »).
CHAPTER_GOAL = (
    "Chapitre 2 complet, trois entrées du carnet à dates consécutives, "
    "450-600 mots chacune. Matière du chapitre : la première divergence — "
    "l'entrée relue du cahier mentionne une seconde assiette (ancre, à "
    "recopier verbatim dans l'entrée concernée : « Deux assiettes mises, sans "
    "y penser. Je l'ai laissée sur la table jusqu'au matin. »), vérification "
    "perceptive à la cuisine, rationalisation par la fatigue, verdict : "
    "erreur de relevé, résolution de pointer plus précisément. Interdits du "
    "brief v2 inchangés."
)


# --- Brief v3 (session 5, item 6) -------------------------------------------
#
# Delta sur la v2 : le RÉSULTAT de la vérification devient un fait imposé,
# chiffré, au matériau. M4 (« l'entrée relue a raison contre la mémoire ») a
# cassé deux fois sur trois à l'étage B malgré un beat 3 explicite — le modèle
# résolvait le conflit par tous les canaux sauf celui du roman : l'objet
# disparaissait, ou le corps contredisait le texte. On ne discute pas l'état du
# monde, on le donne.
# L'ancre de CITATION seule : l'en-tête est désormais composé par le code
# (`graph.entete`), plus recopié depuis une constante. Servi aussi aux chapitres
# complets — c'est le vide d'ancre qui avait engendré le manuscrit intérieur de
# B′C.
ANCHOR_CH2 = ("« Deux assiettes mises, sans y penser. Je l'ai laissée sur la "
             "table jusqu'au matin. »")

BRIEF_V3 = BRIEF_V2.replace(
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.",
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.\n"
    "FAIT IMPOSÉ, au matériau : « L'égouttoir, ce soir : deux assiettes. » "
    "La vérification CONSTATE ce fait, elle ne le découvre pas.\n"
    "En-tête : jamais de mois, jamais d'année."
)

# L'objectif de chapitre hérite du même fait imposé.
CHAPTER_GOAL_V3 = CHAPTER_GOAL + (
    " Fait imposé, au matériau : « L'égouttoir, ce soir : deux assiettes. » "
    "En-tête : jamais de mois, jamais d'année."
)

# BRIEF DE L'ÉTAGE C. Il ne demande plus l'en-tête ni la recopie de l'ancre :
# le code les POSE (bloc B et item 5). Les laisser dans le brief a produit, au
# premier run C, un texte à deux en-têtes et deux ancres — le modèle obéissait à
# la consigne, et le code ajoutait la sienne par-dessus. Une consigne et une
# concaténation qui font la même chose se cumulent.

BRIEF_C = (BRIEF_V3
           .replace("En-tête imposé, "
                    "première ligne exacte : « Mardi 12. Ciel couvert. »", "")
           .replace("Citation ancre, recopiée verbatim entre guillemets après "
                    "l'en-tête : « Deux assiettes mises, sans y penser. Je "
                    "l'ai laissée sur la table jusqu'au matin. »\n", "")
           .replace("Squelette, dans l'ordre : en-tête → citation → constat",
                    "L'en-tête et la citation sont DÉJÀ ÉCRITS. Squelette de "
                    "ce qui reste, dans l'ordre : constat"))

# BRIEF V4 — LE SQUELETTE EN LANGUE DU MONDE (session 6, §3.2).
#
# La chaîne de `.replace` s'arrête ici : la traduction touche presque chaque
# ligne, et un empilement de dix remplacements aurait rendu le diff illisible
# précisément là où il compte. Écrit d'un trait, donc, et gardé par une
# assertion plutôt que par la relecture.
#
# Ce que la session 5 avait fait pour l'état narratif, on ne l'avait pas fait
# pour le brief : « Couperet : » est sorti EN TEXTE sur C2 et « Couperet. » sur
# C3, parce que notre propre squelette servi nommait le couperet. Le run C3 est
# le run de voix de la série, et il porte un mot d'atelier au milieu — venu de
# nous, pas du modèle.
#
# Trois traductions et une soustraction :
#   · « notation physiologique → couperet » devient « le corps constate, une
#     ligne ; une phrase brève referme » ;
#   · « Matériau : » devient « Dans la maison, ce soir : » ;
#   · le verdict rejoint la matière servie, dans les mots du personnage — il
#     réparait déjà la régression B′ (verdict absent des trois runs) ;
#   · LA SPIRALE DISPARAÎT du beat 4. Elle appartient à `accumulate` désormais.
#     C'est ce doublon qui faisait raconter sa soirée deux fois à C3 : une
#     consigne et un nœud qui font la même chose se cumulent, ils ne se
#     remplacent pas.
#
# « rationalisation » reste « elle se donne une raison » — et non « elle
# explique », qui aurait contredit l'interdit « aucune explication » deux lignes
# plus bas. Un brief qui se contredit lui-même laisse le modèle choisir.
BRIEF_V4 = (
    "Chapitre 2, entrée unique du carnet, 450-600 mots.\n"
    "L'en-tête et la citation sont DÉJÀ ÉCRITS.\n"
    "Ce qui reste, dans l'ordre : elle relit, constate l'écart, va vérifier ; "
    "elle rétablit sa soirée ; elle rend son verdict ; le corps constate, une "
    "ligne ; une phrase brève referme.\n"
    "Le soir : elle relit l'entrée de la veille de son cahier, comme chaque "
    "soir. Sa mémoire dit une assiette, un dîner seule ; l'entrée en compte "
    "deux. Elle va voir : la cuisine, l'égouttoir — regarder, compter. Ce "
    "qu'elle voit confirme l'entrée, pas sa mémoire. Elle se donne une raison : "
    "la fatigue, l'automatisme.\n"
    "Verdict à rendre, dans ses mots : erreur de relevé — la faute est à elle, "
    "pas au texte ; et la résolution de pointer plus précisément.\n"
    "Dans la maison, ce soir : le cahier, l'assiette, l'égouttoir.\n"
    "CE QU'ELLE VOIT, imposé : « L'égouttoir, ce soir : deux assiettes. » Elle "
    "le CONSTATE, elle ne le découvre pas.\n"
    "En-tête : jamais de mois, jamais d'année.\n"
    "Interdits : aucun nom propre, aucun dialogue, aucune explication, "
    "« journal » et « journal intime » bannis, aucun terme réservé "
    "(la tierce, l'errata, le bon à tirer)."
)

# La garde d'entrée EST le lint de sortie. Le détecteur qui attrape « Couperet »
# dans le texte est exactement celui qui aurait dû interdire de le servir : on
# a linté la sortie contre un vocabulaire qu'on injectait à l'entrée. Cette
# assertion supprime la classe entière, pour ce brief et pour les suivants.

# L'objectif du chapitre complet, traduit lui aussi. Il en avait BESOIN :
# `OBJECTIF_CHAPITRE_V3` servait « Fait imposé, au matériau », et « matériau »
# est dans `META_TERMES` — donc CC recevait un terme d'atelier sans que personne
# l'ait remarqué. L'assertion ci-dessous n'a pas été écrite pour ce cas, elle
# l'a trouvé.
CHAPTER_GOAL_V4 = (
    "Chapitre 2 complet, trois entrées du carnet à dates consécutives, "
    "450-600 mots chacune. Ce que le chapitre raconte : la première "
    "divergence — l'entrée relue de son cahier mentionne une seconde assiette "
    "(citation à recopier verbatim dans l'entrée concernée : « Deux assiettes "
    "mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »), "
    "elle va voir à la cuisine, elle se donne une raison — la fatigue —, elle "
    "rend son verdict : erreur de relevé, et la résolution de pointer plus "
    "précisément.\n"
    "CE QU'ELLE VOIT, imposé : « L'égouttoir, ce soir : deux assiettes. »\n"
    "En-tête : jamais de mois, jamais d'année.\n"
    "Interdits : aucun nom propre, aucun dialogue, aucune explication, "
    "« journal » et « journal intime » bannis, aucun terme réservé "
    "(la tierce, l'errata, le bon à tirer)."
)

# La garde d'entrée EST le lint de sortie. Le détecteur qui attrape « Couperet »
# dans le texte est exactement celui qui aurait dû interdire de le servir : on
# a linté la sortie contre un vocabulaire qu'on injectait à l'entrée. Cette
# assertion supprime la classe entière, pour ces briefs et pour les suivants.
for _name, _brief in [("BRIEF_V4", BRIEF_V4),
                     ("OBJECTIF_CHAPITRE_V4", CHAPTER_GOAL_V4)]:
    _leaks = sorted({m.group(0).lower() for m in META_TERMS.finditer(_brief)})
    assert not _leaks, (
        f"{_name} sert des termes d'atelier que le lint bannit en sortie : "
        f"{_leaks}. C'est la cause mesurée du « Couperet : » de C2.")


# Météo de la première entrée : le brief la fixait, et sur un run mono-entrée le
# plan est court-circuité — donc aucun champ [météo] ne remonte, et le code
# tombait sur son défaut (« Temps calme ») en contredisant le brief.
START_WEATHER = "Ciel couvert"

# NARRATRICE, la spec du chapitre 7 (ENTREES_CH7, briefs, beats, verdict,
# objets) sont importées de `ch7` en tête de fichier — source unique partagée
# avec le chemin live de l'API.

# Ancre de la séquence d'en-têtes : le code DÉRIVE les dates suivantes, donc
# elles sont consécutives par construction (B′C avait produit [8,7,7,7,7,9,10,7]).
START_DAY, START_NUMBER = "Mardi", 12

# Le VERDICT est le repère d'épissure de l'accumulation — le seul point garanti
# de l'entrée, parce qu'un autre lint l'exige en présence. Les marqueurs de
# reconstruction (fatigue, automatisme) ne servent qu'en repli : ce sont des
# valeurs de la table de pilotage, qui MIGRENT d'un chapitre à l'autre.
VERDICT_CH2 = "erreur de relevé"
OBJECTS_CH2 = "le cahier, le carnet, l'assiette, l'égouttoir"



PLAN_RUNS = {
    "A": [("A1", BRIEF_V2, "score"), ("A2", BRIEF_V2, "score"),
          ("A3", BRIEF_V2, "score"),
          ("AC", CHAPTER_GOAL, "chapitre complet, hors score")],
    "B": [("B1", BRIEF_V2, "score"), ("B2", BRIEF_V2, "score"),
          ("B3", BRIEF_V2, "score"),
          ("BC", CHAPTER_GOAL, "chapitre complet, hors score")],
    # B′ : le service réparé. Brief v3, retrieval actif — la seule variable
    # face à B est le lot correctif.
    "Bp": [("Bp1", BRIEF_V3, "score"), ("Bp2", BRIEF_V3, "score"),
           ("Bp3", BRIEF_V3, "score"),
           ("BpC", CHAPTER_GOAL_V3, "chapitre complet, hors score")],
    # C : B′ plus les micro-nœuds d'assemblage. L3 et M1 deviennent bloquants.
    "C": [("C1", BRIEF_C, "score"), ("C2", BRIEF_C, "score"),
          ("C3", BRIEF_C, "score"),
          ("CC", CHAPTER_GOAL_V3, "chapitre complet, hors score")],
    # S6 : `write` décomposé en trois segments, brief v4, glissement pris à la
    # banque. La variable mesurée est le DÉCOUPAGE — le reste du lot corrige des
    # défauts nés à l'étage C, il n'ajoute pas de dispositif.
    "S6": [("S6-1", BRIEF_V4, "score"), ("S6-2", BRIEF_V4, "score"),
           ("S6-3", BRIEF_V4, "score"),
           ("S6-C", CHAPTER_GOAL_V4, "chapitre complet, hors score")],
    # S7 : le lot correctif. Brief v4 inchangé — ce qui bouge est DANS le
    # pipeline (stations, consignes en faits, garde-fou conscient de la cible,
    # dédoublonnage, tampon d'ancre) et dans la bible. Le brief reste le même
    # pour que la comparaison avec S6 porte sur le lot, et sur rien d'autre.
    "S7": [("S7-1", BRIEF_V4, "score"), ("S7-2", BRIEF_V4, "score"),
           ("S7-3", BRIEF_V4, "score"),
           ("S7-C", CHAPTER_GOAL_V4, "chapitre complet, hors score")],
    # CH7 : la répétition. Un seul run, le chapitre entier, deux entrées.
    "CH7": [("CH7", None, "répétition — chapitre 7 en conditions réelles")],
}


def time_per_node(metrics: list[dict]) -> dict[str, float]:
    """Agrège les durées par nœud — le livrable « marge des 28 minutes »."""
    out: dict[str, float] = {}
    for m in metrics:
        key = (m.get("noeud") or "?").split("/")[0]
        out[key] = round(out.get(key, 0.0) + m.get("wall_s", 0.0), 1)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--etage", choices=["A", "B", "Bp", "C", "S6", "S7", "CH7"],
                   required=True)
    # La graine du tirage de glissement, consignée au frontmatter : le tirage
    # varie d'un run à l'autre (sinon la même phrase à la même place devient une
    # liturgie de notre propre gabarit), mais un run reste rejouable à
    # l'identique quand un geste sort mal.
    p.add_argument("--graine", type=int, default=None)
    p.add_argument("--skip-preflight", action="store_true",
                   help="passe outre le préflight — les durées relevées ne "
                        "sont alors PAS comparables au run de référence")
    p.add_argument("--seulement", nargs="*", default=None)
    p.add_argument("--out-dir", default=None)
    args = p.parse_args()

    # PRÉFLIGHT, BLOQUANT POUR S6 SEULEMENT.
    #
    # L'arbitrage établi laissait l'outillage de calibration en simple
    # avertissement : il juge de la prose, pas des durées. La session 6 inverse
    # ce rapport — la variable mesurée est le COÛT du découpage en trois
    # segments, et le budget des 28 minutes se recalcule avec ces chiffres. Un
    # run joué pendant `mediaanalysisd` rendrait des temps ininterprétables
    # (32 et 49 minutes mesurées aux runs 3 et 4, trous de 5 à 18 minutes entre
    # deux appels), et on aurait dépensé deux heures pour rien.
    #
    # Les autres étages gardent le comportement d'avant : on ne change pas la
    # règle d'un étage en passant.
    timer = args.etage in ("S6", "S7", "CH7")
    try:
        for warning in preflight(timer=timer):
            print(f"  ⚠ {warning}", file=sys.stderr)
    except PreflightError as exc:
        print(f"\n{exc}\n", file=sys.stderr)
        if not args.skip_preflight:
            return 1
        print("  (--skip-preflight : on passe outre, temps NON comparables)",
              file=sys.stderr)

    rag = args.etage != "A"
    # Runs land under experiments/runs/<date>-<stage> (ADR-0003).
    out_dir = Path(args.out_dir or (
        RACINE / "experiments" / "runs"
        / f"{datetime.now():%Y%m%d}-{args.etage.lower()}"))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Import TARDIF : construire le graphe importe chromadb et, à l'étage A, on
    # veut pouvoir tourner conteneur éteint. L'import lui-même ne se connecte
    # pas, mais on garde l'ordre propre.
    from factory.pipeline.graph import build_graph
    graph = build_graph()

    for ident, brief, role in PLAN_RUNS[args.etage]:
        if args.seulement and ident not in args.seulement:
            continue
        print(f"\n{'=' * 66}\n[{ident}] {role} — rag={rag}\n{'=' * 66}",
              flush=True)
        # §5 : le journal de routage se vide avant chaque run pour que
        # les collections vues soient imputables à CE run seul.
        retrieval.clear_routing()
        # Une graine PAR RUN : trois runs d'un même étage doivent tirer des
        # glissements différents, sinon la variation qu'on cherche à obtenir est
        # annulée à l'intérieur même de la série. Consignée au frontmatter.
        seed = (args.graine if args.graine is not None
                  else random.randrange(1, 10**6))
        start, wall_start = time.monotonic(), time.time()
        # `entrees_attendues` commande le court-circuit du plan (item 10) et
        # `prefixe` le texte posé d'avance (item 5) — pour les runs mono-entrée
        # seulement : un chapitre complet garde son plan et ses propres en-têtes.
        mono = role == "score"
        # LE CHAPITRE 7 diffère de tout le reste par sa STRUCTURE, pas par son
        # câblage : deux entrées du même jour, la première en deux phrases sans
        # citation. `entrees_spec` porte cette structure ; partout ailleurs elle
        # est vide et le comportement est inchangé.
        ch7 = args.etage == "CH7"
        status = graph.invoke(
            {"brief": brief_chapter_7() if ch7 else brief,
             "characters": NARRATOR, "rag": rag,
             "expected_entries": len(ENTRIES_CH7) if ch7 else (1 if mono else 3),
             "entry_specs": ENTRIES_CH7 if ch7 else [],
             "imposed_plan": beats_chapter_7() if ch7 else [],
             # L'ancre du ch. 7 est PAR ENTRÉE (l'entrée 1 ne cite pas), donc
             # elle vit dans `entrees_spec` et non dans le préfixe global.
             "prefix": "" if ch7 else (
                 ANCHOR_CH2 if args.etage in ("Bp", "C", "S6", "S7") else ""),
             "micro_nodes": args.etage in ("C", "S6", "S7", "CH7"),
             # LA VARIABLE MESURÉE. Hors S6, `write` reste l'appel unique par
             # lequel tout le pipeline a été chronométré : l'habillage d'un
             # étage ne doit jamais rejouer la validation d'un autre.
             "segments": args.etage in ("S6", "S7", "CH7"),
             "seed": seed,
             # Le numéro de chapitre commande le SCOPE des interdits matériels
             # et la chute imposée de l'accumulation. Sans lui, un lint qui ne
             # connaît pas sa portée est soit inutile, soit faux.
             "chapter": 7 if ch7 else 2,
             "drawn_approaches": [],
             "start_day": "Samedi" if ch7 else START_DAY,
             "start_number": 14 if ch7 else START_NUMBER,
             "verdict": VERDICT_CH7 if ch7 else VERDICT_CH2,
             "active_objects": OBJECTS_CH7 if ch7 else OBJECTS_CH2,
             "start_weather": "Beau temps" if ch7 else START_WEATHER,
             "accumulation": ""},
            config={"recursion_limit": 50},
        )
        duration = time.monotonic() - start
        # DEUX HORLOGES, et elles ne mesurent pas la même chose.
        #
        # `time.monotonic()` s'ARRÊTE pendant la veille système sur macOS ;
        # `time.time()` continue. Le budget de scène est du temps de MUR — le
        # compteur du deck tourne pendant que le public attend, veille comprise.
        # Notre chiffre de référence était donc le mauvais.
        #
        # Découvert sur S7-3 : `duree_s` annonçait 374 s pendant que la somme
        # des appels au modèle donnait 2682 s. La machine avait fait deux
        # « Maintenance Sleep » sur batterie au milieu du run (confirmé par
        # `pmset -g log`). Sur scène, ce run aurait explosé les 28 minutes et la
        # métrique aurait dit que tout allait bien.
        wall_duration = time.time() - wall_start

        entries = status.get("repaired") or status.get("reviewed") or status["scenes"]
        text = "\n\n".join(entries)
        lint = analyze(text)
        per_node = time_per_node(status.get("metrics") or [])
        # TEMPS PAR SEGMENT — le chiffre qui décide si le découpage tient dans
        # les 28' du compteur. Les trois appels d'écriture portent un label
        # « entrée N/segment », donc ils se somment par segment sans que le
        # graphe ait à tenir un compteur de plus.
        segment_times: dict[str, float] = {}
        for m in status.get("metrics") or []:
            seg = m.get("segment")
            if seg:
                # `wall_s`, pas `ms` : c'est la clé que produit `chat()`, et
                # c'est celle que `temps_par_noeud` utilise depuis toujours. La
                # première version sommait une clé inexistante et rendait
                # 0,0 s par segment — un chiffre faux se lit comme une mesure,
                # là où une absence se serait vue.
                segment_times[seg] = round(
                    segment_times.get(seg, 0.0) + m.get("wall_s", 0.0), 1)
        guards = [w for w in status.get("warnings", []) if "garde-fou 60 %" in w]
        collections = sorted(set(retrieval.routing()))
        # `ctx_need` est le seul signal fiable de saturation de fenêtre : Ollama
        # tronque en silence et ne rapporte que ce qu'il a lu. Relevé obligatoire
        # au lot correctif — la texture servie en plus va le faire monter.
        ctx_max = max((m.get("ctx_need", 0) for m in status.get("metrics") or []),
                      default=0)

        path = out_dir / f"run-{ident}.md"
        path.write_text(
            "---\n"
            f"run: {ident}\n"
            f"etage: {args.etage}\n"
            f"role: {role}\n"
            f"rag: {rag}\n"
            f"ctx_need_max: {ctx_max}\n"
            f"graine: {seed}\n"
            f"segments: {args.etage in ('S6', 'S7', 'CH7')}\n"
            f"temps_par_segment: {json.dumps(segment_times, ensure_ascii=False)}\n"
            f"date: {datetime.now().isoformat(timespec='seconds')}\n"
            f"mots: {len(text.split())}\n"
            f"entrees_generees: {len(entries)}\n"
            f"entrees_detectees: {lint['entrees']}\n"
            f"temperature: 0.7\n"
            f"duree_s: {duration:.0f}\n"
            f"duree_mur_s: {wall_duration:.0f}\n"
            f"veille_s: {max(0, wall_duration - duration):.0f}\n"
            f"done_reason: {'length' if ends_mid_sentence(text) else 'stop'}\n"
            f"temps_par_noeud: {json.dumps(per_node, ensure_ascii=False)}\n"
            f"garde_fou_60: {len(guards)}\n"
            f"collections_interrogees: {json.dumps(collections, ensure_ascii=False)}\n"
            f"fin_pendante: {ends_mid_sentence(text)}\n"
            f"plan: {json.dumps(status.get('plan') or [], ensure_ascii=False)}\n"
            f"plan_report: {json.dumps(status.get('plan_report') or '', ensure_ascii=False)}\n"
            f"coherence: {json.dumps(status.get('coherence') or '', ensure_ascii=False)}\n"
            f"warnings: {json.dumps(status.get('warnings') or [], ensure_ascii=False)}\n"
            "---\n\n" + text + "\n",
            encoding="utf-8",
        )
        print(f"[{ident}] {len(text.split())} mots, {len(entries)} entrée(s), "
              f"{duration:.0f}s → {path}")
        # Un écart de plus de 30 s entre les deux horloges = la machine a dormi
        # ou a été suspendue. Le dire FORT : un run dont les durées sont
        # contaminées ne se compare à rien, et c'est le chiffre central de la
        # session.
        if wall_duration - duration > 30:
            print(f"  ⚠ VEILLE DÉTECTÉE : {wall_duration - duration:.0f}s d'écart "
                  f"entre l'horloge de mur ({wall_duration:.0f}s) et le temps de "
                  f"calcul ({duration:.0f}s). Les durées de ce run ne sont PAS "
                  f"comparables. Brancher la machine et relancer "
                  f"(`caffeinate -is`).", file=sys.stderr)
        print(f"        temps par nœud : {per_node}")
        print(f"        collections interrogées : {collections or 'aucune'}")
        for g in guards:
            print(f"  ⚠ {g}", file=sys.stderr)

    print(f"\nGrille : python3 outillage/grille_session.py {out_dir} 450-600")
    return 0


if __name__ == "__main__":
    sys.exit(main())
