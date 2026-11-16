# review-guard — mesure

> Change : `openspec/changes/review-guard`. Une variable : la garde de
> relecture (en-tête rétabli, relecture rejetée si elle ajoute un défaut de
> bornes). Auteur M (`ministral3-14b-q5`), chapitre 7, branche
> `review-guard` `46cb108`, `--no-voice`. Mêmes graines que
> `20261111-measure-prepared-plan` (sans garde).

## Runs

| run | graine | état | durée |
|-----|--------|------|-------|
| `20261116-231819-ch07-anniversaire` | 424242 | error : préflight refusé (corespotlightd 110 %) | 16 s |
| `20261116-231835-ch07-anniversaire` | 171197 | ready | 350 s |
| `20261116-232425-ch07-anniversaire` | 174597 | ready | 366 s |
| `20261116-233047-ch07-anniversaire` | 424242 (reprise du refus) | ready | 356 s |

Le refus est le préflight qui fait son travail ; le run est gardé.

## Garde

- **Entrée 1 : relecture rejetée 3 fois sur 3.** Chaque fois la relecture
  ajoutait une citation et plus de 2 phrases (et plus de 60 mots sur 2 des
  3). Sans garde, la semaine dernière, ces trois défauts arrivaient dans
  `chapitre.md`.
- **En-tête rétabli : 0.** Aucune relecture retenue n'a touché l'en-tête
  cette fois ; les trois relectures qui l'auraient pu sont rejetées.
- Entrée 2 : une relecture rejetée par la garde existante (coupe sous la
  cible, 424242), aucune par la nouvelle.

## Entrée 1 telle que servie (`chapitre.md`)

Toutes : « Samedi 14. Beau temps. », 2 phrases, sans citation.

- **171197** (26 mots) — « L'après-midi, les mains ont tenu le téléphone
  avant même de décider. L'écran a tremblé, les photos alignées comme des
  preuves, toutes à effacer d'un coup sec. » Aucune marque de personne :
  ni « je » ni « elle ».
- **174597** (35 mots) — « Je n'ai pas allumé les bougies du soir. Les
  photos du premier étage, celles avec les cadres en bois clair, restent
  dans le tiroir du meuble de l'entrée, empilées à plat sous les chaussettes
  d'hiver. »
- **424242** (54 mots) — « J'ai tourné la clé dans la serrure sans bruit,
  comme si la maison attendait qu'on lui rappelle son usage. Le cadre doré
  posé sur la table basse — *23 octobre 1987, trois ans déjà* — glisse
  entre mes doigts avant que je ne le range dans le tiroir des souvenirs à
  ne plus voir. » Date et durée inventées (« 1987 », « trois ans ») contre
  neuf ans de mariage : à juger.

## Trouvaille : la réparation linguistique réécrit le français

La réparation (Qwen, « corrige TOUT passage qui n'est pas en français … tu
ne changes NI le sens ») a réécrit le texte gardé :

- 174597 : « J'ai décidé de ne pas allumer les bougies du soir. » →
  « Je n'ai pas allumé les bougies du soir. » — la décision, le sujet de
  l'entrée 1, disparaît ;
- 424242 : « *le 23 octobre 1987, trois ans, déjà* » → « *23 octobre 1987,
  trois ans déjà* ».

Sa garde ne regarde que la longueur. Suite possible (non faite) : ne
réparer que les phrases où le lint trouve de l'anglais, ou rejeter une
réparation qui touche une phrase sans fuite.
