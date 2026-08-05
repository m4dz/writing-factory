# fiction-assistant

Stack locale de rédaction littéraire assistée. Règle d'or : la fabrique reste à notre main — tout tourne en local.

## Architecture

- **Ollama** (hors conteneur, GPU Apple Silicon) : serving des modèles + embeddings `nomic-embed-text`
- **ChromaDB** (conteneur, mode serveur HTTP) : base vectorielle de la bible monde
- **Indexeur** (conteneur à la demande) : Markdown → chunks → embeddings → ChromaDB
- **OpenWebUI** (conteneur) : frontend
- **LangGraph** (à venir) : orchestration RAG dynamique

La source canonique est `bible/` (Markdown, édité à la main). ChromaDB est
toujours généré *depuis* cette source, jamais l'inverse.

## Prérequis

```sh
ollama pull nomic-embed-text
```

Vérifier qu'Ollama écoute bien sur `11434` :

```sh
curl -s http://localhost:11434/api/tags | head -c 200
```

## Démarrage

```sh
# 1. Lancer les services persistants (OpenWebUI + ChromaDB)
podman-compose up -d

# 2. Vérifier que ChromaDB répond
curl -s http://localhost:8000/api/v2/heartbeat

# 3. Créer une fiche : copier le template, le remplir, retirer le _ du nom
cp bible/characters/principals/_template.md bible/characters/principals/elara-vance.md

# 4. Indexer la bible
podman-compose --profile tools run --rm indexer

# 5. Valider le retrieval
podman-compose --profile tools run --rm indexer python query_test.py "quelle est la fracture d'Élara ?"
podman-compose --profile tools run --rm indexer python query_test.py "sa voix" --doc elara-vance
podman-compose --profile tools run --rm indexer python query_test.py "la forge" --type lieu
```

## Cycle de travail

1. Éditer une fiche dans `bible/` (le plus souvent : le chunk *État narratif
   courant*, seul chunk mis à jour régulièrement)
2. Incrémenter `version` dans le frontmatter
3. `podman-compose --profile tools run --rm indexer`

L'indexation est idempotente : chunks mis à jour, chunks orphelins purgés.

## Conventions

- Les fichiers préfixés `_` (templates) ne sont jamais indexés
- Un chunk = une section `## ` d'une fiche ; ID déterministe `{id}::{section}`
- Les commentaires HTML `<!-- -->` sont des instructions pour l'humain,
  purgés avant embedding
- Métadonnées de filtre : `type` (character, lieu, prop, scene), `rank`,
  `doc_id`, `section`, `tags`

## Dépannage

- **L'indexeur ne joint pas Ollama** : vérifier que
  `host.containers.internal` résout depuis un conteneur
  (`podman run --rm alpine ping -c1 host.containers.internal`). Selon la
  version de Podman, il faut parfois ajouter
  `--add-host=host.containers.internal:host-gateway` ou utiliser
  l'IP de la machine.
- **ChromaDB ne persiste pas** : selon la version de l'image, le répertoire
  de persistance peut être `/data` ou `/chroma/chroma`. Le compose fixe
  `PERSIST_DIRECTORY=/data` ; si les données disparaissent au redémarrage,
  vérifier les logs (`podman-compose logs chromadb`).
