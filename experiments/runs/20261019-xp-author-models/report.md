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

## Ce qui a tourné

Commit `6648499`, 2026-10-19, 22:33–23:08, par graine N puis M, modèle
précédent déchargé avant chaque run, aucun refus du préflight.

- N × 3 : `ready`.
- M × 2 `ready` (395959, 528559) ; M/781771 en **erreur** après 3 min :
  l'assertion de `_prompt_beat` (graph.py:1413) refuse le prompt du temps
  suivant, qui porte « grille » — un mot que M a écrit dans un temps
  précédent (le texte déjà écrit est resservi en tête du prompt). Le mot est
  un terme d'atelier pour la garde, du français ordinaire pour le modèle
  (vraisemblablement la grille du four). Défaut du harnais : la garde des
  termes servis s'applique au texte du modèle resservi. N n'y est pas
  immunisé ; il n'a simplement pas écrit le mot sur ces graines.

## La grille (texte final)

| bras | graine | temps | tok/s (chapitre) | mots | mots entrée 2 | 3ᵉ personne (avert.) | « aucune variante propre » | accumulation abandonnée | italique Markdown (entrée 2) |
|---|---|---|---|---|---|---|---|---|---|
| N | 395959 | 355 s | 8,6 | 407 | 388 | 0 | 1 | 0 | 0 |
| N | 528559 | 372 s | 8,4 | 340 | 320 | 0 | 0 | 0 | 0 |
| N | 781771 | 355 s | 9,5 | 311 | 281 | 0 | 1 | 1 | 0 |
| M | 395959 | 408 s | 9,0 | 327 | 207 | 3 | 1 | 1 | 2 |
| M | 528559 | 409 s | 10,5 | 487 | 258 | 3 | 2 | 1 | 0 |
| M | 781771 | erreur | | | | | | | |

Moyennes : temps N 361 s, M 408 s (×1,13) ; mots de l'entrée 2 N 330, M 233.

## Prédictions

- **M1 (vitesse, ≥ 15 % plus rapide)** : **réfutée**. M est 13 % plus lent
  sur le chapitre, malgré un débit par jeton un peu plus haut : il écrit plus
  de variantes rejetées et d'essais d'accumulation (l'essai à blanc à 355 s
  n'était pas représentatif).
- **M2 (pas plus de fuite)** : tenue sur la fuite lexicale (aucune, les deux
  bras) ; mais M introduit deux défauts absents de N : la troisième personne
  (3 avertissements par run, 0 chez N) et l'italique Markdown.
- **M3 (lecture)** : non lue à ce stade (voir la règle).

## La règle

« Rejeté si … un run compté non `ready` » : M/781771 est en erreur, donc M
est **rejeté** à la lettre. Indépendamment de la cause de l'erreur, M montre
aussi un défaut de véto absent de N (troisième personne) et une entrée 2
plus courte de 30 %. Une lecture aveugle ne pourrait pas le sauver : la
règle exige aussi « aucun défaut de véto absent de N ».

## Bras abandonnés avant tout tirage

- **G (`gemma4:12b-it-q8_0`)**, décision de l'auteur, 2026-10-19 : la réflexion
  est active par défaut (réponse vide, le raisonnement en anglais mange
  `num_predict`) et `think: false` demanderait un changement dans `src/` ;
  une réponse commencée redémarre au lieu d'être continuée, or les temps de
  P sont des continuations ; 14 Go chargé, 12 % sur le CPU dès 4k de contexte.
  Les prédictions G1–G3 ne sont pas testées.
