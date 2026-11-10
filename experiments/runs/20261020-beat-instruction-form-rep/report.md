# beat-instruction-form, réplication — rapport

> Change : `openspec/changes/beat-instruction-form`. Même variable, mêmes
> réglages que `20261020-beat-instruction-form` (R prose contre F nominale,
> nemo, `beat_context=plan`), trois graines neuves : 935325, 981791, 992103.
> Commandée par l'auteur après la première lecture aveugle (F 2/1/0 contre
> R 1/2/0), que la règle mécanique avait déclarée non concluante.

## Correction de la première règle

La première règle faisait d'un compte de défauts (« aucun défaut de véto
absent de R ») une condition d'adoption au même rang que la lecture. Or le
juge est la lecture (doctrine 3) et le ton est la décision de l'auteur. Ici,
les défauts sont mesurés et rapportés ; ils orientent la sélection, ils ne
décident pas.

## Prédictions (écrites avant le premier tirage, jamais modifiées)

- **P1 (lecture).** F au moins égal à R sur 2 graines sur 3.
- **P2 (récitation).** F récite moins que R sur chaque graine.
- **P3 (personne).** F n'a aucun avertissement « troisième personne ».
- **P4 (défaut nouveau).** Au moins une variante tirée de F redémarre ou
  invente une présence ; au plus une est retenue.

## Règle de décision (écrite avant les runs)

Juge : la lecture aveugle de l'auteur, graine contre graine, sur les six
paires (première série et réplication).

- **F adopté** (forme de référence pour l'expérience modèles) si F est au moins
  égal à R sur ≥ 2 graines de la réplication, et pire sur aucune graine de la
  réplication.
- **F rejeté** si F est pire sur ≥ 2 graines de la réplication.
- **Sinon** : l'auteur tranche sur les six paires.

Les défauts retenus (ceux qui atteignent le chapitre) sont rapportés à côté
de chaque verdict ; un défaut retenu propre à F devient une tâche de la
sélection (chantier distinct), pas un motif de rejet.

Un run tué par la garde des termes est exclu et retiré sur la graine
suivante, pour les deux bras.

## Résultats

Six runs, aucun tué par la garde, aucun exclu. Mêmes mesures que la première
série.

| graine | bras | récitent | 3ᵉ pers. (variantes) | phrases courtes / phrases | mots entrée 2 | défauts de véto tirés | retenus avec défaut de véto |
|---|---|---|---|---|---|---|---|
| 935325 | R | 6/9 | 1 | 6/43 | 609 | 3ᵉ pers. ×1, décor interdit ×1 | — |
| 935325 | F | 6/9 | 0 | 6/19 | 325 | congédie ×1, décor interdit ×1 | — |
| 981791 | R | 8/9 | 3 | 6/22 | 323 | 3ᵉ pers. ×3, présence perçue ×1 | — (décide ×1) |
| 981791 | F | 6/9 | 0 | 6/23 | 284 | — | — |
| 992103 | R | 6/9 | 1 | 7/24 | 419 | 3ᵉ pers. ×1, congédie ×1 | — (décide ×1) |
| 992103 | F | 3/9 | 0 | 6/23 | 253 | — | — (décide ×2) |

Relève retenue de F : récitation **1,0** / 0,40 / 0,49 — à la graine 935325,
la relève du chapitre est encore la forme nominale mot pour mot.

### Prédictions (hors lecture)

- **P2** réfutée : égalité à 935325 (6/9 contre 6/9) ; moins aux deux autres.
- **P3** confirmée : F 0 ; R 1, 3, 1.
- **P4** réfutée : aucune variante de F ne redémarre ni n'invente de
  présence (un « congédie ») ; rien de retenu.
- **P1** : en attente de la lecture.

### Lecture aveugle

`blind/E01–E06.md`, clé fermée dans `blind-key.yaml`. Mêmes limites
d'aveugle que la première série.

Clé ouverte après les verdicts (`blind/verdicts.md`, 2026-10-20).

| graine | R | F | F contre R |
|---|---|---|---|
| 935325 | E04 oui — « le meilleur tirage jusqu'ici » (609 mots) | E02 oui — « maigre densité » | à trancher par l'auteur : égal (oui/oui) ou pire |
| 981791 | E05 partiel — « ton clinique ne pose pas le doute » | E06 non — « désordonné, erreurs, contre-sens » | pire |
| 992103 | E01 partiel — « micro-dérapages » | E03 oui — « bonne tenue du doute », densité faible | meilleur |

Réplication : R 1 / 2 / 0, F 2 / 0 / 1. Six paires : R 2 / 4 / 0, F 4 / 1 / 1.

La règle bascule sur la paire 935325 : pire → F rejeté (pire sur 2 graines) ;
égal → ni adopté (pire sur une graine) ni rejeté, l'auteur tranche sur les
six paires.

« Densité faible » revient sur trois des quatre « oui » de F, et sur un « oui »
de R ; le meilleur tirage est le plus long (609 mots contre 225–420).

## Verdict

**F rejeté, R reste** (décision de l'auteur, 2026-10-20, sur les six paires).
La prose en « elle » reste la forme servie ; l'expérience modèles se fait sur
la prose. Le code `beat_form=nominal` et les formes nominales du brief restent
en place, inertes par défaut (`prose`).
