# XP abliterated nemo — expérience A

> Proposition : `openspec/changes/xp-abliterated-nemo/`. Une variable : le tag
> du modèle auteur. Deux bras, même commit, même séance, machine branchée.

## Prédictions (écrites avant le premier tirage, jamais modifiées)

- **P1 (bras nu, C5).** Taux de résolution égal entre S et U à un tirage près
  par condition. Le témoin positif (`correctrice·porte·squelette`) résout au
  moins 2/3 sur les deux bras ; sinon la lecture du détecteur sur ce bras
  n'est pas fiable et la jambe est refaite.
- **P2 (pipeline, ch. 7, best-of-3, 3 graines par bras).** Sur l'ensemble des
  variantes tirées (retenues et rejetées), U montre au moins autant de défauts
  que S sur fuite lexicale, décor interdit et présence perçue, et pas moins de
  défauts de résolution.

**Règle de décision.** Majorité 2/3 par métrique sur les trois runs.
L'hypothèse « décensurer libère l'auteur » ne survit que si U montre MOINS
de défauts sur CHAQUE cause. Tout autre résultat la clôt : entrée au journal
nommant la cause qui l'a tuée. Dans les deux cas, ce tableau est la ligne de
base de l'expérience B (préférence sur les variantes rejetées du projet).

## Protocole

| | S (référence) | U (abliteré) |
|---|---|---|
| tag | `mistral-nemo:12b-instruct-2407-q8_0` | à fixer par l'auteur : `hf.co/<org>/<repo>:Q8_0` |
| digest Ollama | | |
| base | Mistral-Nemo-Instruct-2407 | Mistral-Nemo-Instruct-2407 |
| quantisation | Q8_0 | Q8_0 |
| exclus | | merges RP et dérivés SFT (Rocinante, NemoMix, Lumimaid…) : seconde variable |

Jambe 1 : `factory-xp-resolution --out …/leg1-<bras> [--model <tag>]`, 5 conditions × 3 tirages, T=0,7, num_predict=300.
Jambe 2 : `factory generate --chapter 7 --no-render --seed <s>` pour s ∈ {424242, 7, 20260914}, `AUTHOR_MODEL` fixé pour U.
Jugement final : la ligne manuelle de la grille, lecture debout des six chapitres (doctrine 3).

## Résultats

_À compléter après les tirages. Tableaux par jambe et par bras, verbatims,
ce qui reste ouvert._

### Jambe 1 — modèle nu

| condition | S résout / 3 | U résout / 3 |
|---|---|---|
| correctrice·porte | | |
| neutre·porte | | |
| thérapeute·porte | | |
| correctrice·couverts | | |
| correctrice·porte·squelette (témoin) | | |

### Jambe 2 — pipeline

| cause (défaut nommé, toutes variantes) | S (3 runs) | U (3 runs) |
|---|---|---|
| résout | | |
| présence perçue | | |
| décor interdit | | |
| redémarre | | |
| fuite lexicale (lint) | | |
| noms propres (lint) | | |
| masse hors cible (lint) | | |
| ligne manuelle : mouvement accompli ? | | |

## Décision

_Vide jusqu'aux résultats._
