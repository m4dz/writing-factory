#!/usr/bin/env python3
"""Assemble the four-column session grid from the run files.

Crosses the FINE grid of `_scene-test-style.md` (mechanics / structure / oral,
2-runs-out-of-3 rule) with the four-column layout of the lint grid. Lines the
code can decide are filled by `factory.eval.lint`; the others stay empty for
the reader, who fills them aloud (doctrine 3: counting is not reading).

Regenerated at every iteration of the sheet, hence a program rather than a
hand-copied file: a transcribed grid drifts from what the runs actually say,
and that drift is paid when deciding which chunk to harden.

Usage:
  factory eval grid <runs-dir> [min-max] [chapter] > grid.md
"""

import re
import sys
from pathlib import Path

from factory.eval.lint import (ACC_ABSTRACT_MAX, ENTRY_HEADER,
                        L3_WORDS, L3_COMMAS,
                        analyze, chapter_constraints, chapter_checks,
                        strip_frontmatter)

def discover(folder: str = "runs") -> list[tuple[str, Path]]:
    """Every run present, scored runs first, then controls.

    Discovery by glob, not a fixed list: the protocol allows relaunching a draw
    to settle a grey zone, and a grid ignoring the extra run would decide from
    incomplete data.
    """
    def key(f: Path) -> tuple[int, int, str]:
        """Reading order: scored runs, then control, then exploration.

        The protocol's order, and it carries meaning: read what is scored first,
        then what illuminates it. An alphabetical sort would put the control
        between runs 1 and 2 and `run-controle-2` BEFORE `run-controle` (the
        hyphen sorts before the period): the wrong columns compared.
        """
        name = f.stem.removeprefix("run-")
        num = re.search(r"(\d+)", name)
        rank = int(num.group(1)) if num else 1
        if name.lower().startswith("x"):
            family = 2                      # exploration, outside the score
        elif name.upper().endswith("C") or name.lower().startswith(
                ("c", "controle", "contrôle")):
            # `AC`/`BC` are the full chapters outside the score: read AFTER the
            # scored runs, like the control. Without this case `AC` sorted
            # between A1 and A2 (rank 1, having no digit).
            family = 1
        else:
            family = 0                      # scored runs
        return (family, rank, name)

    def name_for(f: Path) -> str:
        name = f.stem.removeprefix("run-")
        if name.lower().startswith(("controle", "contrôle")):
            return "Contrôle" + name[8:]
        if name.upper() == "C":
            return "Contrôle"
        if name.lower().startswith("x"):
            return name.upper()               # X1, X2: exploration
        return f"Run {name}"

    files = sorted(Path(folder).glob("run-*.md"), key=key)
    return [(name_for(f), f) for f in files]

# Lines the code CANNOT settle without understanding the text. Listed explicitly
# rather than omitted: a grid silent about a line reads as a line held.
# THE JUDGE. One manual line, first: the automatic grid no longer says whether
# the text is good, it says whether it is disqualified (ADR-0019, doctrine 3).
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
# M1-M4 of the chapter 2 calibration protocol. Explicitly NOT automated: they
# require reading, not counting. Kept as empty lines rather than omitted: a grid
# silent about a line reads as a line held.
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
    """Read the run's frontmatter (temperature, done_reason, duration…)."""
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
    # One session per folder: the runs of sheet v1 stay readable while v2 runs.
    # Comparing two sheet versions requires keeping both sets of draws.
    folder = argv[0] if len(argv) > 0 else "runs"
    # The length target moves with the brief: 400-550 for the session 1 test
    # scene, 450-600 for chapter 2. Hardcoded, it flagged conformant runs as
    # off-target: a false defect, the kind that sends one hardening a healthy
    # section.
    target = argv[1] if len(argv) > 1 else "400-600"
    target_min, target_max = (int(x) for x in target.split("-"))
    # Chapter number: enables the SCOPED interdicts (notes §3 and §4). Without
    # it the grid cannot know that « la tierce » is legitimate at chapter 9 and
    # forbidden at 2; an interdict unaware of its scope is useless or wrong.
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
        "Généré par `factory eval grid`. **Ne pas éditer les lignes "
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
    # Several candidate keys per line: runs from different sessions do not
    # write the same frontmatter, and a grid knowing only one shows « ? » over
    # data that exists.
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

    # --- L1-L4 extensions of the chapter 2 calibration protocol --------------
    out += ["", "## Protocole ch. 2 — contrôles L1-L4 (AUTO)", "", header, sep]

    out.append(line("Entrées de journal détectées",
                     [str(res[n]["entrees"]) for n in names]))
    # §1: the normalised header is the landmark shared by the L3 count, the
    # grid and the audio switch (`pipeline.assembly`). A malformed header breaks
    # the stage, not just the grid.
    headers = {n: ENTRY_HEADER.findall(
        strip_frontmatter(Path(p).read_text(encoding="utf-8")))
        for n, p in available}
    out.append(line(
        "En-têtes au format normalisé (« Jour N. Météo. »)",
        [f"{'✓' if headers[n] else '✗'} ({len(headers[n])})" for n in names]))

    # CONSECUTIVE dates, no duplicates. The chapter goal requires it, and a
    # notebook whose entries repeat or go backwards is no notebook. Seen at BC:
    # eight headers for three entries, one repeated five times; a header count
    # alone would have missed it.
    def _dates(n: str) -> str:
        days = [int(j) for _, j in headers[n]]
        if not days:
            return "—"
        # TWO ENTRIES THE SAME DAY are legitimate: chapter 7's structure (the
        # afternoon and the night of the anniversary), and the audio switch sits
        # precisely at the second header (ADR-0018). `consistent_headers` already
        # knew the rule; this line still flagged the imposed structure as a
        # defect.
        #
        # What stays faulty: a date going BACKWARDS, or a jump of more than one
        # day between two entries of different dates.
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

    # L1: zero tolerated. Detection is a capital-letter heuristic: occurrences
    # are quoted in the appendix so the reading decides.
    out.append(line(
        "L1 · Noms propres (zéro toléré)",
        [f"{'✓' if not res[n]['l1_noms_propres'] else '✗'} "
         f"({len(res[n]['l1_noms_propres'])})" for n in names]))

    # L2: without RAG a leak is a SHEET/INTERDICTS failure: no retrieval context
    # can bear the responsibility.
    out.append(line(
        "L2 · Fuite lexicale — champ de la mort",
        [f"{'✓' if not res[n]['l2_fuite'] else '✗'} "
         f"({len(res[n]['l2_fuite'])})" for n in names]))
    out.append(line(
        "L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante",
        [f"{'—' if not res[n]['l2_fuite_ambigue'] else '⚠'} "
         f"({len(res[n]['l2_fuite_ambigue'])})" for n in names]))

    # L3: exactly one accumulation PER ENTRY (D1), at the thresholds sheet v3
    # states (60 words, 6 commas), not those of session 1.
    def _l3(n: str) -> str:
        per_entry = res[n]["l3_par_entree"]
        count = [len(e) for e in per_entry]
        ok = count and all(c == 1 for c in count)
        recop = sum(len(e) for e in res[n]["l3_recopies"])
        mark = "✓" if ok else "✗"
        detail = "/".join(str(c) for c in count) or "0"
        return f"{mark} ({detail})" + (f" ⛔{recop} recopie(s)" if recop else "")

    # L3 EXEMPT when the table puts the chapter off scale: chapter 7 does not
    # require an accumulation, it allows one. Showing « ✗ (0) » for a check not
    # required is an impossible green read as a defect; draw 6 carried one.
    l3_exempt = bool(constraints
                      and "hors échelle" in (constraints.get("verdict") or ""))
    out.append(line(
        f"L3 · Accumulation par entrée (≥{L3_WORDS} mots, ≥{L3_COMMAS} virg.)"
        + (" — *non exigée à ce chapitre*" if l3_exempt else ""),
        ["— non exigée" if l3_exempt else _l3(n) for n in names]))

    # L4: the drift is the only permitted use of « … ». Two ways to fail: too
    # many occurrences, or one far from the departure's field.
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
        # Zero occurrences pass L4 as the protocol states it (only excess and
        # off-field fail) yet fail M1, which requires at least one. Say it here:
        # a lone tick would read as « tenu ».
        if total == 0:
            return "✓ (0) — mais aucun glissement, échec M1"
        return f"✓ ({total})"

    out.append(line("L4 · Points de suspension = glissement seul",
                     [_l4(n) for n in names]))

    # --- Interdicts SCOPED per chapter (notes §3 and §4) ---------------------
    if constraints:
        # `strip_frontmatter` is MANDATORY here: a run's frontmatter copies the
        # brief, which NAMES the reserved terms to forbid them. Without the cut
        # every conformant run showed three violations: the grid penalised the
        # brief, not the text.
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
        # MATERIAL INTERDICTS: nemo's generic decor, a FLAG over the written
        # text. Blocking inside `accumulate` (the validator retries), a flag
        # here: automating a check and making it blocking are two distinct
        # decisions, and a run must not fail over a furniture word while mass
        # and gestures pass. The family is named so the reading knows what to
        # look for.
        out.append(line(
            "⚑ Interdits matériels *(drapeau — décor hors du monde)*",
            [(lambda fam: f"{'—' if not fam else '⚑'} "
                          f"({', '.join(sorted(fam)) or '0'})")(
                {x.split(" : ")[0] for x in scope[n]["materiels"]})
             for n in names]))

    # --- Session 5: the five detectors, wired at last ------------------------
    #
    # All existed in the lint and none reached the grid: computed, then thrown
    # away. That is how « Demain est un autre jour » passed without a cross in
    # B′3: the instrument was unplugged, not holed. Phantom lint is doctrine 5.
    out += ["", "## Sessions 5-6 — voix, formulaire et décor (AUTO)", "",
            header, sep]
    for key, lib in [
        ("attracteurs", "Attracteurs *(familles : folie, demain qui résout, "
                        "bouée/océan)*"),
        ("meta_termes", "Méta-termes en sortie (couperet, squelette, beat…)"),
        ("formulaire", "Formulaire par paraphrase (« … est le suivant : »)"),
        # Session 6: instances are no longer served to the model (the *Interdits*
        # section keeps only the categories), so they are checked here. Without
        # this line, closing « perplexe » at the service would have made it
        # invisible instead of absent (ADR-0011).
        ("etats_mentaux", "État mental nommé en apposition *(perplexe, "
                          "songeuse, incrédule…)*"),
        # A trademark dates the text and takes it out of the closed world of the
        # house. L1 already saw it as a proper noun, drowned: named here so it
        # can be removed.
        ("marques", "Marque déposée *(Bluetooth, Frigidaire…)*"),
    ]:
        out.append(line(lib, [f"{'✓' if not res[n].get(key) else '✗'} "
                              f"({len(res[n].get(key) or [])})" for n in names]))

    # FLAGS, not blocking. Arbitration 1B moved the M3 ceiling out as a separate
    # lint, a posed flag. Blocking would fail a whole run over a two-occurrence
    # tic while L3 and M1 pass; automating a check and making it blocking are
    # two distinct decisions. M3 stays the manual line settling the pair.
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

    # THE ACCUMULATION THAT SUMMARISES. Blocking INSIDE the node (the validator
    # retries), so a cross here means the node returned its last attempt
    # anyway: a device defect, not a pen defect. The ratio is shown, not just
    # the verdict: the 0.20 threshold is an arbitration and must stay debatable
    # with the figures in view.
    def _summary(n: str) -> str:
        ratios = res[n].get("accumulations_abstraction") or []
        if not ratios:
            return "— (aucune accumulation)"
        mark = "✓" if all(r <= ACC_ABSTRACT_MAX for r in ratios) else "✗"
        return f"{mark} ({'/'.join(f'{r:.0%}' for r in ratios)})"

    out.append(line(
        "Accumulation d'étapes, non de beats *(≤ 20 % d'items abstraits)*",
        [_summary(n) for n in names]))

    # M1 AS A COMPOSITION CHECK (session 6, §2; ADR-0018). The drift is no longer
    # asked of the model: drawn from the bank, cut and pasted by the code. The
    # question moves from "did the model produce the gesture" to "did the
    # composition keep its promises": presence, uniqueness, L4 conformity. Green
    # by construction, and that is the point; the manual M1 line stays for the
    # oral judgement no counter replaces.
    #
    # Position and non-adjacency are guaranteed in `gestures.assemble` and NOT
    # re-checked here: they exist only as offsets, invisible in the rendered
    # text. Said here rather than letting the line seem to cover them: a grid
    # silent about a criterion reads as a criterion held.
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

    # THE REPEAT, blocking. The code removes the duplicate at assembly (cf.
    # `graph.place_gestures_node`), so a cross here means what it could not
    # remove: a repeat reworded past the threshold, or a sentence reused in an
    # otherwise different paragraph. What the CODE composes is excluded from
    # both counts: headers, anchor and drifts repeat by function, and counting
    # them would have removed the switch and the gesture.
    out.append(line(
        "Aucun paragraphe redit *(similarité ≥ 50 %, hors artefacts du code)*",
        [(lambda r: f"{'✓' if not r else '✗'} ({len(r)})")(
            res[n].get("paragraphes_redits") or []) for n in names]))
    # The PERSON of the accumulation: blocking inside the node, so a cross here
    # means the last attempt went through anyway.
    out.append(line(
        "Accumulation à la première personne",
        [(lambda r: f"{'✓' if not r else '✗'} ({len(r)})")(
            res[n].get("accumulations_3p") or []) for n in names]))
    # FABRICATED QUOTATIONS, a flag. `quotations_outside_anchor` drops the
    # anchor and the verdict from the count when given them; the grid does not
    # know the run's anchor, so it passes the chapter's.
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
