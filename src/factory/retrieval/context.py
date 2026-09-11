#!/usr/bin/env python3
"""Retrieval contextuel dynamique sur la bible (ChromaDB).

Le principe du projet : le contexte n'est PAS statique. À chaque scène on
assemble un prompt système de 2-3k tokens à partir de la vérité stockée hors
du modèle : fiches des personnages présents, lieu, scènes précédentes
pertinentes. Le modèle n'est qu'un lecteur de cette vérité.

Deux stratégies combinées :
  1. DÉTERMINISTE (par id) pour les personnages présents : on connaît le
     patron d'id `{doc_id}::{section}`, donc on va chercher directement les
     chunks qui comptent pour ÉCRIRE un personnage (voix, état courant,
     psychologie) — pas de pari sémantique là où on sait déjà quoi vouloir.
  2. SÉMANTIQUE (top-k) pour l'ambiance : lieu et scènes précédentes
     pertinentes, retrouvés par similarité sur la requête de la scène.
"""

import os
import re

import chromadb


from factory.settings import settings

# Fiche de style, servie PAR SECTIONS et lue sur disque : elle n'est jamais
# indexée (cf. EXCLUSIONS de l'indexeur). Servie entière, elle pèse ~4 200
# tokens sur les 8 192 de la fenêtre et pousse `FRENCH_GUARD` vers la sortie —
# Ollama fait alors glisser la fenêtre et ampute le DÉBUT du prompt, sans une
# erreur. Chemin : `settings.style_path`.

# Ce que chaque nœud reçoit de la fiche. Les « Extraits étalons » ne sont
# servis à AUCUN nœud : la session 3 a mesuré qu'un modèle à qui on montre un
# étalon le recopie caractère pour caractère, dans une scène qui parle d'autre
# chose. Ils restent artefacts d'évaluation.
# *Lexique et registre* rejoint la liste au lot correctif de la session 5. Les
# heures, les quantités exactes, la notation physiologique, les adjectifs rares
# et le registre du départ y vivent — et HUIT RUNS SUR HUIT les ont manqués,
# non pas faute de les avoir écrits dans la fiche, mais faute de les avoir
# SERVIS. Le verdict oral de la session 4 (« la voix nulle part ») porte
# d'abord sur ce trou de liste.
WRITING_STYLE = ("Narration", "Lexique et registre", "Interdits")
REVIEW_STYLE = ("Interdits", "Phrase et rythme")

# La règle épistémique du roman, servie à l'écriture. Elle n'est pas une
# section de la fiche : c'est la ligne qui décide qui a raison quand la mémoire
# et le texte divergent, et tout le fantastique en découle.
EPISTEMIC_LINE = (
    "Le texte fait foi : l'entrée relue a toujours raison contre la mémoire."
)

# Chunks qui comptent pour écrire un personnage, par ordre de priorité.
# On ne charge pas les 7 : histoire/compétences/relations gonflent le prompt
# sans servir la rédaction immédiate d'une entrée. Les slugs suivent les
# sections numérotées de la fiche, dont l'indexeur retire le rang.
WRITING_SECTIONS = ["voix", "etat_narratif_courant", "psychologie"]

# Chunks de MONDE, pour la dérivation des faits (item 3 du lot correctif).
# `derive_facts` lisait les chunks d'écriture, dont l'état narratif — lequel
# portait la table de pilotage. Les « faits » dérivés parlaient donc de verdict
# imposé, de grade et de ratio : du vocabulaire de production, servi ensuite au
# planificateur comme s'il s'agissait du monde. On dérive désormais depuis ce
# qui décrit le monde, pas depuis ce qui pilote sa fabrication.
WORLD_SECTIONS = ["psychologie", "histoire", "relations"]


def world_context(doc_id: str) -> str:
    """Chunks de monde d'un personnage — base des faits invariants."""
    ids = [f"{doc_id}::{s}" for s in WORLD_SECTIONS]
    got = _collection().get(ids=ids, include=["documents"])
    found_item = {i: d for i, d in zip(got["ids"], got["documents"])}
    return "\n\n".join(found_item[i] for i in ids if i in found_item)

# Chunks qui comptent pour INCARNER un personnage (mode acteur). La liste est
# plus large que celle d'écriture, et ce n'est pas une négligence : écrire une
# scène n'exige pas la biographie du personnage, alors qu'un interlocuteur lui
# posera des questions sur son passé et ses proches. Répondre « je ne sais pas »
# à propos de sa propre histoire EST une sortie de personnage.
ACTING_SECTIONS = [
    "voix", "psychologie", "etat_narratif_courant",
    "histoire", "relations", "comportement",
]

# Mémoire de conversation du mode acteur. Collection SÉPARÉE de `bible` : la
# bible est dérivée du Markdown canonique et l'indexeur y purge les chunks
# orphelins, ce qui effacerait une mémoire de session au premier réindexage.
# Le sens du flux reste le même — Markdown d'abord (sessions/), index ensuite.

_client = None

# Journal de ROUTAGE (test d'étanchéité §5). Chaque accès à une collection y
# laisse son nom : à la fin d'un run B, une seule valeur doit y figurer. Un
# firewall qui repose sur « on n'interroge que la bonne collection » n'est une
# garantie que si on peut le PROUVER après coup.
_ROUTING: list[str] = []


def routing() -> list[str]:
    """Collections réellement interrogées depuis le dernier `vider_routage`."""
    return list(_ROUTING)


def clear_routing() -> None:
    _ROUTING.clear()


def _collection(name: str | None = None):
    """Point de passage UNIQUE vers une collection — et donc seul endroit à
    instrumenter. Des appels dispersés à `get_collection` rendraient le
    journal de routage incomplet sans que rien ne le signale."""
    name = name or settings.author_collection
    _ROUTING.append(name)
    return _chroma().get_collection(name)


def _chroma():
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return _client


def embed(text: str) -> list[float]:
    """Embedding d'une requête via nomic-embed-text (même modèle que l'index)."""
    import json
    import urllib.request

    payload = json.dumps({"model": settings.embed_model, "input": [text]}).encode()
    req = urllib.request.Request(
        f"{settings.ollama_url}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    # Timeout large : un premier embed peut attendre le chargement du modèle
    # d'embedding en RAM (surtout si un gros modèle auteur y est déjà chaud).
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())["embeddings"][0]


_STYLE_CACHE: dict[str, str] | None = None


def style_sections(names: tuple[str, ...]) -> str:
    """Rend les sections nommées de la fiche de style, lues sur disque.

    Sur DISQUE et non depuis Chroma : la fiche de style n'est pas de la matière
    narrative qu'on retrouve par similarité, c'est une consigne qu'on sert
    toujours en entier ou pas du tout. La passer par le retrieval reviendrait à
    parier sur un embedding pour obtenir une règle qu'on connaît déjà.
    """
    global _STYLE_CACHE
    if _STYLE_CACHE is None:
        _STYLE_CACHE = {}
        path = str(settings.style_path)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            # Le frontmatter et les commentaires HTML sont des notes d'édition.
            if text.startswith("---"):
                text = text.split("---", 2)[-1]
            text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
            title, body = None, []
            for line in text.splitlines():
                if line.startswith("## "):
                    if title:
                        _STYLE_CACHE[title] = "\n".join(body).strip()
                    title, body = line[3:].strip(), []
                elif title:
                    body.append(line)
            if title:
                _STYLE_CACHE[title] = "\n".join(body).strip()

    blocks = [f"## {n}\n{_without_examples(_STYLE_CACHE[n])}"
             for n in names if _STYLE_CACHE.get(n)]
    return "\n\n".join(blocks)


# Les exemples Écrire / Ne pas écrire sont RETIRÉS DU SERVICE, pas de la fiche :
# la référence reste intacte pour la relecture humaine. Motif : B′2 a écrit
# « perplexe », qui est le contre-exemple VERBATIM de *Lexique et registre*.
# C'est la troisième fois qu'on mesure la même chose — un exemple montré se
# récite, quel que soit le panneau qu'on plante devant (« ne pas écrire »).
# La règle prescriptive, elle, survit : seule l'illustration part.
_SERVED_EXAMPLE = re.compile(
    r"^\s*\*\*(?:Écrire|Ne pas écrire)\s*:?\*\*.*?(?=^\s*[-*]\s|^\s*\*\*|\Z)",
    re.MULTILINE | re.DOTALL)


def _without_examples(section: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", _SERVED_EXAMPLE.sub("", section)).strip()


def character_context(doc_id: str) -> str:
    """Récupère, par id déterministe, les chunks d'écriture d'un personnage.

    Retourne le texte assemblé (déjà préfixé `[doc_id / Titre]` à l'index),
    ou une chaîne vide si le personnage n'est pas encore dans la bible.
    """
    ids = [f"{doc_id}::{section}" for section in WRITING_SECTIONS]
    got = _collection().get(ids=ids, include=["documents"])
    # Chroma renvoie les ids trouvés dans l'ordre demandé ; on filtre les absents.
    found = {i: d for i, d in zip(got["ids"], got["documents"])}
    blocks = [found[i] for i in ids if i in found]
    return "\n\n".join(blocks)


def list_characters() -> list[dict]:
    """Personnages disponibles dans la bible, pour peupler une interface.

    Lecture par MÉTADONNÉE, sans embedding : on veut la liste exhaustive, pas
    les plus proches d'une requête.
    """
    try:
        got = _collection().get(
            where={"type": "character"}, include=["metadatas"]
        )
    except Exception:                      # collection absente : bible non indexée
        return []
    seen_map: dict[str, dict] = {}
    for meta in got.get("metadatas") or []:
        doc_id = (meta or {}).get("doc_id")
        if doc_id and doc_id not in seen_map:
            seen_map[doc_id] = {
                "id": doc_id,
                "rank": (meta or {}).get("rank", ""),
                "nom": doc_id.split("-")[0].capitalize(),
            }
    return sorted(seen_map.values(), key=lambda c: c["id"])


def acting_context(doc_id: str) -> str:
    """Chunks nécessaires pour INCARNER un personnage (cf. ACTING_SECTIONS)."""
    ids = [f"{doc_id}::{section}" for section in ACTING_SECTIONS]
    got = _collection().get(ids=ids, include=["documents"])
    found = {i: d for i, d in zip(got["ids"], got["documents"])}
    return "\n\n".join(found[i] for i in ids if i in found)


def sessions_collection():
    """Collection de mémoire conversationnelle, créée à la demande.

    `get_or_create` et non `get` : la première session d'un personnage ne peut
    pas exiger qu'un indexeur soit passé avant elle.
    """
    return _chroma().get_or_create_collection(
        settings.sessions_collection, metadata={"hnsw:space": "cosine"}
    )


def session_memories(doc_id: str, *, n: int = 3) -> list[str]:
    """Résumés des dernières sessions de roleplay d'un personnage.

    Récupérés par MÉTADONNÉE (doc_id) puis triés par horodatage décroissant, pas
    par similarité : en début de session on ne sait pas encore de quoi on va
    parler, donc « les plus récents » bat « les plus proches d'une requête »
    qu'on n'a pas. Le retrieval sémantique reprend la main en cours de session.
    """
    try:
        got = sessions_collection().get(
            where={"doc_id": doc_id}, include=["documents", "metadatas"]
        )
    except Exception:      # collection absente ou Chroma muet : pas de mémoire
        return []
    pairs = sorted(
        zip(got.get("metadatas") or [], got.get("documents") or []),
        key=lambda p: (p[0] or {}).get("horodatage", ""),
        reverse=True,
    )
    return [doc for _, doc in pairs[:n]]


def semantic_context(query: str, *, doc_type: str, n: int = 3) -> list[str]:
    """Top-k chunks pertinents d'un type donné (lieu, scene) pour la requête."""
    results = (
        _collection()
        .query(
            query_embeddings=[embed(query)],
            n_results=n,
            where={"type": doc_type},
            include=["documents"],
        )
    )
    docs = results.get("documents") or [[]]
    return docs[0]


# Préambule de L'Involontaire. Il remplace celui d'un roman de fantasy au passé
# simple, qui contredisait FRONTALEMENT la fiche de style — laquelle classe le
# passé simple parmi ses interdits bloquants. Deux consignes contraires dans le
# même prompt système ne lèvent aucune erreur : elles produisent du texte moyen.
PREAMBLE = (
    "Tu écris le carnet de relecture d'une correctrice, à la première "
    "personne. Fantastique psychologique contemporain, passé composé et "
    "présent. Une maison, une voix, aucun dialogue. Elle écrit pour "
    "comprendre, pas pour raconter."
)


def assemble_system_prompt(
    *,
    characters: list[str],
    scene_brief: str,
    n_scenes: int = 2,
    include_scenes: bool = True,
    rag: bool = True,
    style: tuple[str, ...] = WRITING_STYLE,
    epistemic: bool = True,
) -> str:
    """Construit le prompt système d'une entrée.

    `rag` : c'est L'UNIQUE variable qui sépare l'étage A de l'étage B de la
        session 4. À False, aucun appel à Chroma ni au modèle d'embedding — le
        contexte narratif se limite au brief. En faire un paramètre, plutôt
        qu'une variable d'environnement à débrancher, est ce qui garantit que
        les deux étages ne diffèrent que par elle.
    `style` : sections de la fiche à servir (écriture ou relecture).
    `include_scenes` : injecter les entrées précédentes retrouvées. À DÉSACTIVER
        pour la rédaction : le modèle RECOPIE une entrée présente dans son
        contexte plutôt qu'il ne s'en sert de toile de fond. La continuité est
        assurée par le threading explicite de `write_node`.

    L'appel « lieu par similarité » a disparu : il n'y a qu'une maison, et
    aucune scène hors les murs.
    """
    parts: list[str] = [PREAMBLE]

    style_block = style_sections(style)
    if style_block:
        parts.append("=== CONTRAT DE STYLE (à respecter sans exception) ===\n"
                     + style_block)
    if epistemic:
        parts.append("=== RÈGLE DU RÉCIT ===\n" + EPISTEMIC_LINE)

    if not rag:
        return "\n\n".join(parts)

    for doc_id in characters:
        block = character_context(doc_id)
        if block:
            parts.append(f"=== NARRATRICE : {doc_id} ===\n{block}")

    if include_scenes and n_scenes > 0:
        scenes = semantic_context(scene_brief, doc_type="scene", n=n_scenes)
        if scenes:
            parts.append(
                "=== ENTRÉES PRÉCÉDENTES (contexte de continuité — NE PAS "
                "RECOPIER, seulement pour la cohérence) ===\n" + "\n\n".join(scenes)
            )

    return "\n\n".join(parts)
