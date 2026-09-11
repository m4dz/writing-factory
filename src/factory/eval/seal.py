#!/usr/bin/env python3
"""Test d'étanchéité de la collection auteur — session 4, §4 du protocole.

L'étanchéité est une propriété du CONTENU de la collection, pas du routage des
requêtes. Un test qui se contenterait d'interroger `auteur` et de constater
qu'aucun chunk profond n'en sort ne prouverait rien : le profond n'y est pas,
donc il ne peut pas en sortir. Le protocole audite donc ce qui est indexé.

Cinq contrôles :
  1. Inventaire — chaque chunk trace vers le manifeste des sources autorisées.
  2. Lint de contenu — lexique de fuite + marqueurs profonds, zéro match.
  3. Test du splitter — la fiche Judith seule ; aucune ligne [PROFOND] produite.
  4. Témoin positif — un chunk profond INJECTÉ doit remonter, preuve que les
     requêtes ont des dents. Puis retrait, purge, ré-inventaire.
  5. Routage — journalisé pendant les runs (cf. `retrieval.routage`).

Le quatrième est le seul qui puisse faire échouer le test volontairement : sans
lui, un vert ne distingue pas « rien à trouver » de « incapable de trouver ».

Usage : python3 outillage/etancheite.py > rapport-etancheite.md
"""

import re
import sys

from factory.paths import DATA_DIR, REPO_ROOT as RACINE

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


# Ajouts du lot correctif de la session 5, à vérifier dans les chunks SERVIS.
# Les ids, eux, ne sont jamais servis au modèle : la vérification porte sur les
# documents.
#
#  - le PRÉNOM (item 8) : traduit en « la narratrice » à l'indexation. Il reste
#    dans la bible, il ne doit plus exister dans la collection.
#  - les TROIS ANCIENNES INSTANCES (item 9) : les exemples copiables dont la
#    liturgie d'AC et BC était la récitation. Leurs fragments restent légitimes
#    dans `citations-cahier.md` — la vérification porte sur la collection
#    servie, pas sur la bible.
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
    """Espaces normalisés avant toute recherche de marqueur.

    Un marqueur multi-mots coupé par un retour à la ligne échappait à
    `re.escape` : « vérité\nprofonde » ne matche pas « vérité profonde ». Les
    fichiers de bible étant retournés à la main, la coupe peut tomber n'importe
    où — le contrôle était donc juste par chance, pas par construction. Vérifié
    sur les 26 chunks : aucun marqueur n'était masqué, mais rien ne le
    garantissait.
    """
    return re.sub(r"\s+", " ", text)


def dump() -> dict:
    col = retrieval._chroma().get_collection(COLLECTION)
    return col.get(include=["documents", "metadatas"])


def main() -> int:
    MARKERS, MANIFESTO = markers(), manifesto()
    failures: list[str] = []
    out = ["# Rapport d'étanchéité — collection auteur", "",
           "Session 4, §4 du protocole. Cinq contrôles ; tout échec est "
           "bloquant pour l'étage B.", ""]

    # --- 1. Inventaire -------------------------------------------------------
    got = dump()
    ids, docs, metas = got["ids"], got["documents"], got["metadatas"] or []
    out += [f"## 1. Inventaire — {len(ids)} chunks", "",
            "| id | source | statut |", "|---|---|---|"]
    for i, mt in zip(ids, metas):
        src = (mt or {}).get("source_file", "?")
        ok = src in MANIFESTO
        if not ok:
            failures.append(f"inventaire : `{i}` vient de `{src}`, hors manifeste")
        out.append(f"| `{i}` | `{src}` | {'✓' if ok else '⛔ HORS MANIFESTE'} |")

    # Clés de métadonnées : une clé imprévue est une porte ouverte.
    keys = sorted({k for mt in metas for k in (mt or {})})
    out += ["", f"Clés de métadonnées présentes : {', '.join(f'`{c}`' for c in keys)}", ""]

    # --- 2. Lint de contenu --------------------------------------------------
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

    # --- 3. Test du splitter -------------------------------------------------
    out += ["## 3. Test du splitter — la fiche Judith seule", ""]
    raw = SHEET_JUDITH.read_text(encoding="utf-8")
    deep_lines = set()
    for block in re.findall(r"^### \[PROFOND\].*?(?=^### |^## |\Z)", raw,
                           re.MULTILINE | re.DOTALL):
        for line in block.splitlines()[1:]:
            if len(line.strip()) > 40:
                deep_lines.add(line.strip())
    # Filtrage par SOURCE et non par préfixe d'id : le préfixe dépend du
    # doc_id, et une divergence de doc_id (constatée : `fiche_judith` au lieu
    # de `fiche-judith`) rendait ce contrôle VIDE — donc vert sans rien
    # vérifier. Un test qui passe sur un ensemble vide est pire qu'absent.
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

    # --- 4. Témoin positif ---------------------------------------------------
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

    # Retrait, purge, ré-inventaire.
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

    # --- 5. Routage ----------------------------------------------------------
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
