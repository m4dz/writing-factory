# scaffold-ablation — rapport

> Change : `openspec/changes/scaffold-ablation`. Runs du 2026-10-18, 01:48–04:10,
> commit `8218bb6` ; A3 rejoué 08:53–09:31 (`fd57830`, interrupteur
> `accumulation_enabled`). Verdict : la lecture de l'auteur, à l'aveugle
> (`blind/verdicts.md`), clé ouverte après coup ; la grille n'est qu'un véto.

## Ce qui a tourné

15 runs `ready` (5 bras × 3 graines : 395959, 528559, 781771), entrelacés par
graine. 8 tentatives exclues (`manifest.yaml`, `excluded`) : 7 refus du
préflight (entretien macOS : `mediaanalysisd`, `corespotlightd`,
`mds_stores`), 1 run interrompu par l'opérateur. Aucune génération n'a échoué
une fois le préflight passé.

## Deux défauts de protocole, trouvés à l'exécution

1. **A3 n'est pas une variable.** `micro_nodes=false` coupe l'accumulation,
   mais aussi le glissement, la pose des gestes (dont la chute « Constat :
   anniversaire. ») et le pruning. Les trois entrées A3 n'ont ni chute ni
   glissement. Ces runs sont gardés sous `A3x`, hors lecture. **A3 rejoué**
   avec `--override accumulation_enabled=false` (accumulation seule ; chute
   présente sur 3/3, aucun appel d'accumulation) : entrées E13–E15 du jeu
   à l'aveugle.
2. **L'appariement par graine est partiel.** La graine pilote le tirage du
   glissement, pas l'échantillonnage du modèle (Ollama ne reçoit pas de
   `seed`). Les trois tirages d'un même bras sont donc trois tirages
   indépendants du modèle ; « même graine » ne veut pas dire « même texte de
   départ ». Trois graines restent trois mesures, pas trois paires.

## La grille (entrée 2, texte final)

Table complète : `ablation-table.md`. Après vérification de chaque
correspondance des détecteurs (doctrine 4) :

| bras | résout | présence | récursion | redémarrage | autres | lecture |
|---|---|---|---|---|---|---|
| R — production | 1/3 runs | 1/3 | 1/3 | 1/3 | — | à rendre |
| A1 — sans best-of | 0/3 | 0/3 | 0/3 | **2/3** | — | à rendre |
| A2 — sans pruning | **2/3** (dont un run à 4 « je me souviens maintenant ») | 0/3 | 0/3 | 0/3 | décor interdit 1/3 | à rendre |
| A3 — sans accumulation (rejoué) | 0/3 | 1/3 (« je me souviens l'avoir entendu sonner », vu par le détecteur corrigé seulement) | 0/3 | 0/3 | **170 mots en moyenne** (R : 326) | à rendre |
| A4 — entrée 2 en un appel | 1/3 | 0/3 | 0/3 | 2/3 | litanie la plus haute (0,21), longueur 464 mots en moyenne | à rendre |

Vérification des détecteurs sur les correspondances réelles :

- **Faux positifs** : les deux « congédie » de A4 (« peut-être l'ai-je fait
  sans y penser ») sont l'étape « automatisme » de la trajectoire du brief,
  pas un congé. Retirés du tableau ci-dessus.
- **Redémarrage** : vrais défauts (« Je me suis réveillée ce matin… » dans une
  entrée de NUIT). Mais le score de sélection exempte le premier beat du
  redémarrage — or, au chapitre 7, le premier beat de l'entrée 2 suit déjà
  l'entrée 1. L'exemption laisse passer ce défaut en production (R, A1).
- **Manqué** : « je me souviens maintenant avoir entendu la porte d'entrée se
  fermer » (A2) — un son, donc une présence, que `_BEAT_PRESENCE` ne voit
  pas (il cherche « un bruit », pas « entendu »).
- **Manqué** : « Je décide de relever… » (A4), la doctrine 8 en clair ; aucun
  détecteur de la sélection ne la compte.

## Après correction des détecteurs (`ablation-table-v2.md`)

Mêmes textes, comptés avec les quatre vérifications corrigées (branche
`detector-fixes`). Les runs ont été TIRÉS avec l'ancienne sélection ; seul
le comptage change.

| bras | « je décide de » dans l'entrée 2, par run |
|---|---|
| R, A1, A2, A3 (beats) | 0, 0, 0 |
| A4 (un appel) | **1, 8, 7** |

Le reste bouge peu : les deux « congédie » de A4 disparaissent (faux
positifs), A3 gagne une présence perçue réelle.

## La lecture de l'auteur (à l'aveugle, clé ouverte après)

Mouvement déclaré accompli ? Par graine (395959 · 528559 · 781771) :

| bras | 395959 | 528559 | 781771 | oui / partiel / non |
|---|---|---|---|---|
| R — production | non (E07) | partiel (E08) | non (E06) | 0 / 1 / 2 |
| A1 — sans best-of | partiel (E12) | partiel (E11) | non (E10) | 0 / 2 / 1 |
| A2 — sans pruning | non (E02) | partiel (E09) | non (E05) | 0 / 1 / 2 |
| A3 — sans accumulation | non (E15) | non (E14) | non (E13) | 0 / 0 / 3 |
| A4 — entrée 2 en un appel | non (E04) | **oui** (E03) | **oui** (E01) | **2** / 0 / 1 |

Les deux seuls « oui » de la série sont A4. E03 : « un des meilleurs tirages
[…] la construction est claire et la progression de la tension évidente ».
E01 : « oui ; aucun détail, aucune tension, froide énumération ». E04, le
plus long (624 mots) : « on a de la densité, mais le ton sonne creux […] le
personnage ne tient pas son rôle ».

La production elle-même n'accomplit le mouvement sur aucune graine.

Motif récurrent des notes, hors A4 : **l'invention**. « le texte invente des
narratifs » (E06, R), « externalités qui ne peuvent avoir lieu » (E08, R),
« Huit couverts ce soir. » (E09, A2), « le reste est inventé » (E10, A1),
« incohérences et inventions » (E14, A3), « incohérent » (E05, A2). Aucune
note d'invention sur A4. Hypothèse, pas constat : chaque beat est servi
seul, sans le mouvement entier (`_prompt_beat`) ; le modèle comble ce qu'il
ne voit pas.

## Décision par pièce (règle écrite avant les runs)

Règle : **retirable** si la lecture n'est pas pire que R sur ≥ 2 graines ET
qu'aucun défaut de véto absent de R n'apparaît ; **porteuse** si le bras
montre le défaut contre lequel la pièce a été construite sur ≥ 2 graines.
Liste de véto écrite avant les runs : résout, congédie, redémarre,
présence, récursion, décor interdit.

- **Best-of (A1) : retirable.** Pas pire que R sur 3/3 (mieux sur 395959).
  Seul défaut de véto : le redémarrage, que R a aussi.
- **Pruning (A2) : porteur.** Résolution sur 2/3 (le défaut contre lequel il
  a été construit) et décor interdit sur 1, absent de R. La lecture est
  égale à R sur 3/3 : il ne gâche rien.
- **Accumulation (A3) : retirable à la lettre, à ne pas retirer.** Pas pire
  que R sur 2/3 — mais seulement parce que R est « non » sur ces deux
  graines : effet plancher. Pire sur 528559. Trois « non », « pas de
  densité », « pas de profondeur », et la moitié de la masse de l'entrée en
  moins (170 mots contre 326). La règle ne voit pas la densité ; c'est son
  angle mort, pas un acquittement.
- **Beats plafonnés par le code (A4) : retirables selon la règle.** Mieux que
  R sur 2/3, égal sur la troisième ; aucun défaut de véto absent de R
  (résolution, présence, redémarrage : R les a ; les deux « congédie » sont
  des faux positifs).

**Ce que j'avais écrit avant la lecture est faux.** J'avais déclaré les
beats porteurs sur la doctrine 8 (« je décide de » : 1, 8, 7 dans A4, 0
ailleurs). La doctrine 8 n'était pas dans la liste de véto écrite avant les
runs : l'y ajouter après coup déplacerait le but. Et la lecture contredit
le compte : E03, le meilleur tirage de la série, porte 8 « je décide de ».
La doctrine 8 reste un défaut à mesurer — c'est peut-être les
« automatismes » que la note d'E03 relève —, pas un véto rétroactif.

## A4 n'est pas une pièce, c'est un paquet

`strategy: single` ne retire pas que le découpage. Pour l'entrée 2, A4 :
sert le mouvement entier (`_movement_prompt`) au lieu de beats aveugles ;
n'a ni best-of ni plafond de phrases ; **n'est pas élagué** (`assemble_node`
ne nettoie que les entrées en beats) ; **sert le squelette de voix avec le
verdict et le couperet** (amputés seulement dans les beats, correctif C5) ;
ne sert pas le suffixe de véto des beats (« aucune voix, aucun bruit… »).
Les deux « oui » ne disent pas laquelle de ces différences compte. Et le
squelette de verdict servi n'a donné qu'une résolution sur trois, comme R :
le constat C5 (12/12 tiennent sans lui) ne se retrouve pas dans le pipeline
complet.

## Ce que la série dit, au-delà des pièces

1. **L'échafaudage actuel de l'entrée 2 ne livre pas le mouvement.** R : 0
   oui sur 3. Retirer une pièce ne le fait pas basculer, sauf les beats.
2. **Le découpage en beats servis seuls est le suspect principal** : il
   coïncide avec les inventions, et l'appel unique, qui voit tout le
   mouvement, donne les deux seuls « oui ». C'est la question que
   `storyboard-density` doit poser autrement : des beats qui voient le
   mouvement entier et la matière de chaque action, pas des beats aveugles.
3. **Densité et justesse ne vont pas ensemble chez nemo, telles quelles** :
   le tirage le plus dense (E04) est un contre-sens ; le plus juste avec
   tension (E03) est à 438 mots ; E01 est juste et froid.
4. **Trois graines.** Deux « oui » sur trois tirages n'est pas un taux ; c'est
   assez pour retourner une présomption, pas pour la remplacer.

## Temps

Non interprétable (doctrine 5) : le premier run a calé ~9 min sur un appel à
0,4 tok/s sous pression mémoire (swap 15,8/16,4 Go, navigateur ~13 Go
résident). Les autres runs : 6 à 12 min. Le temps n'est pas un critère.

## À faire

1. ~~Lecture à l'aveugle~~ rendue.
2. Proposition d'ADR : `adr-proposal.md` (à l'auteur de décider ; aucun
   changement de `chapters/07-anniversaire/spec.yaml` sans son go).
3. Journal : `experiments/journal/20261018T*-scaffold-ablation.md`.
4. Branche `detector-fixes` (af17580) : à fusionner avant
   `storyboard-density`. La vérification doctrine 8 y pénalise « je décide
   de » dans la sélection — à rediscuter au vu d'E03 (score, pas véto ?).
