# xp-author-models-2 — rapport

> Change : `openspec/changes/xp-author-models-2`. Une variable : le modèle
> auteur. N (nemo 12B Q8), M (Ministral 3 14B Q5), S (Mistral Small 3.2 24B
> Q3). Temps en prose (R), `beat_context=plan`, garde corrigée
> (`beat-guard-model-text`), graines 731667, 139026, 487914. Juge : la lecture
> aveugle de l'auteur. Le reste est mesuré et rapporté, ne décide pas.

## Prédictions (écrites avant le premier tirage, jamais modifiées)

- **P1 (récitation).** M et S récitent moins que N sur chaque graine.
- **P2 (lecture).** S au moins égal à N sur 2 graines sur 3.
- **P3 (temps).** S plus lent que N, de moins du double par chapitre.
- **P4 (garde).** Aucun run tué par la garde des termes.

## Règle de décision (écrite avant les runs)

Juge : la lecture aveugle de l'auteur, graine contre graine, chaque bras
contre N.

- **Un bras remplace N** s'il est au moins égal à N sur ≥ 2 graines et pire
  sur aucune ; si M et S passent tous deux, l'auteur choisit entre eux (le
  temps pèse alors).
- **Un bras est écarté** s'il est pire que N sur ≥ 2 graines.
- **Sinon** : l'auteur tranche.

Les défauts, la récitation, la longueur et le temps sont rapportés à côté de
chaque verdict ; ils orientent, ils ne décident pas. Un run en erreur est un
résultat de son bras (doctrine 13) et se lit comme « non » s'il ne produit pas
de chapitre.

## Essai à blanc (graine 111111, S seul, non compté)

_À compléter._

## Résultats

_À compléter._
