#!/usr/bin/env python3
"""Indexeur de la bible monde.

Lit les fichiers Markdown de la bible, découpe chaque fiche en chunks
(un chunk par section `## `), génère les embeddings via nomic-embed-text
sur Ollama, et pousse le tout dans ChromaDB.

Idempotent : les IDs de chunks sont déterministes ({id}::{section}),
un re-run met à jour les chunks modifiés et purge les chunks disparus.
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

# --- Firewall ----------------------------------------------------------------
#
# L'Involontaire se lit en deux couches : une vérité de surface, que le modèle
# auteur a le droit de connaître, et une vérité profonde qui ne doit JAMAIS
# l'atteindre. Le cloisonnement n'est pas une précaution de principe : la
# nouvelle ne tient que si le modèle ignore ce que le lecteur ignore.
#
# Trois barrières, du gros grain au fin :
#   1. des répertoires entiers jamais lus (ci-dessous) ;
#   2. dans un fichier mixte, seuls les blocs de couche autorisés ;
#   3. dans un fichier de personnage, seules les sections numérotées.
# Chacune est indépendante — c'est voulu : une barrière qui tombe ne doit pas
# emporter les autres.

# Répertoires et fichiers jamais indexés côté auteur, quel que soit leur contenu.
EXCLUSIONS = (
    "profond/",          # chronologie en partie double, fiches Romane/thérapeute…
    "style-auteur.md",   # servi par sections à la génération, jamais récupéré
)

# Couches admises dans un fichier mixte. `[PROFOND]` n'est jamais lu — pas même
# chargé en mémoire pour être filtré plus tard.
# [GABARIT] et [VALEURS] SORTENT du périmètre servi au lot correctif de la
# session 5 (item 2) : ils portent la langue de production — régime, grade,
# ratio, chaleur — et l'étage B a écrit des formulaires parce qu'on lui servait
# des tableaux. Ils restent dans la fiche, où ils sont la SOURCE du générateur
# `build_etat_narratif.py` ; c'est sa traduction diégétique, en [SURFACE], qui
# est désormais indexée à leur place.
COUCHES_ADMISES = ("SURFACE",)
BLOC_COUCHE = re.compile(r"^###\s*\[([A-ZÉ]+)[^\]]*\]\s*$", re.MULTILINE)

# La même convention à crochets sert AU NIVEAU SECTION : `objets.md` marque
# ainsi `## [RÉSERVÉS — chapitre 7, ne jamais mentionner…]`, qui liste le
# quatuor (photos, playlist, plat, couverts). Ces objets sont précisément ceux
# que la grille linte comme interdits hors du chapitre 7 : les indexer
# reviendrait à pouvoir servir à une génération de chapitre 2 la liste de ce
# qu'elle n'a pas le droit d'écrire, et la session 3 a mesuré qu'un modèle à
# qui l'on montre une matière s'en sert. On réutilise la règle des couches
# plutôt que d'entretenir une liste de titres interdits.
SECTION_COUCHE = re.compile(r"^\s*\[([A-ZÉ]+)[^\]]*\]\s*$")

# Une fiche de personnage annonce ses chunks par une section NUMÉROTÉE
# (« ## 1. Voix »). Les sections non numérotées sont des notes de travail —
# celle de la fiche Judith cite la chronologie firewallée. Règle déterministe :
# elle ne dépend d'aucune liste de titres à maintenir.
SECTION_NUMEROTEE = re.compile(r"^\s*(\d+)\.\s+(.+)$")

# Clés de métadonnées recopiées dans Chroma. LISTE BLANCHE, et non liste noire :
# le frontmatter de `verite-de-surface.md` porte un `depends_on` qui NOMME la
# chronologie firewallée. Une liste noire laisserait passer la prochaine clé
# qu'on ajoutera sans y penser.
METADONNEES_ADMISES = ("doc_id", "type", "layer", "version", "section",
                       "source_file", "nom")

# TRADUCTION DES NOMS À L'INDEXATION (item 8, session 5). Le prénom reste dans
# la bible — c'est du canon — mais il disparaît du contexte de génération : au
# run BC de la session 4, le modèle a ÉCRIT « Judith » dans la prose, alors que
# la règle du roman réserve ce prénom au chapitre 8, où il doit être le premier
# et l'unique nom propre du texte.
#
# L'ordre des règles compte : le LABEL de chunk (`[fiche-judith / Voix]`) est
# servi au modèle au même titre que le corps. Le traduire d'abord évite qu'il
# ne devienne « fiche-la narratrice ».
TRADUCTION_NOMS = (
    (re.compile(r"\bfiche-judith\b", re.IGNORECASE), "fiche-narratrice"),
    (re.compile(r"\bJudith\b"), "la narratrice"),
    (re.compile(r"\bjudith\b"), "la narratrice"),
)


def traduire_noms(texte: str) -> str:
    """Remplace les prénoms canoniques par leur désignation neutre."""
    for motif, remplacement in TRADUCTION_NOMS:
        texte = motif.sub(remplacement, texte)
    return texte

# --- Utilitaires -------------------------------------------------------------

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def slugify(text: str) -> str:
    """`## Voix et expression` -> `voix_et_expression`"""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return text.strip("_")


def split_sections(body: str) -> list[tuple[str, str]]:
    """Découpe le corps Markdown en (titre_de_section, contenu).

    Tout ce qui précède le premier `## ` est rattaché à une section
    `_preambule` (le titre `# Nom` de la fiche, typiquement).
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


def exclu(path: Path) -> bool:
    """Vrai si le fichier ne doit jamais atteindre la collection auteur."""
    relatif = str(path.relative_to(BIBLE_DIR))
    return any(motif in relatif for motif in EXCLUSIONS)


def filtrer_couches(contenu: str) -> str:
    """Ne garde que le CORPS des blocs de couche autorisés.

    Deux détails qui ont l'air cosmétiques et ne le sont pas :

    - la ligne de titre du bloc est retirée avec le reste. `[GABARIT — seul
      chunk mutable : régénéré depuis LA PARTIE DOUBLE entre chaque chapitre]`
      est une consigne adressée à l'humain, et elle nomme un document
      firewallé. L'indexer reviendrait à publier le nom de ce qu'on cache.
    - un fichier SANS marqueur de couche passe intact. Tous les fichiers de
      surface ne sont pas mixtes, et exiger le balisage partout ferait
      disparaître `objets.md` de l'index sans que personne ne s'en aperçoive.
    """
    marques = list(BLOC_COUCHE.finditer(contenu))
    if not marques:
        return contenu

    morceaux = []
    bornes = [m.start() for m in marques] + [len(contenu)]
    # Ce qui précède le premier marqueur appartient à la section, pas à une
    # couche : on le garde (chapeau de section, le cas échéant).
    if marques[0].start() > 0:
        morceaux.append(contenu[: marques[0].start()])
    for marque, fin in zip(marques, bornes[1:]):
        if marque.group(1) in COUCHES_ADMISES:
            morceaux.append(contenu[marque.end():fin])
    return "\n".join(morceaux)


def clean_for_embedding(text: str) -> str:
    """Retire les commentaires HTML (instructions pour l'humain,
    pas pour le retrieval) et compacte les lignes vides."""
    text = HTML_COMMENT.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def embed(client: httpx.Client, texts: list[str]) -> list[list[float]]:
    """Embeddings par lot via l'API Ollama /api/embed."""
    resp = client.post(
        f"{settings.ollama_url}/api/embed",
        json={"model": settings.embed_model, "input": texts},
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"]


def scalar_metadata(meta: dict) -> dict:
    """ChromaDB n'accepte que des métadonnées scalaires :
    les listes (tags, relations) sont sérialisées en CSV.

    Filtre par LISTE BLANCHE avant conversion : le frontmatter est exclu du
    texte indexé, mais il finissait quand même dans l'index par cette porte.
    """
    out = {}
    for key, value in meta.items():
        if key not in METADONNEES_ADMISES:
            continue
        if isinstance(value, list):
            out[key] = ",".join(str(v) for v in value)
        elif isinstance(value, (str, int, float, bool)):
            out[key] = value
        elif value is not None:
            out[key] = str(value)
    return out


# --- Indexation ---------------------------------------------------------------

def index_file(path: Path, ollama: httpx.Client) -> tuple[list[str], list[str], list[dict]]:
    """Retourne (ids, documents, metadatas) pour un fichier de la bible."""
    post = frontmatter.load(path)
    # `doc_id` AVANT `id` : c'est la clé qu'emploient les fiches de
    # L'Involontaire. Sans elle, on retombait sur `slugify(path.stem)`, qui
    # rend `fiche_judith` là où le retrieval demande `fiche-judith` — et
    # `character_context()` serait revenu VIDE, sans erreur, à chaque appel de
    # l'étage B. Un firewall qui ne sert rien a l'air parfaitement étanche.
    doc_id = post.get("doc_id") or post.get("id") or slugify(path.stem)
    doc_meta = scalar_metadata(dict(post.metadata))
    doc_meta["doc_id"] = doc_id
    doc_meta["source_file"] = str(path.relative_to(BIBLE_DIR))

    # Une fiche de personnage n'expose que ses sections numérotées ; les autres
    # sont des notes de travail (celle de la fiche Judith cite la chronologie
    # firewallée). Un fichier sans aucune section numérotée n'est pas une fiche :
    # tout y est indexable, et `verite-de-surface.md` en dépend.
    sections = split_sections(post.content)
    numerotees = [(t, c) for t, c in sections if SECTION_NUMEROTEE.match(t)]
    if numerotees:
        sections = numerotees
    # Une section entière peut porter une couche, comme un sous-bloc.
    sections = [
        (t, c) for t, c in sections
        if not (SECTION_COUCHE.match(t)
                and SECTION_COUCHE.match(t).group(1) not in COUCHES_ADMISES)
    ]

    ids, documents, metadatas = [], [], []
    for title, content in sections:
        content = filtrer_couches(content)
        cleaned = clean_for_embedding(content)
        if title == "_preambule":
            # Ne garder le préambule que s'il contient autre chose
            # que le titre `# Nom` de la fiche (sinon : bruit).
            without_heading = re.sub(r"^#\s+.*$", "", cleaned, flags=re.MULTILINE).strip()
            if not without_heading:
                continue
        if not cleaned:
            continue  # section vide du template, pas encore remplie
        # Le numéro de tête ne fait pas partie de l'identité de la section :
        # `## 1. Voix` donne `voix`, pas `1_voix`. Un id qui porte un rang se
        # casse au premier réordonnancement de la fiche, et le retrieval
        # déterministe demande des noms (`WRITING_SECTIONS`), pas des rangs.
        numero = SECTION_NUMEROTEE.match(title)
        if numero:
            title = numero.group(2).strip()
        section = slugify(title)
        # Préfixer le chunk avec son identité améliore nettement le retrieval :
        # l'embedding "sait" de qui et de quoi il parle.
        # La traduction s'applique au document COMPLET, label compris : le
        # préfixe `[fiche-judith / …]` est servi au modèle comme le reste.
        document = traduire_noms(f"[{doc_id} / {title}]\n{cleaned}")
        ids.append(f"{doc_id}::{section}")
        documents.append(document)
        metadatas.append({**doc_meta, "section": section})
    return ids, documents, metadatas


def main() -> int:
    if not BIBLE_DIR.is_dir():
        print(f"ERREUR : répertoire bible introuvable : {BIBLE_DIR}", file=sys.stderr)
        return 1

    files = sorted(
        p for p in BIBLE_DIR.rglob("*.md")
        if not p.name.startswith("_")  # _template.md et consorts sont ignorés
        and not exclu(p)               # firewall : profond, fiche de style
    )
    if not files:
        print(f"Aucune fiche à indexer dans {BIBLE_DIR} (les _template.md sont ignorés).")
        # On ne s'arrête PAS ici : il faut quand même purger d'éventuels
        # chunks orphelins (cas où l'on vient de supprimer la dernière fiche).

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

    # Purge des chunks orphelins (sections ou fiches supprimées)
    existing = collection.get(include=[])["ids"]
    stale = [i for i in existing if i not in set(all_ids)]
    if stale:
        collection.delete(ids=stale)
        print(f"  - {len(stale)} chunks orphelins purgés")

    print(f"\nIndexation terminée : {len(all_ids)} chunks dans '{settings.author_collection}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
