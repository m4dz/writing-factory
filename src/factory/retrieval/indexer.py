#!/usr/bin/env python3
"""Indexer of the world bible.

Reads the bible's Markdown files, splits each sheet into chunks (one per
`## ` section), embeds them with nomic-embed-text through Ollama and pushes
everything into ChromaDB.

Idempotent (ADR-0007): chunk ids are deterministic ({id}::{section}); a
re-run updates changed chunks and purges vanished ones.
"""

import re
import sys
import unicodedata
from pathlib import Path

import frontmatter
import httpx
import chromadb

from factory.settings import settings

# --- Configuration : `factory.settings` --------------------------------------
# The bible root is bound at import so a test can point the indexer at a
# fixture tree; everything else is read from `settings` at call time.
BIBLE_DIR = settings.bible_dir

# --- Firewall (ADR-0017) -----------------------------------------------------
#
# L'Involontaire reads in two layers: a surface truth the author model may
# know, and a deep truth it must NEVER reach. Three independent barriers,
# coarse to fine: whole directories never read (below), allowed layer blocks
# only in a mixed file, numbered sections only in a character sheet. One
# barrier falling must not take the others down.

# Directories and files never indexed for the author, whatever they contain.
EXCLUSIONS = (
    "profond/",          # double-entry chronology, Romane/therapist sheets…
    "style-auteur.md",   # served by section at generation, never retrieved
)

# Layers admitted in a mixed file. `[PROFOND]` is never read, not even loaded
# to be filtered later.
# [GABARIT] and [VALEURS] LEFT the served perimeter in the session 5 fix batch
# (item 2): they carry production language (régime, grade, ratio, chaleur) and
# stage B wrote forms because it was served tables. They stay in the sheet as
# the SOURCE of `factory.chapter_spec.narrative_state`, whose diegetic
# translation, in [SURFACE], is indexed in their place.
ALLOWED_LAYERS = ("SURFACE",)
LAYER_BLOCK = re.compile(r"^###\s*\[([A-ZÉ]+)[^\]]*\]\s*$", re.MULTILINE)

# The same bracket convention works AT SECTION LEVEL: `objets.md` marks
# `## [RÉSERVÉS — chapitre 7, ne jamais mentionner…]`, which lists the quartet
# (photos, playlist, dish, cutlery). Those are exactly the objects the grid
# lints as forbidden outside chapter 7: indexing them could serve a chapter 2
# generation the list of what it may not write, and session 3 measured that a
# model shown matter uses it. Reusing the layer rule beats maintaining a list
# of forbidden titles.
LAYER_SECTION = re.compile(r"^\s*\[([A-ZÉ]+)[^\]]*\]\s*$")

# A character sheet announces its chunks with a NUMBERED section
# (« ## 1. Voix »). Unnumbered sections are working notes: Judith's cites the
# firewalled chronology. Deterministic rule, no title list to maintain.
NUMBERED_SECTION = re.compile(r"^\s*(\d+)\.\s+(.+)$")

# Metadata keys copied into Chroma. A WHITELIST, not a blacklist: the
# frontmatter of `verite-de-surface.md` carries a `depends_on` that NAMES the
# firewalled chronology. A blacklist would let the next thoughtlessly added
# key through.
ALLOWED_METADATA = ("doc_id", "type", "layer", "version", "section",
                       "source_file", "nom", "chapter")

# NAME TRANSLATION AT INDEX TIME (session 5, item 8; ADR-0017). The first
# name stays in the bible, it is canon, but leaves the generation context: in
# run BC of session 4 the model WROTE « Judith » in the prose, while the novel
# reserves that name for chapter 8, where it must be the first and only proper
# noun of the text.
#
# Rule order matters: the chunk LABEL (`[fiche-judith / Voix]`) is served to
# the model like the body. Translating it first keeps it from becoming
# « fiche-la narratrice ».
NAME_TRANSLATION = (
    (re.compile(r"\bfiche-judith\b", re.IGNORECASE), "fiche-narratrice"),
    (re.compile(r"\bJudith\b"), "la narratrice"),
    (re.compile(r"\bjudith\b"), "la narratrice"),
)


def translate_names(text: str) -> str:
    """Replace canonical first names with their neutral designation."""
    for pattern, replacement in NAME_TRANSLATION:
        text = pattern.sub(replacement, text)
    return text

# --- Utilities ---------------------------------------------------------------

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def slugify(text: str) -> str:
    """`## Voix et expression` -> `voix_et_expression`"""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return text.strip("_")


def split_sections(body: str) -> list[tuple[str, str]]:
    """Split a Markdown body into (section_title, content).

    Everything before the first `## ` goes to a `_preambule` section
    (typically the sheet's `# Nom` title).
    """
    sections: list[tuple[str, str]] = []
    current_title = "_preambule"
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_lines and "".join(current_lines).strip():
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines and "".join(current_lines).strip():
        sections.append((current_title, "\n".join(current_lines).strip()))
    return sections


def source_label(path: Path) -> str:
    """`source_file` metadata: the path relative to the bible; a generated file
    kept elsewhere (`GENERATED_DIR`) is labelled as if under `bible/generated/`,
    which is where the seal manifest expects it."""
    try:
        return str(path.relative_to(BIBLE_DIR))
    except ValueError:
        pass
    try:
        return f"generated/{path.relative_to(settings.generated_dir)}"
    except ValueError:
        return path.name


def excluded(path: Path) -> bool:
    """True when the file must never reach the author collection."""
    relative = str(path.relative_to(BIBLE_DIR))
    return any(pattern in relative for pattern in EXCLUSIONS)


def filter_layers(content: str) -> str:
    """Keep only the BODY of allowed layer blocks.

    Two details that look cosmetic and are not:

    - the block's title line goes with the rest: the `[GABARIT — …]` title is
      addressed to the human and names a firewalled document (the
      double-entry chronology). Indexing it would publish the name of what is
      hidden.
    - a file WITHOUT layer markers passes intact. Not every surface file is
      mixed, and requiring markup everywhere would drop `objets.md` from the
      index with nobody noticing.
    """
    marks = list(LAYER_BLOCK.finditer(content))
    if not marks:
        return content

    pieces = []
    bounds = [m.start() for m in marks] + [len(content)]
    # What precedes the first marker belongs to the section, not to a layer:
    # keep it (a section lead, when there is one).
    if marks[0].start() > 0:
        pieces.append(content[: marks[0].start()])
    for mark, end in zip(marks, bounds[1:]):
        if mark.group(1) in ALLOWED_LAYERS:
            pieces.append(content[mark.end():end])
    return "\n".join(pieces)


def clean_for_embedding(text: str) -> str:
    """Strip HTML comments (instructions for the human, not for retrieval)
    and collapse blank lines."""
    text = HTML_COMMENT.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def embed(client: httpx.Client, texts: list[str]) -> list[list[float]]:
    """Batch embeddings through the Ollama /api/embed endpoint."""
    resp = client.post(
        f"{settings.ollama_url}/api/embed",
        json={"model": settings.embed_model, "input": texts},
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"]


def scalar_metadata(meta: dict) -> dict:
    """ChromaDB accepts scalar metadata only: lists (tags, relations) are
    serialised as CSV.

    WHITELIST filter before conversion: the frontmatter is excluded from the
    indexed text, yet it used to reach the index through this door.
    """
    out = {}
    for key, value in meta.items():
        if key not in ALLOWED_METADATA:
            continue
        if isinstance(value, list):
            out[key] = ",".join(str(v) for v in value)
        elif isinstance(value, (str, int, float, bool)):
            out[key] = value
        elif value is not None:
            out[key] = str(value)
    return out


# --- Indexing -----------------------------------------------------------------

def index_file(path: Path, ollama: httpx.Client) -> tuple[list[str], list[str], list[dict]]:
    """(ids, documents, metadatas) for one bible file."""
    post = frontmatter.load(path)
    # `doc_id` BEFORE `id`: the key the sheets of L'Involontaire use. Without
    # it the fallback was `slugify(path.stem)`, which yields `fiche_judith`
    # where retrieval asks for `fiche-judith`, and `character_context()` came
    # back EMPTY, without error, at every stage B call. A firewall that serves
    # nothing looks perfectly sealed.
    doc_id = post.get("doc_id") or post.get("id") or slugify(path.stem)
    doc_meta = scalar_metadata(dict(post.metadata))
    doc_meta["doc_id"] = doc_id
    doc_meta["source_file"] = source_label(path)
    # A chapter-scoped file (the generated narrative state of chapter N) keeps
    # the sheet's section id and adds `::chNN`: retrieval asks for the chunk of
    # its chapter first and falls back to the sheet's own section.
    chapter = post.get("chapter")
    suffix = f"::ch{int(chapter):02d}" if chapter is not None else ""

    # A character sheet exposes only its numbered sections; the others are
    # working notes (Judith's cites the firewalled chronology). A file with no
    # numbered section is not a sheet: all of it is indexable, and
    # `verite-de-surface.md` relies upon that.
    sections = split_sections(post.content)
    numbered = [(t, c) for t, c in sections if NUMBERED_SECTION.match(t)]
    if numbered:
        sections = numbered
    # A whole section may carry a layer, like a sub-block.
    sections = [
        (t, c) for t, c in sections
        if not (LAYER_SECTION.match(t)
                and LAYER_SECTION.match(t).group(1) not in ALLOWED_LAYERS)
    ]

    ids, documents, metadatas = [], [], []
    for title, content in sections:
        content = filter_layers(content)
        cleaned = clean_for_embedding(content)
        if title == "_preambule":
            # Keep the preamble only when it holds more than the sheet's
            # `# Nom` title (otherwise: noise).
            without_heading = re.sub(r"^#\s+.*$", "", cleaned, flags=re.MULTILINE).strip()
            if not without_heading:
                continue
        if not cleaned:
            continue  # empty template section, not yet filled
        # The leading number is not part of the section's identity: `## 1. Voix`
        # gives `voix`, not `1_voix`. An id carrying a rank breaks at the first
        # reordering of the sheet, and deterministic retrieval asks for names
        # (`WRITING_SECTIONS`), not ranks.
        number = NUMBERED_SECTION.match(title)
        if number:
            title = number.group(2).strip()
        section = slugify(title)
        # Prefixing the chunk with its identity clearly improves retrieval: the
        # embedding "knows" who and what it is about.
        # Translation applies to the WHOLE document, label included: the
        # `[fiche-judith / …]` prefix is served to the model like the rest.
        document = translate_names(f"[{doc_id} / {title}]\n{cleaned}")
        ids.append(f"{doc_id}::{section}{suffix}")
        documents.append(document)
        metadatas.append({**doc_meta, "section": section})
    return ids, documents, metadatas


def main() -> int:
    if not BIBLE_DIR.is_dir():
        print(f"ERREUR : répertoire bible introuvable : {BIBLE_DIR}", file=sys.stderr)
        return 1

    files = sorted(
        p for p in BIBLE_DIR.rglob("*.md")
        if not p.name.startswith("_")  # _template.md and the like are skipped
        and not excluded(p)               # firewall: profond, style sheet
    )
    if not files:
        print(f"Aucune fiche à indexer dans {BIBLE_DIR} (les _template.md sont ignorés).")
        # Do NOT stop here: orphan chunks must still be purged (the last sheet
        # may just have been deleted).

    chroma = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    collection = chroma.get_or_create_collection(
        settings.author_collection, metadata={"hnsw:space": "cosine"}
    )

    all_ids: list[str] = []
    with httpx.Client() as ollama:
        for path in files:
            ids, documents, metadatas = index_file(path, ollama)
            if not ids:
                print(f"  ~ {path.name} : aucune section remplie, ignoré")
                continue
            embeddings = embed(ollama, documents)
            collection.upsert(
                ids=ids, documents=documents,
                metadatas=metadatas, embeddings=embeddings,
            )
            all_ids.extend(ids)
            print(f"  + {path.relative_to(BIBLE_DIR)} : {len(ids)} chunks")

    # Purge orphan chunks (deleted sections or sheets)
    existing = collection.get(include=[])["ids"]
    stale = [i for i in existing if i not in set(all_ids)]
    if stale:
        collection.delete(ids=stale)
        print(f"  - {len(stale)} chunks orphelins purgés")

    print(f"\nIndexation terminée : {len(all_ids)} chunks dans '{settings.author_collection}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
