# Jalon — test de style

Protocole de calibration de la fiche `style-auteur.md` : trois générations
de la scène test avec la fiche complète en prompt système, lecture à voix
haute, grille de lint binaire, plus un run de contrôle pour isoler le
facteur de confusion des lignes régime.

**Point d'architecture :** ce test NE passe PAS par le RAG. Il mesure le
plafond — ce que le modèle tient avec la fiche complète en contexte. Le
circuit : fiche → prompt système (Modelfile) → génération. LangGraph servira
plus tard des morceaux de cette fiche *validée* ; on ne câble pas
l'orchestration sur une fiche non calibrée.

## Prérequis

1. `style-auteur.md` placé dans `bible/style/` (créer le dossier)
2. La scène test renommée `_scene-test-style.md`, placée dans
   `bible/scenes/` (le préfixe `_` la protège de l'indexation : c'est un
   outil, pas du canon narratif)
3. Ollama opérationnel avec `mistral-small` tiré
4. Copier `outillage/` et `runs/` de ce paquet à la racine du projet

## Séquence

```sh
# 0. Sanity check stack (optionnel) : la fiche est indexée et retrievable
podman-compose run --rm indexer
podman-compose run --rm indexer python query_test.py "rythme des phrases" --doc style-auteur

# 1. Construire le modèle de test (fiche complète en prompt système)
python3 outillage/build_modelfile.py
ollama create auteur-test -f Modelfile.auteur-test

# 2. Les trois runs (chaque run = contexte neuf, le modèle ne s'auto-imite pas)
python3 outillage/run_scene.py

# 3. Le run de contrôle (brief sans les lignes « Régime : … »)
python3 outillage/run_scene.py --control

# 4. Scorer : lecture à voix haute, puis grille
#    → outillage/grille-lint.md (copier en grille-lint-session-1.md, remplir)
```

Les scripts d'outillage tournent sur l'hôte (pas en conteneur) car ils
pilotent Ollama et `ollama create`. Stdlib Python uniquement, rien à
installer.

## Boucle d'ajustement

1. Défaut présent sur les 3 runs → ajuster le chunk fautif de la fiche
2. Incrémenter `version` dans le frontmatter de `style-auteur.md`
3. Réindexer (`podman-compose run --rm indexer`) — pour garder ChromaDB
   synchrone, même si le test lui-même n'y passe pas
4. Reconstruire le modèle : `python3 outillage/build_modelfile.py &&
   ollama create auteur-test -f Modelfile.auteur-test`
5. Régénérer, re-scorer

Ne jamais éditer le Modelfile à la main : la fiche Markdown est la source
canonique, le Modelfile est toujours régénéré depuis elle (même règle que
pour ChromaDB).

## Réglages

- Trois runs trop sages ou trop semblables → `--temperature 0.9` (voire 1.0)
  au build_modelfile, recréer le modèle
- Pastiche gothique dès le run 1 → renforcer le chunk *interdits* AVANT de
  toucher à la température (c'est le chunk qui travaille le plus dur avec
  Mistral-small)
- Évaluation comparative de mistral-nemo pour la prose française :
  `python3 outillage/build_modelfile.py --base mistral-nemo --name auteur-test-nemo`
  puis `run_scene.py --model auteur-test-nemo` — mêmes runs, même grille

## Critère de sortie du jalon

Fiche validée = zéro défaut bloquant sur 3 runs consécutifs, les quatre
régimes traversés, et une lecture à voix haute qui tient 90 secondes sans
accroc. C'est l'extrait de la section 7 du talk qui se joue ici.
