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
import re
import random
import sys
import time
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outillage"))
sys.path.insert(0, str(RACINE / "orchestrator"))

from lint_style import META_TERMES, analyse  # noqa: E402
import retrieval  # noqa: E402
from style import ends_mid_sentence  # noqa: E402
from preflight import PreflightError, preflight  # noqa: E402
# La spécification du chapitre 7 vit dans orchestrator/ch7.py — source unique
# partagée avec le chemin live de l'API (voir le module). NARRATRICE y est aussi
# (le doc_id de la narratrice vaut pour TOUS les étages, pas seulement le ch. 7).
from ch7 import (  # noqa: E402
    NARRATRICE, ENTREES_CH7, beats_chapitre_7, brief_chapitre_7,
    VERDICT_CH7, OBJETS_CH7,
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
OBJECTIF_CHAPITRE = (
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
ANCRE_CH2 = ("« Deux assiettes mises, sans y penser. Je l'ai laissée sur la "
             "table jusqu'au matin. »")

BRIEF_V3 = BRIEF_V2.replace(
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.",
    "Matériau : le cahier, le carnet, l'assiette, l'égouttoir.\n"
    "FAIT IMPOSÉ, au matériau : « L'égouttoir, ce soir : deux assiettes. » "
    "La vérification CONSTATE ce fait, elle ne le découvre pas.\n"
    "En-tête : jamais de mois, jamais d'année."
)

# L'objectif de chapitre hérite du même fait imposé.
OBJECTIF_CHAPITRE_V3 = OBJECTIF_CHAPITRE + (
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
OBJECTIF_CHAPITRE_V4 = (
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
for _nom, _brief in [("BRIEF_V4", BRIEF_V4),
                     ("OBJECTIF_CHAPITRE_V4", OBJECTIF_CHAPITRE_V4)]:
    _fuites = sorted({m.group(0).lower() for m in META_TERMES.finditer(_brief)})
    assert not _fuites, (
        f"{_nom} sert des termes d'atelier que le lint bannit en sortie : "
        f"{_fuites}. C'est la cause mesurée du « Couperet : » de C2.")


# Météo de la première entrée : le brief la fixait, et sur un run mono-entrée le
# plan est court-circuité — donc aucun champ [météo] ne remonte, et le code
# tombait sur son défaut (« Temps calme ») en contredisant le brief.
METEO_DEPART = "Ciel couvert"

# NARRATRICE, la spec du chapitre 7 (ENTREES_CH7, briefs, beats, verdict,
# objets) sont importées de `ch7` en tête de fichier — source unique partagée
# avec le chemin live de l'API.

# Ancre de la séquence d'en-têtes : le code DÉRIVE les dates suivantes, donc
# elles sont consécutives par construction (B′C avait produit [8,7,7,7,7,9,10,7]).
JOUR_DEPART, NUMERO_DEPART = "Mardi", 12

# Le VERDICT est le repère d'épissure de l'accumulation — le seul point garanti
# de l'entrée, parce qu'un autre lint l'exige en présence. Les marqueurs de
# reconstruction (fatigue, automatisme) ne servent qu'en repli : ce sont des
# valeurs de la table de pilotage, qui MIGRENT d'un chapitre à l'autre.
VERDICT_CH2 = "erreur de relevé"
OBJETS_CH2 = "le cahier, le carnet, l'assiette, l'égouttoir"



PLAN_RUNS = {
    "A": [("A1", BRIEF_V2, "score"), ("A2", BRIEF_V2, "score"),
          ("A3", BRIEF_V2, "score"),
          ("AC", OBJECTIF_CHAPITRE, "chapitre complet, hors score")],
    "B": [("B1", BRIEF_V2, "score"), ("B2", BRIEF_V2, "score"),
          ("B3", BRIEF_V2, "score"),
          ("BC", OBJECTIF_CHAPITRE, "chapitre complet, hors score")],
    # B′ : le service réparé. Brief v3, retrieval actif — la seule variable
    # face à B est le lot correctif.
    "Bp": [("Bp1", BRIEF_V3, "score"), ("Bp2", BRIEF_V3, "score"),
           ("Bp3", BRIEF_V3, "score"),
           ("BpC", OBJECTIF_CHAPITRE_V3, "chapitre complet, hors score")],
    # C : B′ plus les micro-nœuds d'assemblage. L3 et M1 deviennent bloquants.
    "C": [("C1", BRIEF_C, "score"), ("C2", BRIEF_C, "score"),
          ("C3", BRIEF_C, "score"),
          ("CC", OBJECTIF_CHAPITRE_V3, "chapitre complet, hors score")],
    # S6 : `write` décomposé en trois segments, brief v4, glissement pris à la
    # banque. La variable mesurée est le DÉCOUPAGE — le reste du lot corrige des
    # défauts nés à l'étage C, il n'ajoute pas de dispositif.
    "S6": [("S6-1", BRIEF_V4, "score"), ("S6-2", BRIEF_V4, "score"),
           ("S6-3", BRIEF_V4, "score"),
           ("S6-C", OBJECTIF_CHAPITRE_V4, "chapitre complet, hors score")],
    # S7 : le lot correctif. Brief v4 inchangé — ce qui bouge est DANS le
    # pipeline (stations, consignes en faits, garde-fou conscient de la cible,
    # dédoublonnage, tampon d'ancre) et dans la bible. Le brief reste le même
    # pour que la comparaison avec S6 porte sur le lot, et sur rien d'autre.
    "S7": [("S7-1", BRIEF_V4, "score"), ("S7-2", BRIEF_V4, "score"),
           ("S7-3", BRIEF_V4, "score"),
           ("S7-C", OBJECTIF_CHAPITRE_V4, "chapitre complet, hors score")],
    # CH7 : la répétition. Un seul run, le chapitre entier, deux entrées.
    "CH7": [("CH7", None, "répétition — chapitre 7 en conditions réelles")],
}


def temps_par_noeud(metrics: list[dict]) -> dict[str, float]:
    """Agrège les durées par nœud — le livrable « marge des 28 minutes »."""
    out: dict[str, float] = {}
    for m in metrics:
        cle = (m.get("noeud") or "?").split("/")[0]
        out[cle] = round(out.get(cle, 0.0) + m.get("wall_s", 0.0), 1)
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
    chrono = args.etage in ("S6", "S7", "CH7")
    try:
        for avertissement in preflight(chrono=chrono):
            print(f"  ⚠ {avertissement}", file=sys.stderr)
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
    from graph import build_graph
    graph = build_graph()

    for ident, brief, role in PLAN_RUNS[args.etage]:
        if args.seulement and ident not in args.seulement:
            continue
        print(f"\n{'=' * 66}\n[{ident}] {role} — rag={rag}\n{'=' * 66}",
              flush=True)
        # §5 : le journal de routage se vide avant chaque run pour que
        # les collections vues soient imputables à CE run seul.
        retrieval.vider_routage()
        # Une graine PAR RUN : trois runs d'un même étage doivent tirer des
        # glissements différents, sinon la variation qu'on cherche à obtenir est
        # annulée à l'intérieur même de la série. Consignée au frontmatter.
        graine = (args.graine if args.graine is not None
                  else random.randrange(1, 10**6))
        depart, depart_mur = time.monotonic(), time.time()
        # `entrees_attendues` commande le court-circuit du plan (item 10) et
        # `prefixe` le texte posé d'avance (item 5) — pour les runs mono-entrée
        # seulement : un chapitre complet garde son plan et ses propres en-têtes.
        mono = role == "score"
        # LE CHAPITRE 7 diffère de tout le reste par sa STRUCTURE, pas par son
        # câblage : deux entrées du même jour, la première en deux phrases sans
        # citation. `entrees_spec` porte cette structure ; partout ailleurs elle
        # est vide et le comportement est inchangé.
        ch7 = args.etage == "CH7"
        etat = graph.invoke(
            {"brief": brief_chapitre_7() if ch7 else brief,
             "characters": NARRATRICE, "rag": rag,
             "entrees_attendues": len(ENTREES_CH7) if ch7 else (1 if mono else 3),
             "entrees_spec": ENTREES_CH7 if ch7 else [],
             "plan_impose": beats_chapitre_7() if ch7 else [],
             # L'ancre du ch. 7 est PAR ENTRÉE (l'entrée 1 ne cite pas), donc
             # elle vit dans `entrees_spec` et non dans le préfixe global.
             "prefixe": "" if ch7 else (
                 ANCRE_CH2 if args.etage in ("Bp", "C", "S6", "S7") else ""),
             "micro_noeuds": args.etage in ("C", "S6", "S7", "CH7"),
             # LA VARIABLE MESURÉE. Hors S6, `write` reste l'appel unique par
             # lequel tout le pipeline a été chronométré : l'habillage d'un
             # étage ne doit jamais rejouer la validation d'un autre.
             "segments": args.etage in ("S6", "S7", "CH7"),
             "graine": graine,
             # Le numéro de chapitre commande le SCOPE des interdits matériels
             # et la chute imposée de l'accumulation. Sans lui, un lint qui ne
             # connaît pas sa portée est soit inutile, soit faux.
             "chapitre": 7 if ch7 else 2,
             "approches_tirees": [],
             "jour_depart": "Samedi" if ch7 else JOUR_DEPART,
             "numero_depart": 14 if ch7 else NUMERO_DEPART,
             "verdict": VERDICT_CH7 if ch7 else VERDICT_CH2,
             "objets_actifs": OBJETS_CH7 if ch7 else OBJETS_CH2,
             "meteo_depart": "Beau temps" if ch7 else METEO_DEPART,
             "accumulation": ""},
            config={"recursion_limit": 50},
        )
        duree = time.monotonic() - depart
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
        duree_mur = time.time() - depart_mur

        entrees = etat.get("repaired") or etat.get("reviewed") or etat["scenes"]
        texte = "\n\n".join(entrees)
        lint = analyse(texte)
        par_noeud = temps_par_noeud(etat.get("metrics") or [])
        # TEMPS PAR SEGMENT — le chiffre qui décide si le découpage tient dans
        # les 28' du compteur. Les trois appels d'écriture portent un label
        # « entrée N/segment », donc ils se somment par segment sans que le
        # graphe ait à tenir un compteur de plus.
        temps_segments: dict[str, float] = {}
        for m in etat.get("metrics") or []:
            seg = m.get("segment")
            if seg:
                # `wall_s`, pas `ms` : c'est la clé que produit `chat()`, et
                # c'est celle que `temps_par_noeud` utilise depuis toujours. La
                # première version sommait une clé inexistante et rendait
                # 0,0 s par segment — un chiffre faux se lit comme une mesure,
                # là où une absence se serait vue.
                temps_segments[seg] = round(
                    temps_segments.get(seg, 0.0) + m.get("wall_s", 0.0), 1)
        gardes = [w for w in etat.get("warnings", []) if "garde-fou 60 %" in w]
        collections = sorted(set(retrieval.routage()))
        # `ctx_need` est le seul signal fiable de saturation de fenêtre : Ollama
        # tronque en silence et ne rapporte que ce qu'il a lu. Relevé obligatoire
        # au lot correctif — la texture servie en plus va le faire monter.
        ctx_max = max((m.get("ctx_need", 0) for m in etat.get("metrics") or []),
                      default=0)

        chemin = out_dir / f"run-{ident}.md"
        chemin.write_text(
            "---\n"
            f"run: {ident}\n"
            f"etage: {args.etage}\n"
            f"role: {role}\n"
            f"rag: {rag}\n"
            f"ctx_need_max: {ctx_max}\n"
            f"graine: {graine}\n"
            f"segments: {args.etage in ('S6', 'S7', 'CH7')}\n"
            f"temps_par_segment: {json.dumps(temps_segments, ensure_ascii=False)}\n"
            f"date: {datetime.now().isoformat(timespec='seconds')}\n"
            f"mots: {len(texte.split())}\n"
            f"entrees_generees: {len(entrees)}\n"
            f"entrees_detectees: {lint['entrees']}\n"
            f"temperature: 0.7\n"
            f"duree_s: {duree:.0f}\n"
            f"duree_mur_s: {duree_mur:.0f}\n"
            f"veille_s: {max(0, duree_mur - duree):.0f}\n"
            f"done_reason: {'length' if ends_mid_sentence(texte) else 'stop'}\n"
            f"temps_par_noeud: {json.dumps(par_noeud, ensure_ascii=False)}\n"
            f"garde_fou_60: {len(gardes)}\n"
            f"collections_interrogees: {json.dumps(collections, ensure_ascii=False)}\n"
            f"fin_pendante: {ends_mid_sentence(texte)}\n"
            f"plan: {json.dumps(etat.get('plan') or [], ensure_ascii=False)}\n"
            f"plan_report: {json.dumps(etat.get('plan_report') or '', ensure_ascii=False)}\n"
            f"coherence: {json.dumps(etat.get('coherence') or '', ensure_ascii=False)}\n"
            f"warnings: {json.dumps(etat.get('warnings') or [], ensure_ascii=False)}\n"
            "---\n\n" + texte + "\n",
            encoding="utf-8",
        )
        print(f"[{ident}] {len(texte.split())} mots, {len(entrees)} entrée(s), "
              f"{duree:.0f}s → {chemin}")
        # Un écart de plus de 30 s entre les deux horloges = la machine a dormi
        # ou a été suspendue. Le dire FORT : un run dont les durées sont
        # contaminées ne se compare à rien, et c'est le chiffre central de la
        # session.
        if duree_mur - duree > 30:
            print(f"  ⚠ VEILLE DÉTECTÉE : {duree_mur - duree:.0f}s d'écart "
                  f"entre l'horloge de mur ({duree_mur:.0f}s) et le temps de "
                  f"calcul ({duree:.0f}s). Les durées de ce run ne sont PAS "
                  f"comparables. Brancher la machine et relancer "
                  f"(`caffeinate -is`).", file=sys.stderr)
        print(f"        temps par nœud : {par_noeud}")
        print(f"        collections interrogées : {collections or 'aucune'}")
        for g in gardes:
            print(f"  ⚠ {g}", file=sys.stderr)

    print(f"\nGrille : python3 outillage/grille_session.py {out_dir} 450-600")
    return 0


if __name__ == "__main__":
    sys.exit(main())
