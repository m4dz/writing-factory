# plan-state-beats — rapport

> Change : `openspec/changes/plan-state-beats`. P tiré le 2026-10-19,
> 10:30–10:55, commit `fe88b0b` (servi v3). R tiré le 2026-10-18
> (`20261018-beats-see-movement`, jamais lu avant). Verdict : la lecture de
> l'auteur, à l'aveugle (`blind/verdicts.md`, graine 503640), clé ouverte
> après coup ; la grille n'est qu'un véto.

## Ce qui a tourné

- Trois essais à blanc (graine 111111, non comptés) :
  - **v1** (`f3e5ac6`, plan d'état + porte de progression) : découverte 3/3
    et doute 3/3 recopient l'entrée. Arrêt.
  - **v2** (`695b197`, la réponse commencée par le dernier paragraphe, la
    tâche lue en dernier, le système replié dans la question) : plus de
    recopie, mais 6/9 variantes vides (nemo clôt après un point final) et le
    doute écrit sa condition de fin dans le texte. Un premier essai v2 a été
    tué par la pression mémoire (exclu). Arrêt.
  - **v3** (`fe88b0b`, réponse commencée suivie d'une ligne blanche, variante
    de moins de deux phrases rejetée, condition de fin dans la ligne d'état) :
    passe les vérifications mécaniques.
- P × 3 (395959, 528559, 781771), tous `ready`, aucun refus du préflight.

## La grille (entrée 2, texte final)

| bras | défauts de véto | mots (moy.) | litanie (moy.) | variantes avec défaut avant sélection |
|---|---|---|---|---|
| R | 3 (redémarrage, décor, résolution) | 365 | 0,14 | 8/27 |
| P | 1 (décor) | 372 | 0,21 | 0/27 |

Dans P, aucune recopie, aucune variante vide, aucun avertissement « aucune
variante propre ». La litanie la plus haute est P/528559 (0,38).

## La lecture de l'auteur

| graine | R | P | P contre R |
|---|---|---|---|
| 395959 | partiel (E01) | **oui** (E05) | mieux |
| 528559 | partiel (E04) | partiel (E06) | égal |
| 781771 | oui (E03) | oui (E02) | égal |
| **oui / partiel / non** | 1 / 2 / 0 | **2 / 1 / 0** | |

Notes : E05 (P) « excellente progression, probablement le meilleur tirage » ;
E02 (P) « manque de densité, mais le mouvement est bon » ; E06 (P) « le
mouvement est bon, avec quelques incohérences, mais l'ensemble est à la
troisième personne » ; E01 (R) « plusieurs inventions de remplissage » ;
E03 (R) « le doute est bon » ; E04 (R) « le ton est nouveau et intéressant,
même si pour le moment trop chirurgical ».

## La règle (écrite avant les runs)

P est adopté si : mieux que R sur ≥ 2 graines, ET moins de notes
« invente », ET aucun défaut de véto absent de R, ET longueur moyenne ≥ 365.
Rejeté si pire sur ≥ 2 graines, ou doute absent ou recopié dans ≥ 2 entrées.

- Mieux sur ≥ 2 graines : **non** (1 mieux, 2 égales).
- Moins de notes d'invention : oui (R : E01 ; P : aucune ; « incohérences »
  sur E06, que je ne compte pas comme invention).
- Défaut de véto absent de R : non (le décor de P existe aussi dans R).
- Longueur : 372 ≥ 365, oui.
- Rejet : aucune graine pire ; le doute n'est absent ni recopié nulle part
  d'après les notes.

**Verdict de la règle : non concluant.** P n'est ni adopté ni rejeté. Il
n'est pire nulle part, il est meilleur une fois, et il porte le seul tirage
que l'auteur désigne comme le meilleur.

## Ce que la série dit

1. **Le mécanisme tient mécaniquement** : en v3, plus de recopie ni de beat
   vide, 0/27 variantes en défaut avant sélection (R : 8/27). Il a fallu deux
   corrections que seuls les essais à blanc ont montrées : nemo recopie ce
   qu'on lui sert en bloc, et clôt une réponse commencée sur un point final.
2. **Le défaut nouveau de P : la troisième personne** (E06). Le beat
   transpose sa consigne, écrite en « elle », au lieu d'écrire en « je ».
   L'essai v3 le montrait déjà sur une variante de la relève. Ce n'est pas
   dans la liste de véto ; aucune vérification ne le voit.
3. **R lit mieux qu'au scaffold-ablation** (1 oui ici, 0 sur 3 hier) : trois
   graines ne mesurent pas un taux, la variance entre séries est du même
   ordre que l'écart entre bras.
4. **Le paragraphe d'accumulation résout le doute** dans les deux essais à
   blanc (« je prends deux couverts dans le tiroir »). Il vient du nœud
   d'accumulation, pas d'un beat ; il touche R comme P. Hors de cette
   change.

## À décider par l'auteur

- Garder P comme mécanisme de beat pour `storyboard-density` malgré le
  non-concluant (la règle ne l'impose pas, elle ne l'interdit pas), ou
  garder R comme référence.
- Si P est gardé : une vérification « troisième personne » (pronom de la
  narratrice) dans la sélection, falsifiée sur E06 et les R, avant toute
  nouvelle série.
- Le paragraphe d'accumulation qui résout : à traiter dans une change à part.

## Décisions de l'auteur (2026-10-19)

1. **P est la référence** pour l'XP modèles (`--override beat_context=plan`).
   Le défaut de production reste `blind` : changer le défaut est une
   décision à part.
2. **L'accumulation qui résout** : une change ultérieure ; non concluant
   pour l'instant.

## La vérification « troisième personne » (après la décision)

Ajoutée à la sélection de P (`fe88b0b` → commit suivant) : aucune marque de
première personne et au moins deux « elle » → −10. Sur toutes les variantes
de beat tirées depuis le 2026-10-18 (scaffold-ablation, beats-see-movement,
plan-state-beats, essais à blanc), la règle sépare sans recouvrement : les
variantes à la troisième personne ont 0 marque de « je » et 2 à 7 « elle » ;
toutes les autres ont au moins une marque de « je ».

**Rejouée sur les trois P, elle ne sauve aucun beat** : là où une variante
est à la troisième personne, les trois le sont (103846 : 9/9 ; 104812 :
découverte 3/3 et doute 3/3 ; 103008 : les gagnants sont déjà en « je »).
Elle signale, elle ne corrige pas. Et E02 (104812, lu « oui ») a sa
découverte et son doute à la troisième personne : la lecture ne l'a pas
relevé. La cause est en amont : la consigne, écrite en « elle », est lue en
dernier dans P.
