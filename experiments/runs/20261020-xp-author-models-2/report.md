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

Prêt, 592 s (nemo ~360 s). Récitation 1/9, aucune retenue ; pas de troisième
personne ; deux « présence perçue » tirées, aucune retenue, mais l'entrée 2
finit sur « La playlist s'est lancée seule ». Entrée 2 : 215 mots. Entrée 1 :
s'ouvre en citant une phrase de consigne (« Elle efface l'anniversaire —
range les photos… ») puis la commente.

## Résultats

Neuf runs, tous prêts ; aucun tué par la garde, aucun exclu.

| graine | bras | temps (s) | récitent | 3ᵉ pers. tirées | 3ᵉ pers. retenues | mots entrée 2 | phrases courtes | autres défauts tirés |
|---|---|---|---|---|---|---|---|---|
| 731667 | N | 334 | 6/9 | 0 | — | 350 | 7/25 | décide ×5 |
| 731667 | M | 357 | 4/9 | 8 | découverte, doute | 229 | 9/25 | présence perçue ×1 |
| 731667 | S | 570 | 1/9 | 2 | — | 178 | 8/23 | décor interdit ×1 |
| 139026 | N | 331 | 7/9 | 7 | découverte, doute | 227 | 6/20 | — |
| 139026 | M | 371 | 1/9 | 2 | — | 400 | 8/24 | recopie ×2 |
| 139026 | S | 561 | 1/9 | 2 | — | 171 | 12/24 | présence perçue ×1 |
| 487914 | N | 371 | 8/9 | 8 | découverte, doute | 490 | 9/40 | — |
| 487914 | M | 366 | 1/9 | 2 | — | 222 | 16/29 | — |
| 487914 | S | 554 | 1/9 | 1 | — | 240 | 11/21 | — |

Moyennes : temps N 345 s, M 365 s (×1,06), S 562 s (×1,63) ; mots de
l'entrée 2 N 356, M 284, S 196.

Hors lecture (l'entrée 2 seule est lue) :

- **Entrée 1 en « elle ».** S récite la consigne de l'entrée 1 dans les trois
  runs (« Elle a effacé l'anniversaire, rangé les photos… » ; « « Elle efface
  l'anniversaire — … » Le texte dit vrai »), M dans un (« Elle a posé le
  stylo… »). nemo jamais ; un nemo écrit l'entrée 1 au masculin (« plus en
  être entouré »). La sélection ne regarde que les temps de l'entrée 2.
- **Fond profond ?** S, 487914, entrée 1 : « La maison est vide. Elle est
  partie. Je l'ai noté. » — à vérifier par l'auteur contre `bible/profond/`.
- **Citation recopiée en italique** (Markdown) après la citation servie : M,
  deux runs sur trois, réécrite (« que j'ai dit oui. Deux couverts, cette
  fois. »).
- S retenu à « --- » en tête de l'entrée 1 (une règle Markdown), un run.

### Prédictions (hors lecture)

- **P1** confirmée : M 4, 1, 1 et S 1, 1, 1 contre N 6, 7, 8.
- **P3** confirmée : S ×1,63.
- **P4** confirmée : aucun run tué par la garde.
- **P2** : en attente de la lecture.

### Lecture aveugle

`blind/E01–E09.md`, entrée 2 de chaque run, clé fermée dans
`blind-key.yaml`. Non tout à fait aveugle : la longueur, l'italique Markdown,
la troisième personne retenue peuvent trahir un bras.

Verdicts rendus le 2026-11-10 (`blind/verdicts.md`), clé ouverte ensuite.

| graine | N | M | S |
|---|---|---|---|
| 731667 | E07 oui — fuite (« Je rentre à la maison à 19h30 »), pas de personnalité, densité faible | E09 oui — ton très bon, densité faible | E08 partiel — doute sans profondeur, pas de personnalité, densité faible |
| 139026 | E03 partiel — une partie du mouvement, pas de ton | E06 oui — pas de tension, erreurs temporelles, densité OK, manque de personnalité | E01 non — pas de mouvement, ton neutre |
| 487914 | E02 partiel — le ton tient à l'avant-dernier paragraphe, deux fuites | E05 oui — ton parfait, vraie personnalité, densité faible | E04 oui — une fuite (« Retour à la maison »), densité faible, manque de personnalité |

Comparaison graine contre graine, oui > partiel > non, les notes départageant
à grade égal (lecture confirmée par l'auteur le 2026-11-10) :

- **M contre N** : mieux sur 731667 (même grade, ton contre fuite), mieux sur
  139026 et 487914 (oui contre partiel). Au moins égal sur 3, pire sur
  aucune.
- **S contre N** : pire sur 731667 (partiel contre oui) et 139026 (non contre
  partiel), mieux sur 487914.

Fuites relevées par l'auteur (consigne recopiée en clair) : N 3 (E02 ×2,
E07), S 1 (E04), M 0 — dans le sens de P1.

Fuite de canon : aucun 4-gramme de `bible/profond/` dans les neuf chapitres
hors le texte servi (`prompts.md` du run ; la citation [CIT-2] est servie et
figure aussi dans `citations-cahier.md`). « La maison est vide. Elle est
partie. » (S, 487914, entrée 1) n'est pas lexical ; S est écarté.

## La règle

- **M remplace N** : au moins égal sur 3 graines, pire sur aucune.
- **S est écarté** : pire que N sur 2 graines.
- **P2 réfutée** : S n'est au moins égal à N que sur une graine.

Décision : **W = M** (`xp-ministral3-14b-q5`), auteur de scène et de livre.
365 s par chapitre, dans le budget de 25 min. Confirmée par l'auteur le
2026-11-10.

### Ce que la décision emporte

- **Entrée 1 en « elle ».** M, graine 487914 (le run de E05, le meilleur
  tirage de l'entrée 2) ouvre l'entrée 1 par une citation à la troisième
  personne (« « Elle a posé le stylo… » »). L'entrée 1 ne doit ni citer ni
  quitter le « je », et c'est celle que le locuteur lit en direct. Cause : la
  matière servie de l'entrée 1 est écrite à la troisième personne
  (`chapters/07-anniversaire/spec.yaml`), et la sélection ne regarde que les
  temps de l'entrée 2. Correctif décidé (A + B) : l'auteur réécrit la matière
  de l'entrée 1 à la première personne ; le code tire l'entrée 1 en best-of
  avec les contrôles de personne et de citation. Changes séparés.
- **Troisième personne retenue.** M, graine 731667, retient découverte et
  doute à la troisième personne, comme N sur 139026 et 487914 : la lecture
  l'a passée (E09 « oui »), elle reste un défaut à suivre.
- **Italique Markdown** sur la citation recopiée (M, 2 runs sur 3) : à
  nettoyer par le code (`delint`) avant la scène.
- **Densité faible** sur 7 des 9 entrées, tous bras : la variable suivante
  (`storyboard-density`, après le 4 décembre).
- ADR remplaçant le choix d'auteur d'ADR-0008 ; contrôle du mode acteur avec
  M.
