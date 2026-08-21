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

Les briefs sont lus dans `briefs/protocole-calibration-ch2.md` (§3 du protocole
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
import sys
import time
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outillage"))
sys.path.insert(0, str(RACINE / "orchestrator"))

from lint_style import analyse  # noqa: E402
import retrieval  # noqa: E402
from style import ends_mid_sentence  # noqa: E402

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

# Météo de la première entrée : le brief la fixait, et sur un run mono-entrée le
# plan est court-circuité — donc aucun champ [météo] ne remonte, et le code
# tombait sur son défaut (« Temps calme ») en contredisant le brief.
METEO_DEPART = "Ciel couvert"

NARRATRICE = ["fiche-judith"]

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
    p.add_argument("--etage", choices=["A", "B", "Bp", "C"], required=True)
    p.add_argument("--seulement", nargs="*", default=None)
    p.add_argument("--out-dir", default=None)
    args = p.parse_args()

    rag = args.etage != "A"
    out_dir = Path(args.out_dir or f"runs-s4-{args.etage.lower()}")
    out_dir.mkdir(exist_ok=True)

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
        depart = time.monotonic()
        # `entrees_attendues` commande le court-circuit du plan (item 10) et
        # `prefixe` le texte posé d'avance (item 5) — pour les runs mono-entrée
        # seulement : un chapitre complet garde son plan et ses propres en-têtes.
        mono = role == "score"
        etat = graph.invoke(
            {"brief": brief, "characters": NARRATRICE, "rag": rag,
             "entrees_attendues": 1 if mono else 3,
             "prefixe": ANCRE_CH2 if args.etage in ("Bp", "C") else "",
             "micro_noeuds": args.etage == "C",
             "jour_depart": JOUR_DEPART, "numero_depart": NUMERO_DEPART,
             "verdict": VERDICT_CH2, "objets_actifs": OBJETS_CH2,
             "meteo_depart": METEO_DEPART,
             "accumulation": ""},
            config={"recursion_limit": 50},
        )
        duree = time.monotonic() - depart

        entrees = etat.get("repaired") or etat.get("reviewed") or etat["scenes"]
        texte = "\n\n".join(entrees)
        lint = analyse(texte)
        par_noeud = temps_par_noeud(etat.get("metrics") or [])
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
            f"date: {datetime.now().isoformat(timespec='seconds')}\n"
            f"mots: {len(texte.split())}\n"
            f"entrees_generees: {len(entrees)}\n"
            f"entrees_detectees: {lint['entrees']}\n"
            f"temperature: 0.7\n"
            f"duree_s: {duree:.0f}\n"
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
        print(f"        temps par nœud : {par_noeud}")
        print(f"        collections interrogées : {collections or 'aucune'}")
        for g in gardes:
            print(f"  ⚠ {g}", file=sys.stderr)

    print(f"\nGrille : python3 outillage/grille_session.py {out_dir} 450-600")
    return 0


if __name__ == "__main__":
    sys.exit(main())
