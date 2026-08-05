# CLAUDE.md — fiction-assistant

## Ce qu'est ce projet

Démonstrateur d'IA locale pour la rédaction littéraire, support technique de la
keynote « L'IA devant soi » (50', keynote de clôture). Deux fonctions :

1. **Assistant d'écriture** (« mode auteur ») : maintien d'une bible monde
   (personnages, lieux, props), planification de chapitres, ghostwriting.
2. **Roleplay** (« mode acteur ») : dialoguer avec les personnages pour
   explorer leur personnalité, sans sortie de personnage.

**Règle d'or, non négociable : tout tourne en local.** La fabrique reste à
notre main. Aucune API cloud, aucun logging externe. C'est la thèse même du
talk : une œuvre dont la fabrique est locale est inauditable.

## Contraintes de scène (keynote)

- La démo est lancée en début de talk et récoltée ~35 minutes plus tard :
  la génération complète d'un chapitre (plan de scènes + rédaction) doit
  tenir dans ce budget sur un MacBook Apple Silicon.
- Un compte à rebours est affiché pendant la génération.
- Le pipeline montré sur scène : plan de scènes → écriture → relecture →
  cohérence (c'est la « strate 4 » du talk, LangGraph).

## Architecture décidée (ne pas rediscuter sans raison forte)

- **Rejet du multi-instances** (un modèle par personnage) : la cohérence
  vient d'une mémoire externe partagée, pas de la multiplication des modèles.
  Les modèles ne sont que des *lecteurs* de la vérité stockée hors d'eux.
- **Trois couches** :
  - *Stockage* : Markdown canonique dans `bible/` (édité par l'humain) →
    ChromaDB (mode serveur HTTP, conteneurisé). ChromaDB est TOUJOURS généré
    depuis la source Markdown, jamais l'inverse.
  - *Retrieval/orchestration* : LangGraph, RAG contextuel dynamique — le
    contexte est assemblé à la requête (fiches des personnages présents,
    lieu, scènes précédentes pertinentes) en un prompt système de 2-3k tokens.
  - *Modèles* : deux rôles, pas plus. « Auteur » (Mistral-small, ou
    Mistral-nemo à évaluer pour la prose française) et « acteur » (roleplay,
    prompt système interdisant la sortie de personnage).
- **Ollama hors conteneur** (accès GPU Apple Silicon direct), joint depuis
  les conteneurs via `http://host.containers.internal:11434`.
  Embeddings : `nomic-embed-text` (768 dims, cosine).
- **Mémoire conversationnelle à deux niveaux** pour le roleplay (à
  implémenter) : N derniers échanges en contexte + rolling summary indexé
  dans ChromaDB, taggé par personnage, retrievé en début de session.
- **Limite connue** : Mistral-small rate parfois la cohérence causale longue
  distance. Mitigation : rendre EXPLICITES dans les fiches les liens de
  cause à effet (le template le rappelle), ne jamais supposer l'inférence.

## Structure

```
bible/                    # source canonique, éditée à la main
  characters/principals/  # fiches 7 chunks (voir _template.md)
  characters/secondaires/ # fiches allégées (3-4 chunks suffisent)
  lieux/  props/  scenes/ # scènes rédigées et validées
indexer/                  # index.py + query_test.py, conteneurisé
data/chromadb/            # volume persistant
podman-compose.yml        # openwebui + chromadb + indexer (profil tools)
```

## Conventions établies

- Un chunk = une section `## ` d'une fiche. ID déterministe `{id}::{slug}`.
- Chunk préfixé `[doc_id / Titre]` avant embedding (améliore le matching).
- Fichiers `_*.md` jamais indexés (templates).
- Commentaires HTML `<!-- -->` = instructions pour l'humain, purgés avant
  embedding.
- Métadonnées scalaires uniquement (listes → CSV). Filtres : `type`
  (character, lieu, prop, scene), `rank`, `doc_id`, `section`, `tags`.
- Sept chunks par personnage principal : psychologie, comportement et
  présentation, voix et expression, histoire, compétences et capacités,
  relations, **état narratif courant** — ce dernier est le SEUL mis à jour
  régulièrement (incrémenter `version`, réindexer).
- Le chunk voix contient des répliques typiques ET des contre-exemples
  (« ne dirait jamais ») : les exemples négatifs ancrent mieux la voix.
- Personnages du récit : 2 principaux, 3 secondaires (à créer).

## État actuel

- [x] Structure du projet, template personnage 7 chunks
- [x] podman-compose : ChromaDB (port 8000) + indexeur (profil tools)
- [x] Indexeur idempotent testé (parsing/chunking validés hors connexion)
- [x] query_test.py pour valider le retrieval
- [x] Validation sur machine réelle (Ollama 0.0.0.0:11434 + ChromaDB) :
      connectivité conteneur→Ollama OK sans `--add-host`, embeddings 768d,
      index/query/purge/persistance validés. Bug purge sur bible vide corrigé.
- [ ] Peupler le premier personnage principal
- [ ] Orchestrateur LangGraph (mode auteur d'abord)
- [ ] Pipeline chapitre : plan de scènes → écriture scène par scène →
      relecture (celui qui tourne pendant la keynote)
- [ ] Mode acteur (roleplay) + mémoire conversationnelle rolling summary
- [ ] Intégration frontend (OpenWebUI via pipelines, ou interface dédiée —
      non tranché)
- [ ] Habillage démo : compte à rebours, affichage de la progression

## Prochaine étape convenue

Valider le retrieval sur machine réelle, puis peupler le premier personnage
principal AVANT d'attaquer LangGraph (un orchestrateur sans matière à
retriever est indéboguable).

## Points de vigilance connus

- `host.containers.internal` peut nécessiter `--add-host=...:host-gateway`
  selon la version de Podman.
- Le chemin de persistance de l'image ChromaDB varie selon les versions
  (`/data` vs `/chroma/chroma`) — vérifier que les données survivent à un
  restart.
- Budget temps de la démo : profiler tôt la génération complète d'un
  chapitre sur la machine de scène. C'est LA contrainte dure du projet.

## Style de travail du propriétaire

Challenger les propositions plutôt qu'acquiescer. Expliquer les *pourquoi*
architecturaux. Pas de listes à puces gratuites dans la prose. Le contenu
littéraire est en français ; le code et ses commentaires aussi.
