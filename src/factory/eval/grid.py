#!/usr/bin/env python3
"""Assemble la grille de session à quatre colonnes depuis les runs.

Croise la grille FINE de `_scene-test-style.md` (mécanique / structure / oral,
règle des 2 runs sur 3) avec la présentation à quatre colonnes de
`outillage/grille-lint.md`. Les lignes décidables mécaniquement sont remplies
par `lint_style`, les autres restent vides : c'est le relecteur qui les remplit,
à voix haute.

Régénéré à chaque itération de la fiche — d'où un script plutôt qu'un fichier
recopié à la main : une grille transcrite à la main dérive de ce que les runs
disent réellement, et c'est cette dérive qu'on paierait au moment de décider
quel chunk durcir.

Usage :
  python3 outillage/grille_session.py > grille-lint-session-1.md
"""

import re
import sys
from pathlib import Path

from factory.eval.lint import (ACC_ABSTRACT_MAX, ENTRY_HEADER,
                        L3_WORDS, L3_COMMAS,
                        analyze, chapter_constraints, chapter_checks,
                        strip_frontmatter)

def discover(folder: str = "runs") -> list[tuple[str, Path]]:
    """Tous les runs présents, runs standard d'abord puis contrôles.

    Découverte par glob et non liste figée : le protocole prévoit de relancer un
    tirage pour lever une zone grise, et une grille qui ignorerait le run
    supplémentaire ferait décider sur des données incomplètes.
    """
    def key(f: Path) -> tuple[int, int, str]:
        """Ordre de lecture : runs de score, puis contrôle, puis exploration.

        C'est l'ordre du protocole, et il porte du sens : on lit d'abord ce qui
        est scoré, ensuite ce qui l'éclaire. Un tri alphabétique mettrait le
        contrôle entre les runs 1 et 2, et placerait `run-controle-2` AVANT
        `run-controle` (le tiret précède le point) — de quoi comparer les
        mauvaises colonnes.
        """
        name = f.stem.removeprefix("run-")
        num = re.search(r"(\d+)", name)
        rank = int(num.group(1)) if num else 1
        if name.lower().startswith("x"):
            family = 2                      # exploration, hors score
        elif name.upper().endswith("C") or name.lower().startswith(
                ("c", "controle", "contrôle")):
            # `AC`/`BC` sont les chapitres complets hors score : ils se lisent
            # APRÈS les runs scorés, comme le contrôle. Sans ce cas, `AC` se
            # rangeait entre A1 et A2 (rang 1, faute de chiffre).
            family = 1
        else:
            family = 0                      # runs de score
        return (family, rank, name)

    def name_for(f: Path) -> str:
        name = f.stem.removeprefix("run-")
        if name.lower().startswith(("controle", "contrôle")):
            return "Contrôle" + name[8:]
        if name.upper() == "C":
            return "Contrôle"
        if name.lower().startswith("x"):
            return name.upper()               # X1, X2 — exploration
        return f"Run {name}"

    files = sorted(Path(folder).glob("run-*.md"), key=key)
    return [(name_for(f), f) for f in files]

# Lignes que le code ne peut PAS trancher sans comprendre le texte. Elles sont
# listées explicitement plutôt qu'omises : une grille silencieuse sur une ligne
# se lit comme une ligne tenue.
# LE JUGE. Une ligne, en tête, manuelle : la grille automatique ne dit plus si
# c'est bon, elle dit si c'est disqualifié. Cette question-là est le seul
# jugement qui distingue une structure conforme d'un texte qui tient.
MANUAL_JUDGE = "**Le mouvement déclaré est-il accompli ?**"

MANUAL_MECHANICS = [
    "Deux adjectifs ou plus coordonnés sur un même nom",
    "Émotion annoncée avant d'être montrée",
    "Météo ou obscurité corrélée à la tension",
    "Information hors du champ perceptif du narrateur",
    "Doute résolu, dans un sens ou dans l'autre",
]
MANUAL_STRUCTURE = [
    "Une vérification matérielle de l'anomalie (le geste, décrit)",
    "Le décalage dans le dialogue (la sœur répond à côté)",
    "Les cinq beats présents, dans l'ordre",
]
# M1-M4 du protocole de calibration ch. 2. Explicitement NON automatisés : ils
# demandent de lire, pas de compter. Les laisser en lignes vides plutôt que de
# les omettre — une grille muette sur une ligne se lit comme une ligne tenue.
MANUAL_PROTOCOL = [
    "M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, "
    "puis retour immédiat à un fait matériel",
    "M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence "
    "(échec si complice ou neutre)",
    "M3 · Décision sans geste — toute décision est notée, aucune exécution "
    "racontée en scène",
    "M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire "
    "de la narratrice",
]

MANUAL_ORAL = [
    "Tenu en moins de 2 minutes à voix haute",
    "Aucune phrase reprise deux fois pour la comprendre",
    "Le style est audible : quelqu'un qui a entendu les étalons "
    "reconnaîtrait la voix",
]


def frontmatter(path: Path) -> dict:
    """Lit le frontmatter du run (température, done_reason, durée…)."""
    meta, inside = {}, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "---":
            if inside:
                break
            inside = True
            continue
        if inside and ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def line(label: str, cells: list[str]) -> str:
    return f"| {label} | " + " | ".join(cells) + " |"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # Une session par dossier : les runs de la fiche v1 restent lisibles quand
    # la v2 tourne. Comparer deux versions de la fiche suppose de garder les
    # deux jeux de tirages.
    folder = argv[0] if len(argv) > 0 else "runs"
    # La cible de longueur change avec le brief : 400-550 pour la scène test de
    # la session 1, 450-600 pour le chapitre 2. Codée en dur, elle aurait
    # affiché « hors cible » sur des runs conformes — un faux défaut, et le
    # genre qui envoie durcir une section qui va bien.
    target = argv[1] if len(argv) > 1 else "400-600"
    target_min, target_max = (int(x) for x in target.split("-"))
    # Numéro de chapitre : active les interdits SCOPÉS (notes §3 et §4). Sans
    # lui, la grille ne peut pas savoir que « la tierce » est légitime au
    # chapitre 9 et interdite au 2 — et un interdit qui ne connaît pas sa
    # portée est soit inutile, soit faux.
    chapter = int(argv[2]) if len(argv) > 2 else None
    constraints = chapter_constraints(chapter) if chapter else None
    available = discover(folder)
    if not available:
        print(f"ERREUR : aucun run dans {folder}.", file=sys.stderr)
        return 1

    res = {name: analyze(p.read_text(encoding="utf-8")) for name, p in available}
    meta = {name: frontmatter(p) for name, p in available}
    names = [name for name, _ in available]
    header = "| Contrôle attendu | " + " | ".join(names) + " |"
    sep = "|---|" + "---|" * len(names)

    out = [
        "# Grille de lint",
        "",
        "Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes "
        "AUTO** : elles se régénèrent. Remplir les lignes vides à la main, "
        "après lecture à voix haute.",
        "",
        "**Règle de décision retenue** — celle du protocole d'origine "
        "(`_scene-test-style.md`), qui prime sur celle du paquet test-style : "
        "un item échoué sur **2 runs sur 3** désigne une section de la fiche à "
        "durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas "
        "à la fiche.",
        "",
        "**Tri des échecs**, structurant pour la suite : échec **mécanique** → "
        "durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le "
        "prompt d'orchestration, donc LangGraph, PAS la fiche.",
        "",
        "## Le juge — ligne manuelle, elle prime sur tout ce qui suit",
        "",
        "Tout ce qui est AUTO ci-dessous est un **véto** : ces lignes ne disent "
        "pas si le texte est bon, elles disent s'il est disqualifié (fuites, "
        "ancre, interdits, bornes). Le jugement est ici, et il se rend à la "
        "lecture debout.",
        "",
        header,
        sep,
        line(MANUAL_JUDGE, [" "] * len(names)),
        "",
        "## Conditions des runs",
        "",
        "| | " + " | ".join(names) + " |",
        sep,
    ]
    # Plusieurs clés possibles par ligne : les runs de sessions différentes
    # n'écrivent pas le même frontmatter, et une grille qui n'en connaît qu'un
    # affiche « ? » sur des données présentes.
    for keys, lib in [(("temperature",), "Température"),
                      (("mots",), "Mots"),
                      (("duree_s", "duree_totale_s"), "Durée (s)"),
                      (("done_reason",), "done_reason"),
                      (("entrees_generees",), "Entrées générées"),
                      (("garde_fou_60",), "Garde-fou 60 % déclenché"),
                      (("temps_par_noeud",), "Temps par nœud (s)")]:
        values = [next((meta[n][c] for c in keys if meta[n].get(c)), "—")
                   for n in names]
        if any(v != "—" for v in values):
            out.append(line(lib, values))
    out.append(line(f"Cible {target_min}-{target_max}",
                     ["✓" if target_min <= res[n]["mots"] <= target_max
                      else "✗ hors cible" for n in names]))

    out += ["", "## Mécanique — échec si présent (AUTO)", "", header, sep]
    for key, lib in [
        ("pastiche", "Lexique pastiche (indicible, ténèbres, effroi…)"),
        ("tics_ia", "Tic d'IA (« une part de moi », « un mélange de »…)"),
        ("exclamation_hors_dialogue", "Point d'exclamation hors dialogue"),
        ("incise_adverbiale",
         "Incise adverbiale ou prépositionnelle (« d'un ton surpris »)"),
        ("elision", "Élision manquante (« je te appelle »)"),
    ]:
        out.append(line(lib, ["✗" if res[n][key] else "✓" for n in names]))
    out.append(line("Passé simple *(candidats, à confirmer)*",
                     ["⚠ " + ", ".join(res[n]["passe_simple"])
                      if res[n]["passe_simple"] else "✓" for n in names]))

    out += ["", "## Mécanique — échec si présent (MANUEL)", "", header, sep]
    for lib in MANUAL_MECHANICS:
        out.append(line(lib, [" "] * len(names)))

    out += ["", "## Structure — échec si absent (AUTO)", "", header, sep]
    out.append(line(
        "Exactement une phrase d'accumulation",
        [f"{'✓' if len(res[n]['accumulations']) == 1 else '✗'} "
         f"({len(res[n]['accumulations'])})" for n in names]))
    out.append(line(
        "≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe",
        [f"{'✓' if res[n]['couperets_fin_para'] else '✗'} "
         f"({len(res[n]['couperets_fin_para'])})" for n in names]))
    out.append(line(
        "Heure ou quantité exacte",
        [f"{'✓' if res[n]['precision'] else '✗'} "
         f"({len(res[n]['precision'])})" for n in names]))

    out += ["", "## Structure — échec si absent (MANUEL)", "", header, sep]
    for lib in MANUAL_STRUCTURE:
        out.append(line(lib, [" "] * len(names)))

    # --- Extensions L1-L4 du protocole de calibration ch. 2 ------------------
    out += ["", "## Protocole ch. 2 — contrôles L1-L4 (AUTO)", "", header, sep]

    out.append(line("Entrées de journal détectées",
                     [str(res[n]["entrees"]) for n in names]))
    # §1 : l'en-tête normalisé est le repère partagé par le comptage L3, la
    # grille, et la bascule audio de `lire_chapitre.py`. Un en-tête malformé
    # ne casse pas que la grille — il casse la scène.
    headers = {n: ENTRY_HEADER.findall(
        strip_frontmatter(Path(p).read_text(encoding="utf-8")))
        for n, p in available}
    out.append(line(
        "En-têtes au format normalisé (« Jour N. Météo. »)",
        [f"{'✓' if headers[n] else '✗'} ({len(headers[n])})" for n in names]))

    # Dates CONSÉCUTIVES et sans doublon. L'objectif de chapitre l'exige, et un
    # carnet dont les entrées se répètent ou reculent n'est plus un carnet.
    # Constaté sur BC : huit en-têtes pour trois entrées, dont un répété cinq
    # fois — le comptage d'en-têtes seul ne l'aurait pas vu.
    def _dates(n: str) -> str:
        days = [int(j) for _, j in headers[n]]
        if not days:
            return "—"
        # DEUX ENTRÉES LE MÊME JOUR sont légitimes : c'est la structure du
        # chapitre 7 (l'après-midi et la nuit de l'anniversaire), et la bascule
        # audio se pose justement sur le second en-tête. La règle avait déjà été
        # apprise à `entetes_coherents` ; cette ligne-ci l'ignorait encore et
        # marquait la structure imposée comme un défaut.
        #
        # Ce qui reste fautif : une date qui RECULE, ou un saut de plus d'un
        # jour entre deux entrées de dates différentes.
        gaps = [b - a for a, b in zip(days, days[1:])]
        step_back = [e for e in gaps if e < 0]
        skipped = [e for e in gaps if e > 1]
        if step_back:
            return f"✗ la date recule : {days}"
        if skipped:
            return f"✗ saut de date : {days}"
        same_ones = gaps.count(0)
        return (f"✓ : {days}" if not same_ones
                else f"✓ : {days} ({same_ones} même jour — structure imposée)")

    out.append(line("Dates consécutives, sans répétition", [_dates(n) for n in names]))

    # L1 — zéro toléré. La détection est une heuristique de majuscule : les
    # occurrences sont citées en annexe pour que la lecture tranche.
    out.append(line(
        "L1 · Noms propres (zéro toléré)",
        [f"{'✓' if not res[n]['l1_noms_propres'] else '✗'} "
         f"({len(res[n]['l1_noms_propres'])})" for n in names]))

    # L2 — en frappe directe sans RAG, une fuite est un échec FICHE/INTERDITS :
    # aucun contexte retrieval ne peut en porter la responsabilité.
    out.append(line(
        "L2 · Fuite lexicale — champ de la mort",
        [f"{'✓' if not res[n]['l2_fuite'] else '✗'} "
         f"({len(res[n]['l2_fuite'])})" for n in names]))
    out.append(line(
        "L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante",
        [f"{'—' if not res[n]['l2_fuite_ambigue'] else '⚠'} "
         f"({len(res[n]['l2_fuite_ambigue'])})" for n in names]))

    # L3 — exactement une accumulation PAR ENTRÉE (D1), aux seuils que la fiche
    # v3 énonce (60 mots, 6 virgules), et non aux seuils de la session 1.
    def _l3(n: str) -> str:
        per_entry = res[n]["l3_par_entree"]
        count = [len(e) for e in per_entry]
        ok = count and all(c == 1 for c in count)
        recop = sum(len(e) for e in res[n]["l3_recopies"])
        mark = "✓" if ok else "✗"
        detail = "/".join(str(c) for c in count) or "0"
        return f"{mark} ({detail})" + (f" ⛔{recop} recopie(s)" if recop else "")

    # L3 EXEMPTÉ quand la table met le chapitre hors échelle — le chapitre 7
    # n'exige pas d'accumulation, elle y est autorisée. Afficher « ✗ (0) » sur
    # un contrôle non exigé, c'est un vert impossible lu comme un défaut : le
    # tirage 6 en portait un.
    l3_exempt = bool(constraints
                      and "hors échelle" in (constraints.get("verdict") or ""))
    out.append(line(
        f"L3 · Accumulation par entrée (≥{L3_WORDS} mots, ≥{L3_COMMAS} virg.)"
        + (" — *non exigée à ce chapitre*" if l3_exempt else ""),
        ["— non exigée" if l3_exempt else _l3(n) for n in names]))

    # L4 — le glissement est le seul emploi autorisé des « … ». Deux façons
    # d'échouer : trop d'occurrences, ou une occurrence loin du champ du départ.
    def _l4(n: str) -> str:
        per_entry = res[n]["l4_par_entree"]
        total = sum(c for c, _ in per_entry)
        too_many = any(c > 1 for c, _ in per_entry)
        outside = sum(len(h) for _, h in per_entry)
        if too_many or outside:
            reasons = []
            if too_many:
                reasons.append(">1/entrée")
            if outside:
                reasons.append(f"{outside} hors champ")
            return f"✗ ({total}) " + ", ".join(reasons)
        # Zéro occurrence passe L4 tel que le protocole le formule (il ne
        # sanctionne que l'excès et le hors-champ) mais échoue M1, qui en exige
        # au moins un. Le dire ici : une coche isolée se lirait comme « tenu ».
        if total == 0:
            return "✓ (0) — mais aucun glissement, échec M1"
        return f"✓ ({total})"

    out.append(line("L4 · Points de suspension = glissement seul",
                     [_l4(n) for n in names]))

    # --- Interdits SCOPÉS par chapitre (notes §3 et §4) ---------------------
    if constraints:
        # `strip_frontmatter` est OBLIGATOIRE ici : le frontmatter d'un run
        # recopie le brief, lequel NOMME les termes réservés pour les
        # interdire. Sans cette coupe, tout run conforme sortait à trois
        # violations — la grille sanctionnait le brief, pas le texte.
        scope = {n: chapter_checks(
            strip_frontmatter(Path(p).read_text(encoding="utf-8")), constraints)
            for n, p in available}
        out += ["", f"## Chapitre {constraints['chapter']} — interdits scopés "
                    "(AUTO)", "",
                f"Verdict imposé : **{constraints['verdict'] or '—'}** · "
                f"objets actifs : {constraints['active_objects'] or '—'}", "",
                header, sep]
        out.append(line(
            "Verdict du chapitre présent (lint EN PRÉSENCE)",
            [("—" if not constraints["verdict_attendu"]
              else "✓" if not scope[n]["verdict"] else "✗") for n in names]))
        out.append(line(
            "Termes réservés absents (la tierce, l'errata, le bon à tirer)",
            [f"{'✓' if not scope[n]['reserves'] else '✗'} "
             f"({len(scope[n]['reserves'])})" for n in names]))
        out.append(line(
            f"Quatuor réservé ch. 7 absent"
            f"{'' if constraints['quatuor_interdit'] else ' — N/A ici'}",
            [("—" if not constraints["quatuor_interdit"]
              else f"{'✓' if not scope[n]['quatuor'] else '✗'} "
                   f"({len(scope[n]['quatuor'])})") for n in names]))
        # INTERDITS MATÉRIELS — le décor générique de nemo, en DRAPEAU sur le
        # texte d'écriture. Bloquant dans `accumulate` (le validateur relance),
        # drapeau ici : automatiser un contrôle et le rendre bloquant sont deux
        # décisions distinctes, et un run ne doit pas échouer sur un mot de
        # mobilier pendant que la masse et les gestes passent. La famille est
        # nommée pour que la lecture sache quoi chercher.
        out.append(line(
            "⚑ Interdits matériels *(drapeau — décor hors du monde)*",
            [(lambda fam: f"{'—' if not fam else '⚑'} "
                          f"({', '.join(sorted(fam)) or '0'})")(
                {x.split(" : ")[0] for x in scope[n]["materiels"]})
             for n in names]))

    # --- Session 5 : les cinq détecteurs, ENFIN branchés ---------------------
    #
    # Ils existaient tous dans `lint_style` et aucun n'atteignait la grille :
    # ils calculaient, et on jetait le résultat. C'est pour ça que « Demain est
    # un autre jour » est passé sans croix en B′3 — l'instrument n'était pas
    # troué, il était débranché. Le lint fantôme est la forme la plus coûteuse
    # d'échec d'outillage, parce qu'elle se lit comme un succès.
    out += ["", "## Sessions 5-6 — voix, formulaire et décor (AUTO)", "",
            header, sep]
    for key, lib in [
        ("attracteurs", "Attracteurs *(familles : folie, demain qui résout, "
                        "bouée/océan)*"),
        ("meta_termes", "Méta-termes en sortie (couperet, squelette, beat…)"),
        ("formulaire", "Formulaire par paraphrase (« … est le suivant : »)"),
        # Session 6 : les instances ne sont plus servies au modèle (la section
        # *Interdits* ne garde que les catégories), donc elles se vérifient ici.
        # Sans cette ligne, fermer « perplexe » au service l'aurait rendu
        # invisible au lieu de le rendre absent.
        ("etats_mentaux", "État mental nommé en apposition *(perplexe, "
                          "songeuse, incrédule…)*"),
        # Une marque déposée date le texte et le sort du monde clos de la
        # maison. L1 la voyait déjà comme nom propre, mais noyée : on la nomme
        # pour pouvoir la retirer.
        ("marques", "Marque déposée *(Bluetooth, Frigidaire…)*"),
    ]:
        out.append(line(lib, [f"{'✓' if not res[n].get(key) else '✗'} "
                              f"({len(res[n].get(key) or [])})" for n in names]))

    # DRAPEAUX, non bloquants. L'arbitrage 1B a sorti le plafond de M3 comme
    # lint séparé — « drapeau posé ». Le rendre bloquant ferait échouer un run
    # entier sur un tic à deux occurrences alors que L3 et M1 passeraient ;
    # automatiser un contrôle et le rendre bloquant sont deux décisions
    # distinctes. M3 reste la ligne manuelle qui tranche le couple.
    out.append(line(
        "⚑ « je décide de » ≤ 1/entrée *(drapeau, non bloquant)*",
        [(lambda c: f"{'—' if all(x <= 1 for x in c) else '⚑'} "
                    f"({'/'.join(map(str, c)) or '0'})")(
            res[n].get("je_decide_par_entree") or [0]) for n in names]))
    out.append(line(
        "⚑ Couple décision-exécution *(candidat, M3 tranche)*",
        [f"{'—' if not res[n].get('couples_m3') else '⚑'} "
         f"({len(res[n].get('couples_m3') or [])})" for n in names]))
    out.append(line(
        "En-têtes cohérents (jour de semaine ↔ date)",
        [f"{'✓' if not res[n].get('entetes_incoherents') else '✗'} "
         f"({len(res[n].get('entetes_incoherents') or [])})" for n in names]))

    # L'ACCUMULATION QUI SE RÉSUME. Bloquant DANS le nœud (le validateur
    # relance), donc une croix ici signale que le nœud a rendu son dernier essai
    # malgré tout — pas un défaut de plume, un défaut de dispositif.
    # Le ratio est affiché, pas seulement le verdict : le seuil de 0,20 est un
    # arbitrage, et il doit rester rediscutable avec les chiffres sous les yeux.
    def _summary(n: str) -> str:
        ratios = res[n].get("accumulations_abstraction") or []
        if not ratios:
            return "— (aucune accumulation)"
        mark = "✓" if all(r <= ACC_ABSTRACT_MAX for r in ratios) else "✗"
        return f"{mark} ({'/'.join(f'{r:.0%}' for r in ratios)})"

    out.append(line(
        "Accumulation d'étapes, non de beats *(≤ 20 % d'items abstraits)*",
        [_summary(n) for n in names]))

    # M1 EN CONTRÔLE DE COMPOSITION (session 6, §2). Le glissement ne se demande
    # plus au modèle : il se prend en banque, le code le coupe et le colle. Ce
    # qui se vérifie donc n'est plus « le modèle a-t-il produit le geste » mais
    # « la composition a-t-elle tenu ses promesses » — présence, unicité,
    # conformité L4. Vert par construction, et c'est le but : la ligne M1
    # manuelle reste, pour le jugement à l'oral qu'aucun compteur ne remplace.
    #
    # La position et la non-adjacence sont garanties dans `gestes.assembler` et
    # ne sont PAS re-vérifiées ici : elles n'existent qu'en offsets, invisibles
    # dans le texte rendu. Le dire plutôt que laisser croire que la ligne les
    # couvre — une grille muette sur un critère se lit comme un critère tenu.
    def _compo(n: str) -> str:
        per_entry = res[n].get("l4_par_entree") or []
        if not per_entry:
            return "—"
        total = sum(c for c, _ in per_entry)
        outside = sum(len(h) for _, h in per_entry)
        too_many = [c for c, _ in per_entry if c > 1]
        if not total:
            return "✗ (aucun glissement)"
        if outside or too_many:
            return (f"✗ ({total} posé(s), {outside} non conforme(s), "
                    f"{len(too_many)} entrée(s) à plus d'un)")
        return f"✓ ({total} posé(s), un par entrée, conformes)"

    # LA REDITE — bloquante. Le code retire le doublon à l'assemblage (cf.
    # `graph.poser_gestes_node`), donc une croix ici signale ce qu'il n'a pas su
    # retirer : une redite trop reformulée pour le seuil, ou une phrase reprise
    # dans un paragraphe par ailleurs différent. Ce que le CODE compose est
    # exclu des deux comptes — en-têtes, ancre, glissements se répètent par
    # fonction, et les compter aurait fait retirer la bascule et le geste.
    out.append(line(
        "Aucun paragraphe redit *(similarité ≥ 50 %, hors artefacts du code)*",
        [(lambda r: f"{'✓' if not r else '✗'} ({len(r)})")(
            res[n].get("paragraphes_redits") or []) for n in names]))
    # LA PERSONNE de l'accumulation — bloquante dans le nœud, donc une croix
    # ici signale que le dernier essai est passé malgré tout.
    out.append(line(
        "Accumulation à la première personne",
        [(lambda r: f"{'✓' if not r else '✗'} ({len(r)})")(
            res[n].get("accumulations_3p") or []) for n in names]))
    # LES CITATIONS FABRIQUÉES — drapeau. L'ancre et le verdict sont retirés du
    # compte par `citations_hors_ancre` quand on les lui donne ; ici la grille
    # ne connaît pas l'ancre du run, donc elle passe l'ancre du chapitre.
    out.append(line(
        "⚑ Citation hors ancre *(drapeau — le cahier est fourni, pas fabriqué)*",
        [(lambda r: f"{'—' if not r else '⚑'} ({len(r)})")(
            [c for c in (res[n].get("citations") or [])
             if not (constraints and constraints.get("verdict")
                     and constraints["verdict"].split("(")[0].strip().lower()
                     in c.lower())]) for n in names]))
    out.append(line(
        "Aucune phrase reprise d'un paragraphe à l'autre",
        [(lambda r: f"{'✓' if not r else '✗'} ({len(r)})")(
            res[n].get("phrases_redites") or []) for n in names]))

    out.append(line(
        "M1 · composition du glissement *(présence, unicité, conformité L4)*",
        [_compo(n) for n in names]))

    out += ["", "## Protocole ch. 2 — contrôles M1-M4 (MANUEL)", "", header, sep]
    for lib in MANUAL_PROTOCOL:
        out.append(line(lib, [" "] * len(names)))

    out += ["", "## Oral — jugement à la lecture (MANUEL, debout, chronométré)",
            "", header, sep]
    for lib in MANUAL_ORAL:
        out.append(line(lib, [" "] * len(names)))

    out += ["", "## Preuves des croix automatiques", ""]
    for n in names:
        evidence = []
        for key, lib in [("pastiche", "pastiche"), ("tics_ia", "tic d'IA"),
                         ("exclamation_hors_dialogue", "exclamation"),
                         ("incise_adverbiale", "incise"),
                         ("elision", "élision"),
                         ("attracteurs", "attracteur"),
                         ("meta_termes", "méta-terme"),
                         ("formulaire", "formulaire"),
                         ("couples_m3", "⚑ couple décision-exécution"),
                         ("entetes_incoherents", "en-tête incohérent")]:
            for e in res[n][key]:
                evidence.append(f"  - **{lib}** : `{e}`")
        for a in res[n]["accumulations"]:
            evidence.append(f"  - **accumulation** : `{a[:150]}…`")
        for w in res[n]["delint"]:
            evidence.append(f"  - **delint** : {w}")
        for occ in res[n]["l1_noms_propres"]:
            evidence.append(f"  - **L1 nom propre** : `{occ}`")
        if res[n]["l2_fuite"]:
            evidence.append("  - **L2 fuite** : "
                           + ", ".join(f"`{m}`" for m in res[n]["l2_fuite"]))
        if res[n]["l2_fuite_ambigue"]:
            evidence.append("  - **L2b ambigu** : "
                           + ", ".join(f"`{m}`" for m in res[n]["l2_fuite_ambigue"]))
        for i, acc in enumerate(res[n]["l3_par_entree"], start=1):
            for a in acc:
                evidence.append(f"  - **L3 entrée {i}** : `{a[:150]}…`")
        for i, rec in enumerate(res[n]["l3_recopies"], start=1):
            for a in rec:
                evidence.append(f"  - **L3 entrée {i} ⛔ ÉTALON RECOPIÉ** : `{a[:110]}…`")
        for i, (_, outside) in enumerate(res[n]["l4_par_entree"], start=1):
            for h in outside:
                evidence.append(f"  - **L4 entrée {i}, hors champ du départ** : `{h}`")
        if evidence:
            out.append(f"- **{n}**")
            out += evidence
        else:
            out.append(f"- **{n}** — aucune croix automatique.")

    out += [
        "",
        "## Lecture du run de contrôle",
        "",
        "Le contrôle (brief sans les 5 lignes « Régime : … ») ne se score pas "
        "comme les autres. Trois lectures possibles, à cocher :",
        "",
        "- [ ] **Bascules tenues sans les lignes régime** → le style ET la "
        "dramaturgie vivent dans la fiche. Meilleur cas.",
        "- [ ] **Voix tenue mais registre monotone** → la fiche porte la voix, "
        "le plan de scènes devra porter la dramaturgie. `plan_node` devra "
        "émettre une directive de régime par beat.",
        "- [ ] **Voix perdue** → la fiche ne tient pas sans béquille. "
        "Retravailler les chunks *voix* et *interdits* avant tout câblage.",
        "",
        "## Verdict",
        "",
        "- [ ] Fiche validée en l'état (≥ 80 % de la grille sur les 3 runs)",
        "- [ ] Chunks à durcir : ______________________",
        "- [ ] Relève du pipeline, pas de la fiche : ______________________",
        "- [ ] Température à revoir : ______________________",
        "",
        "Notes :",
        "",
    ]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
