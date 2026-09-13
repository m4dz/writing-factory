"""Read ``chapters/NN-slug/spec.yaml`` into a ``ChapterSpec``.

The spec file holds what used to be constants in code: structure, calendar,
caps, criterion names, assembly. It POINTS at the author's brief files for
the text they already carry, so a brief keeps one truth:

- ``brief: {file, section}`` — the served brief is the blockquote of that
  section of the brief file (fabrication notes stripped, no bible file name);
  ``brief: "..."`` serves the literal.
- ``plan: entries-of-brief`` — one beat per entry, cut from the served brief
  at its ``**Entrée N`` headings.
- entry ``source: <file>`` — trajectory, material, drift passage and beat
  instructions read from the entry brief's sections (``## 1. Intention``,
  ``## 2. Trajectoire``, ``## 3. Matière``, ``## 4. Glissement``, ``## 7.``
  beats); literal fields in the spec win.
- entry ``movement: {entry: N}`` or chapter ``movement: table`` — the single
  row of the deep movement table for this chapter (and entry). The file is
  deep and is never served; only its row is.

Validation is the anti-leak discipline of the former chapter module: served
text names no bible file, a bank approach passes its own validator, beat
instructions and beat caps match one to one.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from factory import paths
from factory.chapter_spec.model import (BeatSpec, BestOf, Calendar, ChapterSpec, Defaults,
                                        Drift, DriftBank, EntrySpec)
from factory.eval.lint import MACHINERY, META_TERMS

MOVEMENT_TABLE = paths.BIBLE_DIR / "profond" / "mouvements-chapitres.md"


class ChapterSpecError(ValueError):
    """The spec file is missing, malformed or leaks what it must not."""


# --- discovery ----------------------------------------------------------------

def chapter_dirs(root: Path | None = None) -> dict[int, Path]:
    """``{number: directory}`` for every ``chapters/NN-slug/spec.yaml``."""
    root = root or paths.CHAPTERS_DIR
    out: dict[int, Path] = {}
    if not root.is_dir():
        return out
    for d in sorted(root.iterdir()):
        m = re.match(r"^(\d{2})-", d.name)
        if d.is_dir() and m and (d / "spec.yaml").is_file():
            out[int(m.group(1))] = d
    return out


def load_chapter(chapter: int, root: Path | None = None) -> ChapterSpec:
    dirs = chapter_dirs(root)
    if chapter not in dirs:
        raise ChapterSpecError(
            f"chapitre {chapter} : aucune spécification "
            f"(attendu {(root or paths.CHAPTERS_DIR) / f'{chapter:02d}-<slug>' / 'spec.yaml'})")
    return load_spec(dirs[chapter] / "spec.yaml")


# --- served text ----------------------------------------------------------------

_FABRICATION_NOTE = re.compile(r",?\s*pré-écrite selon\s*`[^`]+`\s*§?\d*\s*:")
_FILE_REFERENCE = re.compile(r"\s*\(?\s*(?:cf\.|voir)\s*`?[\w-]+\.md`?[^)\n]*\)?")
_MD_NAME = re.compile(r"`?\b[\w-]+\.md\b`?")


def strip_fabrication_notes(text: str) -> str:
    """Drop the notes that name a bible file. The note stays useful in the
    brief; it never reaches the model."""
    text = _FABRICATION_NOTE.sub(" :", text)
    return _FILE_REFERENCE.sub("", text)


def assert_no_file_names(text: str, what: str) -> None:
    leaks = _MD_NAME.findall(text)
    if leaks:
        raise ChapterSpecError(f"{what} nomme des fichiers de bible : {leaks} "
                               "— le modèle auteur ne doit pas savoir qu'ils existent")


def workshop_terms(text: str) -> list[str]:
    return sorted({m.group(0).lower() for m in META_TERMS.finditer(text)}
                  | {m.group(0).lower() for m in MACHINERY.finditer(text)})


def blockquote_section(text: str, title: str) -> str:
    """The ``> `` lines of the section opened by ``title``, up to the next ``## ``."""
    if title not in text:
        raise ChapterSpecError(f"section « {title} » introuvable dans le brief")
    body = text.split(title, 1)[1]
    body = re.split(r"^## ", body, maxsplit=1, flags=re.MULTILINE)[0]
    lines = [l.lstrip("> ").rstrip() for l in body.splitlines() if l.startswith(">")]
    return "\n".join(l for l in lines if l).strip()


def plan_from_brief(brief: str) -> list[str]:
    """One beat per entry, cut at the brief's own ``**Entrée N`` headings; the
    shared tail (material, progression, fall, interdicts) goes to every entry."""
    parts = re.split(r"(?=\*\*Entrée \d)", brief)
    if len(parts) < 2:
        return []
    common = parts[0].strip()
    entries, queue = [], ""
    for block in parts[1:]:
        m = re.search(r"\n\*\*(?:Matériau|Progression|Chute|Interdits)", block)
        if m:
            queue = block[m.start():].strip()
            block = block[:m.start()]
        entries.append(block.strip())
    return [f"{common}\n\n{e}\n\n{queue}".strip() for e in entries]


def movement_row(chapter: int, entry: int | None = None,
                 table: Path = MOVEMENT_TABLE) -> str:
    """The movement of ONE chapter (and entry) — the row, never the file."""
    if not table.is_file():
        return ""
    target = f"{chapter} — entrée {entry}" if entry else str(chapter)
    for line in table.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 2 and cells[1] == target:
            return cells[2]
    return ""


def read_entry_brief(path: Path) -> dict:
    """The sections of an entry brief written under the movement method."""
    txt = path.read_text(encoding="utf-8")

    def section(title: str, next_one: str) -> str:
        if title not in txt:
            return ""
        return txt.split(title, 1)[1].split(next_one, 1)[0].strip()

    def bullets(block: str) -> list[str]:
        return [l.lstrip("- ").strip() for l in block.splitlines()
                if l.strip().startswith("-")]

    drift = section("## 4. Glissement", "## 5.")
    drift_text = next((l.lstrip("> ").strip() for l in drift.splitlines()
                       if l.strip().startswith(">")), "")
    position = next((l.split(":", 1)[1].strip() for l in drift.splitlines()
                     if l.startswith("Position")), "")

    def beats() -> list[str]:
        if "## 7." not in txt:
            return []
        seg7 = txt.split("## 7.", 1)[1]
        out = []
        heads = list(re.finditer(r"^### Beat \w+", seg7, re.MULTILINE))
        for i, h in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(seg7)
            lines = [l for l in seg7[h.start():end].strip().splitlines() if l.strip()]
            out.append(" ".join(lines[1:]).strip() if len(lines) > 1 else "")
        return out

    return {
        "intention": section("## 1. Intention", "## 2."),
        "trajectory": bullets(section("## 2. Trajectoire", "## 3.")),
        "material": bullets(section("## 3. Matière disponible", "## 4.")),
        "drift": Drift(drift_text, position) if drift_text else None,
        "beats": beats(),
    }


# --- the spec file ----------------------------------------------------------------

def _pair(value) -> tuple[int, int] | None:
    if value is None:
        return None
    if not (isinstance(value, (list, tuple)) and len(value) == 2):
        raise ChapterSpecError(f"fourchette attendue [min, max], reçu {value!r}")
    return int(value[0]), int(value[1])


def _entry(raw: dict, spec_dir: Path, chapter: int) -> EntrySpec:
    source = read_entry_brief(spec_dir / raw["source"]) if raw.get("source") else {}
    movement = raw.get("movement", "")
    if isinstance(movement, dict):
        movement = movement_row(chapter, movement.get("entry"))
    elif movement == "table":
        movement = movement_row(chapter)
    caps = raw.get("beats") or []
    instructions = source.get("beats") or []
    if caps and instructions and len(caps) != len(instructions):
        raise ChapterSpecError(f"{len(caps)} bornes de beats pour {len(instructions)} "
                               f"libellés dans {raw.get('source')}")
    beats = tuple(
        BeatSpec(str(c["name"]), int(c["num_predict"]), int(c["sentences_max"]),
                 str(c.get("instruction") or (instructions[i] if i < len(instructions) else "")))
        for i, c in enumerate(caps))
    strategy = raw.get("strategy")
    if strategy not in (None, "single", "segments", "beats"):
        raise ChapterSpecError(f"stratégie inconnue : {strategy!r}")
    if strategy == "beats" and not beats:
        raise ChapterSpecError("stratégie beats sans liste de beats")
    bo = raw.get("best_of")
    best_of = None
    if bo:
        if isinstance(bo, int):
            bo = {"n": bo}
        best_of = BestOf(int(bo["n"]), str(bo.get("criterion") or ""),
                         tuple(bo.get("names") or ()), tuple(bo.get("drift") or ()))
    drift = raw.get("drift")
    drift = (Drift(str(drift["text"]), str(drift.get("position") or "")) if drift
             else source.get("drift"))
    for text, what in ((raw.get("vetos") or "", "les vétos servis"),
                       (movement, "la ligne de mouvement")):
        assert_no_file_names(text, what)
    return EntrySpec(
        weekday=raw.get("weekday"), number=raw.get("number"), weather=raw.get("weather"),
        words=_pair(raw.get("words")), sentences_max=raw.get("sentences_max"),
        citation=raw.get("citation"), gestures=bool(raw.get("gestures", True)),
        strategy=strategy, beats=beats, best_of=best_of, movement=movement,
        trajectory=tuple(raw.get("trajectory") or source.get("trajectory") or ()),
        material=tuple(raw.get("material") or source.get("material") or ()),
        vetos=str(raw.get("vetos") or ""), form=dict(raw.get("form") or {}),
        fall=str(raw.get("fall") or ""), drift=drift,
    )


def load_spec(path: Path) -> ChapterSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    spec_dir = path.parent
    for key in ("chapter", "slug", "narrator"):
        if key not in raw:
            raise ChapterSpecError(f"{path} : champ « {key} » manquant")
    chapter = int(raw["chapter"])
    narrator = raw["narrator"]
    narrator = tuple([narrator] if isinstance(narrator, str) else narrator)

    brief_field = raw.get("brief") or ""
    terms: list[str] = []
    if isinstance(brief_field, dict):
        text = (spec_dir / brief_field["file"]).read_text(encoding="utf-8")
        brief = strip_fabrication_notes(blockquote_section(text, brief_field["section"]))
        terms = workshop_terms(brief)     # the owner's brief: reported, never rewritten
    else:
        brief = str(brief_field)
        leaks = workshop_terms(brief)
        if leaks:
            raise ChapterSpecError(f"le brief sert des termes d'atelier que le lint "
                                   f"bannit en sortie : {leaks}")
    assert_no_file_names(brief, "le brief servi")
    entry_brief = str(raw.get("entry_brief") or "")
    if entry_brief:
        leaks = workshop_terms(entry_brief)
        if leaks:
            raise ChapterSpecError(f"le brief d'entrée sert des termes d'atelier : {leaks}")
        assert_no_file_names(entry_brief, "le brief d'entrée")

    plan = raw.get("plan")
    imposed = tuple(plan_from_brief(brief)) if plan == "entries-of-brief" else ()
    entries = tuple(_entry(e, spec_dir, chapter) for e in (raw.get("entries") or []))
    entry_count = int(raw.get("entry_count") or len(entries) or 1)
    if entries and len(entries) != entry_count:
        raise ChapterSpecError(f"{len(entries)} entrées décrites pour entry_count={entry_count}")
    if imposed and len(imposed) != entry_count:
        raise ChapterSpecError(f"le brief découpe {len(imposed)} entrées, la spec en "
                               f"annonce {entry_count}")

    cal = raw.get("calendar") or {}
    bank = raw.get("drift_bank") or {}
    drift_bank = DriftBank(tuple(bank.get("approaches") or ()), tuple(bank.get("facts") or ()))
    from factory.pipeline.gestures import approach_valid
    for a in drift_bank.approaches:
        ok, reason = approach_valid(a)
        if not ok:
            raise ChapterSpecError(f"banque du chapitre {chapter} : approche refusée par "
                                   f"son propre validateur — « {a} » ({reason})")
    dflt = raw.get("defaults") or {}
    return ChapterSpec(
        chapter=chapter, slug=str(raw["slug"]), narrator=narrator, brief=brief,
        entry_count=entry_count,
        calendar=Calendar(str(cal.get("weekday", "Mardi")), int(cal.get("number", 12)),
                          str(cal.get("weather", ""))),
        verdict=str(raw.get("verdict") or ""), active_objects=str(raw.get("active_objects") or ""),
        prefix=str(raw.get("prefix") or ""), stations=tuple(raw.get("stations") or ()),
        accumulation_fall=str(raw.get("accumulation_fall") or ""), drift_bank=drift_bank,
        assembly=dict(raw.get("assembly") or {}),
        defaults=Defaults(bool(dflt.get("rag", True)), bool(dflt.get("micro_nodes", True)),
                          bool(dflt.get("segments", True))),
        entries=entries, imposed_plan=imposed, entry_brief=entry_brief,
        workshop_terms=tuple(terms),
    )
