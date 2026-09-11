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
  factory calibrate --stage A                 # A1-A3 + AC
  factory calibrate --stage A --only A1
  factory calibrate --stage B

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

from factory.eval.lint import analyze
from factory.retrieval import context as retrieval
from factory.text import ends_mid_sentence
from factory.infra.preflight import PreflightError
# Chapter knowledge (7 and 2) comes from chapters/NN-slug/spec.yaml through the
# loader — the single source shared with the API's live path and the CLI.
from factory.chapter_spec import load_chapter

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
# (The anchor quotation is now `prefix` in chapters/02-*/spec.yaml.)

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

# BRIEF V4 (session 6) and the chapter goal v4 live in chapters/02-*/spec.yaml
# (`entry_brief`, `brief`); the loader asserts them free of workshop terms.

# Calendar, verdict, objects and anchor of chapter 2 are read from its spec.

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
    "S6": [("S6-1", "entry", "score"), ("S6-2", "entry", "score"),
           ("S6-3", "entry", "score"),
           ("S6-C", "chapter", "chapitre complet, hors score")],
    # S7 : le lot correctif. Brief v4 inchangé — ce qui bouge est DANS le
    # pipeline (stations, consignes en faits, garde-fou conscient de la cible,
    # dédoublonnage, tampon d'ancre) et dans la bible. Le brief reste le même
    # pour que la comparaison avec S6 porte sur le lot, et sur rien d'autre.
    "S7": [("S7-1", "entry", "score"), ("S7-2", "entry", "score"),
           ("S7-3", "entry", "score"),
           ("S7-C", "chapter", "chapitre complet, hors score")],
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="factory calibrate",
                                description="Calibration stages of chapter 2 and the "
                                            "chapter 7 rehearsal, one run file per draw.")
    p.add_argument("--stage", choices=["A", "B", "Bp", "C", "S6", "S7", "CH7"],
                   required=True)
    # La graine du tirage de glissement, consignée au frontmatter : le tirage
    # varie d'un run à l'autre (sinon la même phrase à la même place devient une
    # liturgie de notre propre gabarit), mais un run reste rejouable à
    # l'identique quand un geste sort mal.
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--skip-preflight", action="store_true",
                   help="passe outre le préflight — les durées relevées ne "
                        "sont alors PAS comparables au run de référence")
    p.add_argument("--only", nargs="*", default=None)
    p.add_argument("--out-dir", default=None)
    args = p.parse_args(argv)

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
    #
    # Depuis l'étape 4, le préflight est le premier nœud du graphe : il tourne
    # AVANT CHAQUE RUN (le runbook l'exigeait déjà à la main), bloquant pour les
    # étages chronométrés seulement, avertissement partout ailleurs.
    timer = args.stage in ("S6", "S7", "CH7")
    preflight_request = {"strict": timer and not args.skip_preflight, "timer": timer}
    if timer and args.skip_preflight:
        print("  (--skip-preflight : on passe outre, temps NON comparables)",
              file=sys.stderr)

    rag = args.stage != "A"
    # Runs land under experiments/runs/<date>-<stage> (ADR-0003).
    out_dir = Path(args.out_dir or (
        RACINE / "experiments" / "runs"
        / f"{datetime.now():%Y%m%d}-{args.stage.lower()}"))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Import TARDIF : construire le graphe importe chromadb et, à l'étage A, on
    # veut pouvoir tourner conteneur éteint. L'import lui-même ne se connecte
    # pas, mais on garde l'ordre propre.
    from factory.pipeline.graph import build_graph
    graph = build_graph()

    for ident, brief, role in PLAN_RUNS[args.stage]:
        if args.only and ident not in args.only:
            continue
        print(f"\n{'=' * 66}\n[{ident}] {role} — rag={rag}\n{'=' * 66}",
              flush=True)
        # §5 : le journal de routage se vide avant chaque run pour que
        # les collections vues soient imputables à CE run seul.
        retrieval.clear_routing()
        # Une graine PAR RUN : trois runs d'un même étage doivent tirer des
        # glissements différents, sinon la variation qu'on cherche à obtenir est
        # annulée à l'intérieur même de la série. Consignée au frontmatter.
        seed = (args.seed if args.seed is not None
                  else random.randrange(1, 10**6))
        start, wall_start = time.monotonic(), time.time()
        # `entrees_attendues` commande le court-circuit du plan (item 10) et
        # `prefixe` le texte posé d'avance (item 5) — pour les runs mono-entrée
        # seulement : un chapitre complet garde son plan et ses propres en-têtes.
        mono = role == "score"
        # LE CHAPITRE 7 diffère de tout le reste par sa STRUCTURE, pas par son
        # câblage : deux entrées du même jour, la première en deux phrases sans
        # citation. `entry_specs` porte cette structure ; partout ailleurs elle
        # est vide et le comportement est inchangé.
        ch7 = args.stage == "CH7"
        # The chapter spec builds the state (step 5); the stage only sets the
        # run options: brief version, RAG, micro-nodes, segments, single entry.
        spec = load_chapter(7 if ch7 else 2)
        served = {"entry": spec.entry_brief, "chapter": spec.brief}.get(brief, brief)
        try:
            status = graph.invoke(
                {**spec.state(
                    seed=seed,
                    brief=None if ch7 else served,
                    entry_count=None if ch7 else (1 if mono else 3),
                    rag=rag,
                    micro_nodes=args.stage in ("C", "S6", "S7", "CH7"),
                    # LA VARIABLE MESURÉE de la session 6 : hors S6, `write`
                    # reste l'appel unique par lequel tout a été chronométré.
                    segments=args.stage in ("S6", "S7", "CH7"),
                    prefix=None if ch7 else (
                        spec.prefix if args.stage in ("Bp", "C", "S6", "S7") else ""),
                 ),
                 "preflight": preflight_request},
                config={"recursion_limit": 50},
            )
        except PreflightError as exc:
            print(f"\n{exc}\n", file=sys.stderr)
            return 1
        for w in status.get("preflight_warnings") or []:
            print(f"  ⚠ {w}", file=sys.stderr)
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
            f"etage: {args.stage}\n"
            f"role: {role}\n"
            f"rag: {rag}\n"
            f"ctx_need_max: {ctx_max}\n"
            f"graine: {seed}\n"
            f"segments: {args.stage in ('S6', 'S7', 'CH7')}\n"
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

    print(f"\nGrille : factory eval grid {out_dir} 450-600")
    return 0


if __name__ == "__main__":
    sys.exit(main())
