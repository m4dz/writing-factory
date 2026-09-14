"""The narrative state of chapter N: what chapter N-1 left, told in the
language of the world, from the author's pilot table.

The table (`bible/profond/chronologie-partie-double.md`) is the source; the
state is a GENERATED artifact, one file per chapter under
`bible/generated/narrative-state/ch-NN.md`, indexed by the indexer and by the
`narrative_state` node with the chunk id
`judith::etat_narratif_courant::chNN` and the metadata `chapter: N`.
Retrieval serves the chunk of the chapter being written and falls back to
the sheet's section 7.

The deep column of the table (the real event) is never read: the state says
what she noticed, concluded and decided — never what happened. The chunk
describes the moment she OPENS chapter N, so it is derived from row N-1; a
state written from row N would hand her the end of a chapter not yet written.
"""

from __future__ import annotations

import re
from pathlib import Path

from factory.settings import settings

TABLE_FILE = "profond/chronologie-partie-double.md"
SHEET_FILE = "fiche-judith.md"
NARRATOR_DOC_ID = "judith"

# Chapter 1 has no eve: nothing to tell, only the setup in place.
OPENING = (
    "Le dispositif est installé depuis peu : le cahier du soir, le manuscrit "
    "qui tarde, le carnet pour garder la main. Elle relit chaque soir l'entrée "
    "de la veille et la commente. Rien n'a encore cloché."
)


def read_table(table: Path | None = None) -> dict[int, dict]:
    """Rows of the pilot table by chapter number. The deep column is not read."""
    table = table or settings.bible_dir / TABLE_FILE
    lines: dict[int, dict] = {}
    if not table.is_file():
        return lines
    for line in table.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 12 and cells[1].isdigit():
            lines[int(cells[1])] = {
                "verdict": cells[5], "marche": cells[6], "objets": cells[10],
            }
    return lines


def read_anchors(sheet: Path | None = None) -> dict[int, str]:
    """Continuity anchors, from the `[VALEURS]` blocks of the narrator sheet:
    the PERCEIVED side of the divergence, the only one she may be served."""
    sheet = sheet or settings.bible_dir / SHEET_FILE
    anchors: dict[int, str] = {}
    if not sheet.is_file():
        return anchors
    for block in re.finditer(
            r"### \[VALEURS — chapitre (\d+).*?\](.*?)(?=^### |^## |\Z)",
            sheet.read_text(encoding="utf-8"), re.MULTILINE | re.DOTALL):
        m = re.search(r"Ancre\s*:\s*([^.]*(?:\.[^.]*?)??)(?=\s*(?:Interdits|$))",
                      block.group(2), re.DOTALL)
        if m:
            anchors[int(block.group(1))] = " ".join(m.group(1).split()).rstrip(" .;")
    return anchors


def narrate(previous: dict | None) -> str:
    """One table row → a few sentences in the language of the world. No
    pilot term survives (régime, grade, ratio, chaleur): only what she
    noticed, concluded and decided."""
    if previous is None:
        return OPENING

    verdict = previous["verdict"]
    sentences: list[str] = []

    anchor = (previous.get("ancre") or "").strip()
    if anchor:
        sentences.append(anchor[0].upper() + anchor[1:] + ".")

    def already_said(what: str) -> bool:
        return bool(what) and what.lower() in anchor.lower()

    core = "" if verdict.startswith("aucun") else re.split(r"\s*\(", verdict)[0].strip()
    if verdict.startswith("aucun"):
        if not anchor:
            sentences.append("Elle n'a rien relevé d'anormal.")
    elif not already_said(core):
        sentences.append(f"Verdict rendu : {core}, la faute à elle.")

    pace = previous.get("marche", "").strip()
    if pace and pace not in ("—", "aucune"):
        first = re.split(r"\s*(?:→|,)\s*", pace)[0].strip()
        if not already_said(first):
            sentences.append(f"L'explication qu'elle s'est donnée : {first}.")

    if core and not any(m in anchor.lower()
                         for m in ("résolution", "résolu", "pointer")):
        sentences.append("Elle a résolu de pointer plus précisément.")

    objects = previous.get("objets", "").split(";")[0].strip()
    if objects:
        sentences.append(f"Ce qu'elle a sous la main, ces jours-ci : {objects}.")

    return " ".join(sentences)


def state_text(chapter: int) -> str:
    """The narrative state at the opening of `chapter`, from row chapter-1."""
    if chapter <= 1:
        return narrate(None)
    table, anchors = read_table(), read_anchors()
    previous = table.get(chapter - 1)
    if previous is None:
        raise LookupError(f"aucune ligne pour le chapitre {chapter - 1} dans la table de pilotage")
    return narrate({**previous, "ancre": anchors.get(chapter - 1, "")})


def state_dir() -> Path:
    return settings.generated_dir / "narrative-state"


def state_path(chapter: int) -> Path:
    return state_dir() / f"ch-{chapter:02d}.md"


def render_state_file(chapter: int, text: str) -> str:
    return (
        "---\n"
        f"doc_id: {NARRATOR_DOC_ID}\n"
        "type: character\n"
        f"chapter: {chapter}\n"
        "layer: SURFACE\n"
        "---\n\n"
        f"# État narratif — chapitre {chapter}\n\n"
        "## 7. État narratif courant\n\n"
        "<!-- GÉNÉRÉ par le nœud narrative_state — ne pas éditer à la main : la "
        "table de pilotage est la source. -->\n\n"
        f"{text}\n"
    )


def write_state_file(chapter: int) -> tuple[Path, bool]:
    """Write `ch-NN.md`; idempotent (returns whether the file changed)."""
    content = render_state_file(chapter, state_text(chapter))
    path = state_path(chapter)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return path, False
    path.write_text(content, encoding="utf-8")
    return path, True
