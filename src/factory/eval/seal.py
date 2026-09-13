#!/usr/bin/env python3
"""Seal test of the author collection (ADR-0017).

Sealing is a property of the collection's CONTENT, not of query routing. A test
that only queried `auteur` and saw no deep chunk come back would prove nothing:
the deep layer is absent, so it cannot come back. The test audits what is
indexed.

Controls:
  1. Inventory: every chunk traces to the manifest of allowed sources.
  2. Content lint: leak lexicon and deep markers, zero match.
  3. Splitter test: the Judith sheet alone; no [PROFOND] line produced.
  4. Positive witness: an INJECTED deep chunk must come back, proof the queries
     have teeth. Then removal, purge, re-inventory.
  5. Routing: journaled during the runs (cf. `retrieval.routing`).
  6. Chapters: no line of `chapters/` in any collection (revamp step 5).

The fourth is the only one able to fail deliberately: without it, a green does
not tell « rien à trouver » from « incapable de trouver » (doctrine 4).

Usage: factory eval seal > report.md
"""

import fnmatch
import re
import sys

from factory.paths import CHAPTERS_DIR, DATA_DIR, REPO_ROOT as RACINE

from factory.retrieval import context as retrieval
from factory.eval.lint import lexical_leak

COLLECTION = "auteur"
SHEET_JUDITH = RACINE / "bible" / "fiche-judith.md"

QUERIES = [
    "qui est Romane",
    "pourquoi est-elle partie",
    "que s'est-il passé il y a un an",
    "qui écrit dans le cahier",
    "que cache la narratrice",
    "la vérité sur le départ",
    "ce que Judith ignore",
    "les entrées que Judith n'a pas écrites",
    "ce qui est arrivé à sa compagne",
    "la véritable explication du phénomène",
]

WITNESS_ID = "TEMOIN::injection-profonde"
WITNESS_TEXT = (
    "Colonne réelle — vérité profonde de la partie double. Ce chunk est un "
    "témoin injecté volontairement par le test d'étanchéité. S'il remonte, "
    "les requêtes témoins fonctionnent ; s'il ne remonte pas, elles sont "
    "aveugles et le vert des autres contrôles ne vaut rien. "
    "Romane est partie il y a un an ; ce que Judith ignore la concerne."
)


# Session 5 corrective batch additions, checked in the SERVED chunks. Ids are
# never served to the model: the check covers the documents.
#
#  - the FIRST NAME (item 8): translated to « la narratrice » at indexing
#    (ADR-0017). It stays in the bible; it must no longer exist in the
#    collection.
#  - the THREE FORMER INSTANCES (item 9): the copyable examples whose recital
#    was the liturgy of AC and BC. Their fragments stay legitimate in
#    `citations-cahier.md`: the check covers the served collection, not the
#    bible.
FORBIDDEN_SESSION_5 = [
    "Judith",
    "Jeudi 7. Beau temps.",
    "Égouttoir : deux assiettes.",
    "Je suis désolée de devoir te laisser",
]


def markers() -> list[str]:
    p = DATA_DIR / "marqueurs-profonds.txt"
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()]


def manifesto() -> list[str]:
    p = DATA_DIR / "manifeste-auteur.txt"
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


def flatten(text: str) -> str:
    """Whitespace normalised before any marker search.

    A multi-word marker cut by a line break escaped `re.escape`:
    « vérité\nprofonde » does not match « vérité profonde ». Bible files are
    wrapped by hand, so the cut can fall anywhere: the check was right by luck,
    not by construction. Checked over the 26 chunks: no marker was masked,
    nothing guaranteed it.
    """
    return re.sub(r"\s+", " ", text)


def chapter_material(root=CHAPTERS_DIR) -> list[str]:
    """Distinctive lines of every chapter file (briefs, specs): the material
    that must be in NO collection. Chapter specs are outside `bible/`, so the
    indexer never reads them; this control proves it instead of presuming it."""
    out: list[str] = []
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if path.suffix not in (".md", ".yaml", ".yml") or not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip().lstrip(">-# ").strip()
            if len(line) > 40 and not line.startswith(("|", "```", "---")):
                out.append(flatten(line))
    return out


def chapter_leaks(documents: list[str], material: list[str] | None = None,
                  metadatas: list[dict | None] | None = None) -> list[str]:
    """The chapter lines found verbatim inside indexed documents.

    Promoted scenes (`type: scene`) are skipped: a promoted chapter carries
    its anchor quotation, which the brief also carries, by construction — the
    owner put it there. Everything else must be free of chapter material."""
    material = chapter_material() if material is None else material
    kept = [d for d, mt in zip(documents, metadatas or [None] * len(documents))
            if (mt or {}).get("type") != "scene"]
    body = flatten(" ".join(kept))
    return [line for line in material if line in body]


def dump() -> dict:
    col = retrieval._chroma().get_collection(COLLECTION)
    return col.get(include=["documents", "metadatas"])


def main(argv: list[str] | None = None) -> int:
    MARKERS, MANIFESTO = markers(), manifesto()
    failures: list[str] = []
    out = ["# Rapport d'étanchéité — collection auteur", "",
           "Session 4, §4 du protocole. Cinq contrôles ; tout échec est "
           "bloquant pour l'étage B.", ""]

    # --- 1. Inventory --------------------------------------------------------
    got = dump()
    ids, docs, metas = got["ids"], got["documents"], got["metadatas"] or []
    out += [f"## 1. Inventaire — {len(ids)} chunks", "",
            "| id | source | statut |", "|---|---|---|"]
    for i, mt in zip(ids, metas):
        src = (mt or {}).get("source_file", "?")
        ok = any(fnmatch.fnmatchcase(src, pattern) for pattern in MANIFESTO)
        if not ok:
            failures.append(f"inventaire : `{i}` vient de `{src}`, hors manifeste")
        out.append(f"| `{i}` | `{src}` | {'✓' if ok else '⛔ HORS MANIFESTE'} |")

    # Metadata keys: an unexpected key is an open door.
    keys = sorted({k for mt in metas for k in (mt or {})})
    out += ["", f"Clés de métadonnées présentes : {', '.join(f'`{c}`' for c in keys)}", ""]

    # --- 2. Content lint -----------------------------------------------------
    out += ["## 2. Lint de contenu — lexique de fuite et marqueurs profonds", ""]
    dirty = 0
    for i, d in zip(ids, docs):
        flat = flatten(d)
        hm = sorted({x for x in MARKERS if re.search(re.escape(x), flat, re.I)})
        hard_ones, _ = lexical_leak(flat)
        s5 = sorted({x for x in FORBIDDEN_SESSION_5
                     if re.search(re.escape(x), flat, re.I)})
        if hm or hard_ones or s5:
            dirty += 1
            failures.append(f"lint : `{i}` → marqueurs {hm} fuite {hard_ones} "
                          f"interdits s5 {s5}")
            out.append(f"- ⛔ `{i}` : marqueurs {hm}, fuite {hard_ones}, "
                       f"interdits session 5 {s5}")
    out += [("- ✓ aucun match sur les "
             f"{len(ids)} chunks — marqueurs profonds, lexique de fuite, "
             "prénom (item 8) et anciennes instances (item 9)")
            if not dirty else "", ""]

    # --- 3. Splitter test ----------------------------------------------------
    out += ["## 3. Test du splitter — la fiche Judith seule", ""]
    raw = SHEET_JUDITH.read_text(encoding="utf-8")
    deep_lines = set()
    for block in re.findall(r"^### \[PROFOND\].*?(?=^### |^## |\Z)", raw,
                           re.MULTILINE | re.DOTALL):
        for line in block.splitlines()[1:]:
            if len(line.strip()) > 40:
                deep_lines.add(line.strip())
    # Filter by SOURCE, not by id prefix: the prefix follows the doc_id, and a
    # doc_id divergence (seen: `fiche_judith` for `fiche-judith`) made this
    # check EMPTY, hence green without checking anything. A test passing over an
    # empty set is worse than none (doctrine 4).
    judith = [d for d, mt in zip(docs, metas)
              if (mt or {}).get("source_file") == "fiche-judith.md"]
    body = flatten(" ".join(judith))
    leaks = [l for l in deep_lines if flatten(l) in body]
    out += [f"- {len(deep_lines)} lignes [PROFOND] significatives dans la fiche",
            f"- {len(judith)} chunks indexés depuis `fiche-judith.md`"]
    if not judith:
        failures.append("splitter : AUCUN chunk de la fiche Judith dans l'index "
                      "— le contrôle porterait sur un ensemble vide")
        out.append("- ⛔ aucun chunk à contrôler : ce vert ne prouverait rien")
    elif leaks:
        failures.append(f"splitter : {len(leaks)} ligne(s) [PROFOND] indexée(s)")
        out.append(f"- ⛔ {len(leaks)} ligne(s) [PROFOND] retrouvée(s) dans l'index")
    else:
        out.append("- ✓ aucune ligne [PROFOND] dans les chunks produits")
    out.append("")

    # --- 4. Positive witness -------------------------------------------------
    out += ["## 4. Témoin positif — le test doit pouvoir échouer", "",
            "Un chunk profond est injecté VOLONTAIREMENT dans `auteur`, puis "
            "les dix requêtes témoins sont rejouées. S'il ne remonte pas, les "
            "requêtes sont aveugles et le vert des contrôles 1 à 3 ne vaut "
            "rien.", ""]
    col = retrieval._chroma().get_collection(COLLECTION)
    col.upsert(ids=[WITNESS_ID], documents=[WITNESS_TEXT],
               metadatas=[{"doc_id": "TEMOIN", "source_file": "TEMOIN"}],
               embeddings=[retrieval.embed(WITNESS_TEXT)])
    touched = 0
    out += ["| requête | témoin remonté ? |", "|---|---|"]
    for q in QUERIES:
        r = col.query(query_embeddings=[retrieval.embed(q)], n_results=3,
                      include=["documents"])
        seen = any(WITNESS_TEXT[:60] in d for d in (r.get("documents") or [[]])[0])
        touched += seen
        out.append(f"| {q} | {'✓ oui' if seen else '— non'} |")
    out.append("")
    if touched == 0:
        failures.append("témoin positif : le chunk injecté n'est remonté sur "
                      "AUCUNE requête — les requêtes témoins sont aveugles")
        out.append("- ⛔ **le témoin n'est jamais remonté** : les requêtes ne "
                   "prouvent rien.")
    else:
        out.append(f"- ✓ témoin remonté sur {touched}/{len(QUERIES)} requêtes — "
                   "les requêtes ont des dents.")

    # Removal, purge, re-inventory.
    col.delete(ids=[WITNESS_ID])
    after = dump()["ids"]
    rest = WITNESS_ID in after
    if rest:
        failures.append("témoin positif : le chunk injecté n'a pas été purgé")
    out += ["",
            f"- Après purge : {len(after)} chunks, témoin présent : "
            f"{'⛔ OUI' if rest else '✓ non'}",
            f"- Inventaire re-vérifié : {'⛔ écart' if len(after) != len(ids) else '✓ identique à l’état initial'}",
            ""]

    # --- 6. Chapters ---------------------------------------------------------
    out += ["## 6. Matériau des chapitres — hors de toute collection", "",
            "`chapters/` (briefs, spécifications) vit hors de `bible/` : l'indexeur "
            "ne le lit jamais. Contrôle : aucune ligne de ces fichiers dans "
            "`auteur` ni dans `sessions`.", ""]
    material = chapter_material()
    all_docs, all_metas = list(docs), list(metas)
    try:
        sessions = retrieval.sessions_collection().get(include=["documents", "metadatas"])
        all_docs += sessions["documents"] or []
        all_metas += sessions.get("metadatas") or [None] * len(sessions["documents"] or [])
    except Exception as exc:                          # noqa: BLE001
        out.append(f"- ⚠ collection `sessions` non lue ({type(exc).__name__})")
    leaked = chapter_leaks(all_docs, material, all_metas)
    if not material:
        failures.append("chapitres : aucun matériau trouvé sous chapters/ — le contrôle "
                        "porterait sur un ensemble vide")
        out.append("- ⛔ aucune ligne de chapitre à contrôler : ce vert ne prouverait rien")
    elif leaked:
        failures.append(f"chapitres : {len(leaked)} ligne(s) de chapters/ indexée(s)")
        out.append(f"- ⛔ {len(leaked)} ligne(s) de `chapters/` retrouvée(s) dans l'index")
    else:
        out.append(f"- ✓ {len(material)} lignes de `chapters/` contrôlées, aucune dans l'index")
    out.append("")

    # --- 5. Routing ----------------------------------------------------------
    out += ["## 5. Assertion de routage", "",
            "Journalisée pendant les runs B par `retrieval.routage()` : une "
            "seule collection tolérée. Le point de passage est unique "
            "(`retrieval._collection`), donc le journal ne peut pas être "
            "incomplet sans que le code le soit aussi.",
            f"- Collections vues pendant ce test : "
            f"{sorted(set(retrieval.routing())) or '(aucune — accès directs)'}",
            ""]

    out += ["## Verdict", ""]
    if failures:
        out.append(f"⛔ **{len(failures)} échec(s)** — l'étage B est bloqué :")
        out += [f"- {e}" for e in failures]
    else:
        out.append("✓ **Étanchéité vérifiée** — inventaire conforme au "
                   "manifeste, aucun marqueur profond ni fuite lexicale, "
                   "splitter propre, requêtes témoins prouvées mordantes.")
    print("\n".join(out))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
