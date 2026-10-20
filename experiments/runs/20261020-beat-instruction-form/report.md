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

_Proposées par l'assistant ; validées par l'auteur le 2026-10-20, formes nominales corrigées (B : « fête non-désirée », « un métier » retiré)._

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

Mécanique passée : pas de copie en « elle », aucune variante vide, la garde
tient. Lu : la relève retenue EST la forme nominale (1,0, « aucun défaut ») —
la sélection n'a pas de défaut pour une récitation sans personne. Découverte
et doute perdent leur sujet (ni maison dressée, ni mains froides, ni crayon) ;
« je décide » dans 5 variantes sur 6 ; une bascule en anglais (« fête.yet I
have no memory… »), non retenue. Récitation 4/9.

## Résultats

Six runs, aucun tué par la garde, aucun exclu. Récitation : `recital.py` sur les
9 variantes tirées (≥ 0,50 contre l'une ou l'autre forme). Phrases courtes :
≤ 6 mots, entrée 2 du chapitre (après la bascule).

| graine | bras | récitent | 3ᵉ pers. (variantes) | phrases courtes / phrases | mots entrée 2 | défauts de véto tirés | retenus avec défaut |
|---|---|---|---|---|---|---|---|
| 140419 | R | 7/9 | 8 | 6/21 | 255 | 3ᵉ pers. ×8 | découverte, doute : 3ᵉ pers. |
| 140419 | F | 3/9 | 0 | 7/24 | 361 | vide ×1, récursion ×1, décor interdit ×1 | — (décide ×2) |
| 602237 | R | 6/9 | 4 | 7/23 | 310 | 3ᵉ pers. ×4, résout ×1 | — |
| 602237 | F | 5/9 | 0 | 6/22 | 226 | présence perçue ×1 | — (décide ×1) |
| 913085 | R | 6/9 | 1 | 6/28 | 340 | 3ᵉ pers. ×1, décor interdit ×2 | — (décide ×1) |
| 913085 | F | 2/9 | 0 | 8/21 | 281 | redémarre ×2, récursion ×1, congédie ×1, présence perçue ×1, résout ×1 | découverte : redémarre |

Ligne de base prose (xp-author-models, mêmes réglages, autres graines) :
récitation 6, 6, 7/9 ; défauts de véto tirés : 3ᵉ pers. et résout seulement.

Relève retenue de F : récitation 0,47 / 0,55 / **1,0** — à la graine 913085,
la relève du chapitre est la forme nominale mot pour mot (comme à blanc).

### Prédictions

- **F1** réfutée en partie : F récite moins que R à chaque graine (3<7, 5<6,
  2<6), mais ≤ 2/9 sur une graine seulement.
- **F2** confirmée : F 0 ; R 8, 4, 1.
- **F3** confirmée : F 21 phrases courtes contre 19 (+11 %), ≤ 1,5 × R à
  chaque graine (7/6, 6/7, 8/6).
- **F4** : en attente de la lecture aveugle.

### Règle, avant lecture

- moins de récitation que R sur les 3 graines : **oui** ;
- phrases courtes ≤ 1,5 × R : **oui** ;
- aucun défaut de véto absent de R : **non** — tirés : vide, récursion,
  présence perçue, redémarre, congédie n'apparaissent jamais dans R (ni dans
  la ligne de base) ; retenus : « redémarre » à 913085.

F ne peut donc pas être adopté. Reste à la lecture de trancher entre rejeté
(pire sur ≥ 2 graines) et non concluant.

### Lecture aveugle

`blind/E01–E06.md` (graine de mélange 419032), clé fermée dans
`blind-key.yaml`. Non tout à fait aveugle : une relève nominale mot pour mot
ou une consigne transposée (« c'est mon métier », « ne fais pas le tour ») se
reconnaît.

_À compléter après les verdicts._
