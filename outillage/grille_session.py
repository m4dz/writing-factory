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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_style import (ENTETE_ENTREE, L3_MOTS, L3_VIRGULES,  # noqa: E402
                        analyse, contraintes_chapitre, controles_chapitre,
                        strip_frontmatter)

def decouvrir(dossier: str = "runs") -> list[tuple[str, Path]]:
    """Tous les runs présents, runs standard d'abord puis contrôles.

    Découverte par glob et non liste figée : le protocole prévoit de relancer un
    tirage pour lever une zone grise, et une grille qui ignorerait le run
    supplémentaire ferait décider sur des données incomplètes.
    """
    def cle(f: Path) -> tuple[int, int, str]:
        """Ordre de lecture : runs de score, puis contrôle, puis exploration.

        C'est l'ordre du protocole, et il porte du sens : on lit d'abord ce qui
        est scoré, ensuite ce qui l'éclaire. Un tri alphabétique mettrait le
        contrôle entre les runs 1 et 2, et placerait `run-controle-2` AVANT
        `run-controle` (le tiret précède le point) — de quoi comparer les
        mauvaises colonnes.
        """
        nom = f.stem.removeprefix("run-")
        num = re.search(r"(\d+)", nom)
        rang = int(num.group(1)) if num else 1
        if nom.lower().startswith("x"):
            famille = 2                      # exploration, hors score
        elif nom.upper().endswith("C") or nom.lower().startswith(
                ("c", "controle", "contrôle")):
            # `AC`/`BC` sont les chapitres complets hors score : ils se lisent
            # APRÈS les runs scorés, comme le contrôle. Sans ce cas, `AC` se
            # rangeait entre A1 et A2 (rang 1, faute de chiffre).
            famille = 1
        else:
            famille = 0                      # runs de score
        return (famille, rang, nom)

    def nommer(f: Path) -> str:
        nom = f.stem.removeprefix("run-")
        if nom.lower().startswith(("controle", "contrôle")):
            return "Contrôle" + nom[8:]
        if nom.upper() == "C":
            return "Contrôle"
        if nom.lower().startswith("x"):
            return nom.upper()               # X1, X2 — exploration
        return f"Run {nom}"

    fichiers = sorted(Path(dossier).glob("run-*.md"), key=cle)
    return [(nommer(f), f) for f in fichiers]

# Lignes que le code ne peut PAS trancher sans comprendre le texte. Elles sont
# listées explicitement plutôt qu'omises : une grille silencieuse sur une ligne
# se lit comme une ligne tenue.
MANUELLES_MECANIQUE = [
    "Deux adjectifs ou plus coordonnés sur un même nom",
    "Émotion annoncée avant d'être montrée",
    "Météo ou obscurité corrélée à la tension",
    "Information hors du champ perceptif du narrateur",
    "Doute résolu, dans un sens ou dans l'autre",
]
MANUELLES_STRUCTURE = [
    "Une vérification matérielle de l'anomalie (le geste, décrit)",
    "Le décalage dans le dialogue (la sœur répond à côté)",
    "Les cinq beats présents, dans l'ordre",
]
# M1-M4 du protocole de calibration ch. 2. Explicitement NON automatisés : ils
# demandent de lire, pas de compter. Les laisser en lignes vides plutôt que de
# les omettre — une grille muette sur une ligne se lit comme une ligne tenue.
MANUELLES_PROTOCOLE = [
    "M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, "
    "puis retour immédiat à un fait matériel",
    "M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence "
    "(échec si complice ou neutre)",
    "M3 · Décision sans geste — toute décision est notée, aucune exécution "
    "racontée en scène",
    "M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire "
    "de la narratrice",
]

MANUELLES_ORAL = [
    "Tenu en moins de 2 minutes à voix haute",
    "Aucune phrase reprise deux fois pour la comprendre",
    "Le style est audible : quelqu'un qui a entendu les étalons "
    "reconnaîtrait la voix",
]


def frontmatter(chemin: Path) -> dict:
    """Lit le frontmatter du run (température, done_reason, durée…)."""
    meta, dans = {}, False
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if ligne.strip() == "---":
            if dans:
                break
            dans = True
            continue
        if dans and ":" in ligne:
            k, v = ligne.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def ligne(libelle: str, cellules: list[str]) -> str:
    return f"| {libelle} | " + " | ".join(cellules) + " |"


def main() -> int:
    # Une session par dossier : les runs de la fiche v1 restent lisibles quand
    # la v2 tourne. Comparer deux versions de la fiche suppose de garder les
    # deux jeux de tirages.
    dossier = sys.argv[1] if len(sys.argv) > 1 else "runs"
    # La cible de longueur change avec le brief : 400-550 pour la scène test de
    # la session 1, 450-600 pour le chapitre 2. Codée en dur, elle aurait
    # affiché « hors cible » sur des runs conformes — un faux défaut, et le
    # genre qui envoie durcir une section qui va bien.
    cible = sys.argv[2] if len(sys.argv) > 2 else "400-600"
    cible_min, cible_max = (int(x) for x in cible.split("-"))
    # Numéro de chapitre : active les interdits SCOPÉS (notes §3 et §4). Sans
    # lui, la grille ne peut pas savoir que « la tierce » est légitime au
    # chapitre 9 et interdite au 2 — et un interdit qui ne connaît pas sa
    # portée est soit inutile, soit faux.
    chapitre = int(sys.argv[3]) if len(sys.argv) > 3 else None
    contraintes = contraintes_chapitre(chapitre) if chapitre else None
    dispo = decouvrir(dossier)
    if not dispo:
        print("ERREUR : aucun run dans runs/.", file=sys.stderr)
        return 1

    res = {nom: analyse(p.read_text(encoding="utf-8")) for nom, p in dispo}
    meta = {nom: frontmatter(p) for nom, p in dispo}
    noms = [nom for nom, _ in dispo]
    entete = "| Contrôle attendu | " + " | ".join(noms) + " |"
    sep = "|---|" + "---|" * len(noms)

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
        "## Conditions des runs",
        "",
        "| | " + " | ".join(noms) + " |",
        sep,
    ]
    # Plusieurs clés possibles par ligne : les runs de sessions différentes
    # n'écrivent pas le même frontmatter, et une grille qui n'en connaît qu'un
    # affiche « ? » sur des données présentes.
    for cles, lib in [(("temperature",), "Température"),
                      (("mots",), "Mots"),
                      (("duree_s", "duree_totale_s"), "Durée (s)"),
                      (("done_reason",), "done_reason"),
                      (("entrees_generees",), "Entrées générées"),
                      (("garde_fou_60",), "Garde-fou 60 % déclenché"),
                      (("temps_par_noeud",), "Temps par nœud (s)")]:
        valeurs = [next((meta[n][c] for c in cles if meta[n].get(c)), "—")
                   for n in noms]
        if any(v != "—" for v in valeurs):
            out.append(ligne(lib, valeurs))
    out.append(ligne(f"Cible {cible_min}-{cible_max}",
                     ["✓" if cible_min <= res[n]["mots"] <= cible_max
                      else "✗ hors cible" for n in noms]))

    out += ["", "## Mécanique — échec si présent (AUTO)", "", entete, sep]
    for cle, lib in [
        ("pastiche", "Lexique pastiche (indicible, ténèbres, effroi…)"),
        ("tics_ia", "Tic d'IA (« une part de moi », « un mélange de »…)"),
        ("exclamation_hors_dialogue", "Point d'exclamation hors dialogue"),
        ("incise_adverbiale",
         "Incise adverbiale ou prépositionnelle (« d'un ton surpris »)"),
        ("elision", "Élision manquante (« je te appelle »)"),
    ]:
        out.append(ligne(lib, ["✗" if res[n][cle] else "✓" for n in noms]))
    out.append(ligne("Passé simple *(candidats, à confirmer)*",
                     ["⚠ " + ", ".join(res[n]["passe_simple"])
                      if res[n]["passe_simple"] else "✓" for n in noms]))

    out += ["", "## Mécanique — échec si présent (MANUEL)", "", entete, sep]
    for lib in MANUELLES_MECANIQUE:
        out.append(ligne(lib, [" "] * len(noms)))

    out += ["", "## Structure — échec si absent (AUTO)", "", entete, sep]
    out.append(ligne(
        "Exactement une phrase d'accumulation",
        [f"{'✓' if len(res[n]['accumulations']) == 1 else '✗'} "
         f"({len(res[n]['accumulations'])})" for n in noms]))
    out.append(ligne(
        "≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe",
        [f"{'✓' if res[n]['couperets_fin_para'] else '✗'} "
         f"({len(res[n]['couperets_fin_para'])})" for n in noms]))
    out.append(ligne(
        "Heure ou quantité exacte",
        [f"{'✓' if res[n]['precision'] else '✗'} "
         f"({len(res[n]['precision'])})" for n in noms]))

    out += ["", "## Structure — échec si absent (MANUEL)", "", entete, sep]
    for lib in MANUELLES_STRUCTURE:
        out.append(ligne(lib, [" "] * len(noms)))

    # --- Extensions L1-L4 du protocole de calibration ch. 2 ------------------
    out += ["", "## Protocole ch. 2 — contrôles L1-L4 (AUTO)", "", entete, sep]

    out.append(ligne("Entrées de journal détectées",
                     [str(res[n]["entrees"]) for n in noms]))
    # §1 : l'en-tête normalisé est le repère partagé par le comptage L3, la
    # grille, et la bascule audio de `lire_chapitre.py`. Un en-tête malformé
    # ne casse pas que la grille — il casse la scène.
    entetes = {n: ENTETE_ENTREE.findall(
        strip_frontmatter(Path(p).read_text(encoding="utf-8")))
        for n, p in dispo}
    out.append(ligne(
        "En-têtes au format normalisé (« Jour N. Météo. »)",
        [f"{'✓' if entetes[n] else '✗'} ({len(entetes[n])})" for n in noms]))

    # Dates CONSÉCUTIVES et sans doublon. L'objectif de chapitre l'exige, et un
    # carnet dont les entrées se répètent ou reculent n'est plus un carnet.
    # Constaté sur BC : huit en-têtes pour trois entrées, dont un répété cinq
    # fois — le comptage d'en-têtes seul ne l'aurait pas vu.
    def _dates(n: str) -> str:
        jours = [int(j) for _, j in entetes[n]]
        if not jours:
            return "—"
        doublons = len(jours) - len(set(jours))
        suite = all(b - a == 1 for a, b in zip(jours, jours[1:]))
        if doublons:
            return f"✗ {doublons} doublon(s) : {jours}"
        return f"{'✓' if suite else '✗ non consécutives'} : {jours}"

    out.append(ligne("Dates consécutives, sans répétition", [_dates(n) for n in noms]))

    # L1 — zéro toléré. La détection est une heuristique de majuscule : les
    # occurrences sont citées en annexe pour que la lecture tranche.
    out.append(ligne(
        "L1 · Noms propres (zéro toléré)",
        [f"{'✓' if not res[n]['l1_noms_propres'] else '✗'} "
         f"({len(res[n]['l1_noms_propres'])})" for n in noms]))

    # L2 — en frappe directe sans RAG, une fuite est un échec FICHE/INTERDITS :
    # aucun contexte retrieval ne peut en porter la responsabilité.
    out.append(ligne(
        "L2 · Fuite lexicale — champ de la mort",
        [f"{'✓' if not res[n]['l2_fuite'] else '✗'} "
         f"({len(res[n]['l2_fuite'])})" for n in noms]))
    out.append(ligne(
        "L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante",
        [f"{'—' if not res[n]['l2_fuite_ambigue'] else '⚠'} "
         f"({len(res[n]['l2_fuite_ambigue'])})" for n in noms]))

    # L3 — exactement une accumulation PAR ENTRÉE (D1), aux seuils que la fiche
    # v3 énonce (60 mots, 6 virgules), et non aux seuils de la session 1.
    def _l3(n: str) -> str:
        par_entree = res[n]["l3_par_entree"]
        compte = [len(e) for e in par_entree]
        ok = compte and all(c == 1 for c in compte)
        recop = sum(len(e) for e in res[n]["l3_recopies"])
        marque = "✓" if ok else "✗"
        detail = "/".join(str(c) for c in compte) or "0"
        return f"{marque} ({detail})" + (f" ⛔{recop} recopie(s)" if recop else "")

    out.append(ligne(
        f"L3 · Accumulation par entrée (≥{L3_MOTS} mots, ≥{L3_VIRGULES} virg.)",
        [_l3(n) for n in noms]))

    # L4 — le glissement est le seul emploi autorisé des « … ». Deux façons
    # d'échouer : trop d'occurrences, ou une occurrence loin du champ du départ.
    def _l4(n: str) -> str:
        par_entree = res[n]["l4_par_entree"]
        total = sum(c for c, _ in par_entree)
        trop = any(c > 1 for c, _ in par_entree)
        hors = sum(len(h) for _, h in par_entree)
        if trop or hors:
            raisons = []
            if trop:
                raisons.append(">1/entrée")
            if hors:
                raisons.append(f"{hors} hors champ")
            return f"✗ ({total}) " + ", ".join(raisons)
        # Zéro occurrence passe L4 tel que le protocole le formule (il ne
        # sanctionne que l'excès et le hors-champ) mais échoue M1, qui en exige
        # au moins un. Le dire ici : une coche isolée se lirait comme « tenu ».
        if total == 0:
            return "✓ (0) — mais aucun glissement, échec M1"
        return f"✓ ({total})"

    out.append(ligne("L4 · Points de suspension = glissement seul",
                     [_l4(n) for n in noms]))

    # --- Interdits SCOPÉS par chapitre (notes §3 et §4) ---------------------
    if contraintes:
        # `strip_frontmatter` est OBLIGATOIRE ici : le frontmatter d'un run
        # recopie le brief, lequel NOMME les termes réservés pour les
        # interdire. Sans cette coupe, tout run conforme sortait à trois
        # violations — la grille sanctionnait le brief, pas le texte.
        scope = {n: controles_chapitre(
            strip_frontmatter(Path(p).read_text(encoding="utf-8")), contraintes)
            for n, p in dispo}
        out += ["", f"## Chapitre {contraintes['chapitre']} — interdits scopés "
                    "(AUTO)", "",
                f"Verdict imposé : **{contraintes['verdict'] or '—'}** · "
                f"objets actifs : {contraintes['objets_actifs'] or '—'}", "",
                entete, sep]
        out.append(ligne(
            "Verdict du chapitre présent (lint EN PRÉSENCE)",
            [("—" if not contraintes["verdict_attendu"]
              else "✓" if not scope[n]["verdict"] else "✗") for n in noms]))
        out.append(ligne(
            "Termes réservés absents (la tierce, l'errata, le bon à tirer)",
            [f"{'✓' if not scope[n]['reserves'] else '✗'} "
             f"({len(scope[n]['reserves'])})" for n in noms]))
        out.append(ligne(
            f"Quatuor réservé ch. 7 absent"
            f"{'' if contraintes['quatuor_interdit'] else ' — N/A ici'}",
            [("—" if not contraintes["quatuor_interdit"]
              else f"{'✓' if not scope[n]['quatuor'] else '✗'} "
                   f"({len(scope[n]['quatuor'])})") for n in noms]))

    # --- Session 5 : les cinq détecteurs, ENFIN branchés ---------------------
    #
    # Ils existaient tous dans `lint_style` et aucun n'atteignait la grille :
    # ils calculaient, et on jetait le résultat. C'est pour ça que « Demain est
    # un autre jour » est passé sans croix en B′3 — l'instrument n'était pas
    # troué, il était débranché. Le lint fantôme est la forme la plus coûteuse
    # d'échec d'outillage, parce qu'elle se lit comme un succès.
    out += ["", "## Session 5 — voix et formulaire (AUTO)", "", entete, sep]
    for cle, lib in [
        ("attracteurs", "Attracteurs (« Demain est un autre jour », bouée, océan)"),
        ("meta_termes", "Méta-termes en sortie (couperet, squelette, beat…)"),
        ("formulaire", "Formulaire par paraphrase (« … est le suivant : »)"),
    ]:
        out.append(ligne(lib, [f"{'✓' if not res[n].get(cle) else '✗'} "
                              f"({len(res[n].get(cle) or [])})" for n in noms]))

    # DRAPEAUX, non bloquants. L'arbitrage 1B a sorti le plafond de M3 comme
    # lint séparé — « drapeau posé ». Le rendre bloquant ferait échouer un run
    # entier sur un tic à deux occurrences alors que L3 et M1 passeraient ;
    # automatiser un contrôle et le rendre bloquant sont deux décisions
    # distinctes. M3 reste la ligne manuelle qui tranche le couple.
    out.append(ligne(
        "⚑ « je décide de » ≤ 1/entrée *(drapeau, non bloquant)*",
        [(lambda c: f"{'—' if all(x <= 1 for x in c) else '⚑'} "
                    f"({'/'.join(map(str, c)) or '0'})")(
            res[n].get("je_decide_par_entree") or [0]) for n in noms]))
    out.append(ligne(
        "⚑ Couple décision-exécution *(candidat, M3 tranche)*",
        [f"{'—' if not res[n].get('couples_m3') else '⚑'} "
         f"({len(res[n].get('couples_m3') or [])})" for n in noms]))
    out.append(ligne(
        "En-têtes cohérents (jour de semaine ↔ date)",
        [f"{'✓' if not res[n].get('entetes_incoherents') else '✗'} "
         f"({len(res[n].get('entetes_incoherents') or [])})" for n in noms]))

    out += ["", "## Protocole ch. 2 — contrôles M1-M4 (MANUEL)", "", entete, sep]
    for lib in MANUELLES_PROTOCOLE:
        out.append(ligne(lib, [" "] * len(noms)))

    out += ["", "## Oral — jugement à la lecture (MANUEL, debout, chronométré)",
            "", entete, sep]
    for lib in MANUELLES_ORAL:
        out.append(ligne(lib, [" "] * len(noms)))

    out += ["", "## Preuves des croix automatiques", ""]
    for n in noms:
        preuves = []
        for cle, lib in [("pastiche", "pastiche"), ("tics_ia", "tic d'IA"),
                         ("exclamation_hors_dialogue", "exclamation"),
                         ("incise_adverbiale", "incise"),
                         ("elision", "élision"),
                         ("attracteurs", "attracteur"),
                         ("meta_termes", "méta-terme"),
                         ("formulaire", "formulaire"),
                         ("couples_m3", "⚑ couple décision-exécution"),
                         ("entetes_incoherents", "en-tête incohérent")]:
            for e in res[n][cle]:
                preuves.append(f"  - **{lib}** : `{e}`")
        for a in res[n]["accumulations"]:
            preuves.append(f"  - **accumulation** : `{a[:150]}…`")
        for w in res[n]["delint"]:
            preuves.append(f"  - **delint** : {w}")
        for occ in res[n]["l1_noms_propres"]:
            preuves.append(f"  - **L1 nom propre** : `{occ}`")
        if res[n]["l2_fuite"]:
            preuves.append("  - **L2 fuite** : "
                           + ", ".join(f"`{m}`" for m in res[n]["l2_fuite"]))
        if res[n]["l2_fuite_ambigue"]:
            preuves.append("  - **L2b ambigu** : "
                           + ", ".join(f"`{m}`" for m in res[n]["l2_fuite_ambigue"]))
        for i, acc in enumerate(res[n]["l3_par_entree"], start=1):
            for a in acc:
                preuves.append(f"  - **L3 entrée {i}** : `{a[:150]}…`")
        for i, rec in enumerate(res[n]["l3_recopies"], start=1):
            for a in rec:
                preuves.append(f"  - **L3 entrée {i} ⛔ ÉTALON RECOPIÉ** : `{a[:110]}…`")
        for i, (_, hors) in enumerate(res[n]["l4_par_entree"], start=1):
            for h in hors:
                preuves.append(f"  - **L4 entrée {i}, hors champ du départ** : `{h}`")
        if preuves:
            out.append(f"- **{n}**")
            out += preuves
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
