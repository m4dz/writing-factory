# xp-author-models — rapport

> Change : `openspec/changes/xp-author-models`. Une variable : le tag du
> modèle auteur (le modèle des gestes le suit). `beat_context=plan`, QA
> inchangé, températures inchangées. Verdict : la lecture de l'auteur, à
> l'aveugle, clé ouverte après coup ; la grille n'est qu'un véto.

## Prédictions (écrites avant le premier tirage, jamais modifiées)

_Proposées par l’assistant, validées par l’auteur le 2026-10-19 avant les runs comptés._

- **M1 (vitesse).** M est plus rapide que N d'au moins 15 % (9,6 Go contre
  13 Go, débit mémoire borné).
- **M2 (langue).** M ne fuit pas plus que N (même lignée, corpus français).
- **M3 (lecture).** M fait au moins aussi bien que N sur 2 graines sur 3 ;
  l'hypothèse « génération Small dans le gabarit de nemo » survit seulement
  s'il fait mieux sur 2.
- **G1 (vitesse).** G est dans ±15 % du temps de N (même taille).
- **G2 (forme).** G montre au moins un défaut que N n'a pas (gras ou
  italique Markdown, calque anglais, ponctuation anglaise) sur au moins un
  run ; la grille, calibrée sur nemo, en attrape moins de la moitié.
- **G3 (lecture).** G ne fait pas mieux que N sur 2 graines.

## Règle de décision (écrite avant les runs)

Un challenger est adopté si, contre N : mieux sur ≥ 2 graines à la lecture
aveugle, ET aucun défaut de véto absent de N, ET aucune fuite lexicale, ET
temps moyen ≤ 1,25 × celui de N. Rejeté si pire sur ≥ 2 graines, ou un run
compté non `ready`. Deux adoptés : le meilleur décompte, puis le plus rapide.
Sinon N reste (le sortant garde l'égalité).

Une perte se lit « pire sous les prompts de nemo », pas « pire » : les
prompts servis ont été réglés contre nemo.

## Essai à blanc (graine 111111, non compté)

- Premier essai : erreur après 9,5 s, ChromaDB n'était pas lancé. Exclu.
- Second essai (`20261019-203848`, M) : `ready`, 355 s, 24 appels, aucune
  troncature. Passe les règles d'arrêt (français, pas de balise de gabarit,
  variantes non vides, temps).
- Observé, sans valeur de mesure : découverte 3/3 variantes à la troisième
  personne ; accumulation de l'entrée 2 abandonnée après deux essais (troisième
  personne) ; la citation de la relève recopiée en italique Markdown ;
  294 mots ; une présence inventée (le rouge à lèvres sur la spatule).

## Résultats

_À compléter : grille par bras (défauts de véto, mots, litanie, variantes
avec défaut, temps, tok/s), lecture aveugle, règle appliquée._

## Bras abandonnés avant tout tirage

- **G (`gemma4:12b-it-q8_0`)**, décision de l'auteur, 2026-10-19 : la réflexion
  est active par défaut (réponse vide, le raisonnement en anglais mange
  `num_predict`) et `think: false` demanderait un changement dans `src/` ;
  une réponse commencée redémarre au lieu d'être continuée, or les temps de
  P sont des continuations ; 14 Go chargé, 12 % sur le CPU dès 4k de contexte.
  Les prédictions G1–G3 ne sont pas testées.
