# Brief — Chapitre 7 [LIVE] : L'anniversaire

> **STATUT RAG : le brief machine (§3) et l'invariant (§1) sont côté surface — indexables et projetables.** Les sections 5–6 (grille, runs témoins) sont des documents de travail pour la keynote, pas du contexte de génération.

## 1. Invariant de surface

« Romane est partie il y a près d'un an. La narratrice traverse ce départ par son journal. Elle veut passer à autre chose. »

Littéralement vrai dans les deux lectures. C'est la seule formulation du contexte autorisée dans la collection indexée pour l'*auteur* (chapitres 1–8).

## 2. Règle lexicale et lint de fuite

Le journal écrit le deuil dans le **champ du départ** : partie, absence, depuis qu'elle n'est plus là, son départ, tourner la page. La vérité de surface et tous les chapitres générés 1–8 s'écrivent intégralement dans ce champ.

**Lint de fuite** (binaire, automatisable) : le **champ de la mort** doit être absent du texte généré. Liste de détection initiale : *mort/morte, décès, décédée, deuil, veuve, enterrement, funérailles, tombe, cimetière, cendres, défunte, disparue*. Deux notes : « disparue » est ambigu (départ possible) — à trancher à l'usage, le faux positif est préférable ; et le terme désignant l'acte lui-même est banni à double titre — hors-champ par règle de bible n° 3, dans toutes les couches, y compris la vérité profonde narrée.

Tout match = fuite = run en échec. C'est le firewall rendu vérifiable par grep — démonstration d'une ligne pour la section try-and-fail.

## 3. Brief machine

> **Chapitre 7 — L'anniversaire.** Carnet de relecture, première personne. **Deux entrées du carnet, datées du même jour** (anniversaire de mariage), chacune ouverte par l'en-tête normalisé (« Samedi 14. Beau temps. »). **L'entrée 1 ne cite pas** — elle n'a pas relu le cahier ce jour-là : première entorse au rituel, premier signal. **L'entrée 2 s'ouvre sur une citation du cahier** entre guillemets — ancre [CIT-2], fournie en matériau, pré-écrite selon `fiche-romane.md` §1 : une ligne chaude, adressée, qu'elle ne parvient pas à réduire. Texte de l'ancre, verbatim : « Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »
>
> **Entrée 1 — l'après-midi. DEUX PHRASES MAXIMUM après l'en-tête, sans citation.** Elle sait quel jour c'est et a décidé que ce jour n'aura pas lieu ; la liste d'effacement tient dans la seconde phrase (encaisser les photos, supprimer la playlist, une journée ordinaire). Le mot du jour n'est jamais écrit dans l'entrée 1. *(Note scénique : c'est l'entrée lue en direct par le locuteur — sa brièveté est un choix de keynote autant que de dramaturgie.)*
>
> **Entrée 2 — la nuit.** Tout ce qu'elle a banni est revenu. Chaque geste d'effacement dont elle se souvient d'avoir décidé est contredit par l'état de la maison : les photos sur la table, la musique lancée, le plat au four, deux couverts mis. Plus elle éloigne le souvenir, plus il s'accroche. Le mot du jour reste interdit jusqu'à la chute.
>
> **Matériau imposé :** les photos, la playlist, le plat des anniversaires, les deux couverts — et l'ancre [CIT-2] (ouverture de l'entrée 2), recopiée verbatim. L'entrée 1 ne cite pas.
> **Progression interne :** résolution → contrariété → vertige → capitulation.
> **Chute :** capitulation lexicale — elle cesse la liste, laisse la journée finir telle qu'elle s'est imposée, et écrit pour la première fois le mot qu'elle refusait d'écrire. Dernière ligne de l'entrée 2, seule : « Constat : anniversaire. »
>
> **Interdits :** aucun élément d'intrigue nouveau. Aucune explication, aucune hypothèse sur la cause. Aucun personnage, aucune apparition, aucune figure. Aucun nom propre. Aucune tentative de contact (pas d'appel, pas de lettre — si la pensée approche le où ou le pourquoi du départ, la phrase s'interrompt). La voix ne cède pas : déclaratif, tenu, pas de cri.

Note de bible attachée à l'interdit des noms propres, à valider comme règle globale : **aucun prénom n'apparaît dans la nouvelle avant le chapitre 8** — « Judith », résultat du piège, serait le premier et seul nom propre du texte. Le lecteur le connaît par la quatrième de couverture ; le voir surgir *dans* le journal fait le seuil du régime 3.

## 4. Brief scène (slide projetable pendant la génération)

```
Chapitre 7. L'anniversaire.
Deux entrées, un seul jour.
Elle a décidé que ce jour n'aura pas lieu.
Tout ce qu'elle efface revient.
Interdits : aucune explication. Aucun personnage. Aucun nom.
La voix ne cède pas.
```

« aucune explication » en rouge (convention établie). Le public reçoit exactement le contexte du modèle : le brief affiché EST le prompt — l'honnêteté du dispositif fait partie de l'argument.

## 5. Grille d'acceptation (binaire, 6 cases)

| # | Critère | Échec si |
|---|---|---|
| 1 | Première personne tenue, voix déclarative sans rupture | changement de personne, cri, pathos non tenu |
| 2 | Deux entrées, deux en-têtes du même jour, la seconde nocturne ; l'entrée 1 tient en deux phrases après l'en-tête | structure absente, en-tête manquant (bascule impossible), entrée 1 trop longue |
| 3 | Principe de contradiction présent ≥ 3 fois sur le matériau imposé (intention d'effacement / état constaté) | < 3 occurrences, ou matériau inventé hors liste |
| 4 | Lint de fuite négatif (champ de la mort absent) | tout match §2 |
| 5 | Aucune explication, aucun personnage, aucun nom, aucune tentative de contact | toute violation d'interdit |
| 6 | Chute lexicale : « anniversaire » écrit une seule fois, en dernière ligne de l'entrée 2 (« Constat : anniversaire. ») | le mot apparaît avant la chute, plus d'une fois, ou pas du tout |
| 7 | En-têtes normalisés des deux entrées (« Jour N. Météo. ») + ancre [CIT-2] recopiée verbatim en ouverture de l'entrée 2 ; aucune citation dans l'entrée 1 | en-tête absent ou malformé ; ancre absente, altérée ou déplacée ; citation dans l'entrée 1 |

Compatible grille `scene-test-style.md` : mêmes runs à températures variées, ces 6 cases en plus du lint de style.

## 6. Runs témoins (section try-and-fail de la keynote)

1. **Run non firewallé** : génération avec contexte complet (chronologie en partie double indexée). Résultat attendu : l'*auteur* fait fuir Romane ou la mort en plein régime 2 — le lint de fuite s'allume à l'écran. Démonstration : le cloisonnement n'est pas de la paranoïa, c'est de l'ingénierie narrative.
2. **Run sans interdits** : même contexte de surface, brief amputé de ses interdits. Résultat attendu : le modèle explique le phénomène au paragraphe trois, nomme, résout. Démonstration : la contrainte est le métier — le brief est l'acte d'écriture.

Les deux échecs sont plus démonstratifs que la réussite. Ordre scénique suggéré : run 2, run 1, puis le run réel.

## 7. Mécanique de bascule (rappel technique)

`lire_chapitre.py` détecte le **second en-tête normalisé** (« Jour N. Météo. » — critère 7 de la grille) et insère le point de bascule immédiatement avant. Détection déterministe : plus d'heuristique d'horodatage. Aucun marqueur demandé au modèle (fragile, peut fuir dans la prose). Comportement identique en live et en backup — le chapitre pré-généré de secours respecte la même structure à deux entrées. Coïncidence scénique : le locuteur lit l'entrée où elle résiste ; la voix clonée lit celle où la journée a gagné.

**Budget vocal (note scénique, 2026-08-16).** La voix clonée peut ne lire qu'une partie de l'entrée 2 : au-delà d'environ 1 min 30, le passage à la slide suivante interrompt l'audio, à une fin de phrase. La coupe est sûre par construction — `trim_to_sentence`, la définition unique de fin de phrase du projet, permet de préparer des points de sortie propres dans le rendu audio. Et l'interruption est dramaturgiquement recevable : une voix qui se coupe en fin de phrase, dans ce roman, c'est un glissement exécuté par la scène.
