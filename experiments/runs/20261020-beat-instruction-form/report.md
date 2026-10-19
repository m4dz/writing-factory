# beat-instruction-form — rapport

> Change : `openspec/changes/beat-instruction-form`. Une variable : la forme
> servie des temps de l'entrée 2 (prose en « elle » contre forme nominale, sans
> personne). nemo, `beat_context=plan`, graines neuves. Verdict : la lecture
> de l'auteur, à l'aveugle ; la grille n'est qu'un véto ; la récitation est
> mesurée par `recital.py` sur toutes les variantes tirées.

## Ligne de base (xp-author-models, nemo, prose, plan)

Variantes qui récitent la consigne (similarité phrase à phrase ≥ 0,50) :
6/9, 6/9, 7/9 ; relève et découverte entre 0,72 et 1,0, le doute ≤ 0,50.

## Prédictions (écrites avant le premier tirage, jamais modifiées)

_Proposées par l'assistant, à valider par l'auteur avec les formes nominales._

- **F1 (récitation).** F récite dans au plus 2 variantes sur 9 par run, contre
  au moins 5 pour R, sur chaque graine.
- **F2 (personne).** F n'a aucun avertissement « troisième personne » ; R en a
  au moins un sur 2 graines sur 3 (la copie verbatim en « elle »).
- **F3 (contamination).** F a plus de phrases courtes (≤ 6 mots) dans
  l'entrée 2 que R, de moins de 50 % en plus.
- **F4 (lecture).** F fait au moins aussi bien que R sur 2 graines sur 3.

## Règle de décision (écrite avant les runs)

F est adopté (forme de référence pour l'expérience modèles) si : moins de
variantes qui récitent que R sur les 3 graines, ET lecture aveugle au moins
égale sur ≥ 2 graines, ET aucun défaut de véto absent de R, ET phrases
courtes de l'entrée 2 pas plus de 1,5 × R. Rejeté si la lecture est pire sur
≥ 2 graines, ou si F récite autant que R. Sinon : non concluant, la prose
reste, et l'expérience modèles se fait sur la prose.

Un run tué par la garde des termes (défaut connu,
`beat-guard-model-text`, non corrigé sur cette branche) est exclu et
retiré sur la graine suivante (1, 2, 3… ajoutés à la graine), pour les deux
bras : la même graine reproduirait la même mort.

## Essai à blanc (graine 111111, F seul, non compté)

_À compléter._

## Résultats

_À compléter._
