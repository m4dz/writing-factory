# entry1-decision — mesure

> Change : `openspec/changes/entry1-decision`. Auteur M
> (`ministral3-14b-q5`), chapitre 7, branche `entry1-decision` `9b4ac4e`,
> `--no-voice`, spec variante `spec.yaml` (= spec canonique + la liste
> `best_of.decision` de l'entrée 1, rien d'autre). Mêmes graines que la
> lecture du 2026-11-16 (`20261116-review-guard`).

## 1. Tirages bruts (avant tout bornage)

24 tirages de l'entrée 1 sur le prompt servi par main (`raw-a.json`,
`raw-b.json`, `draw.py`) :

- 4 à 7 phrases, 70 à 99 mots ; un geste d'effacement par phrase. Le
  budget (136 tokens) arrête 16 tirages sur 24. Jamais deux phrases.
- 9 sur 24 s'ouvrent sur « « J'ai décidé … » » : la ligne de la narratrice
  habillée en citation ; 7 portent la décision. Tous rejetés par le contrôle
  « cite ».
- `names-erasure` : 7 sur 12 du premier lot à +3 « propre » — nommer les
  photos suffit, le premier tirage gagne.

Règles rejouées sur ces 24 tirages, par groupes de trois comme le pipeline
(`sim.py`) — groupes sur 8 dont l'entrée servie pose la décision :

| règle | groupes |
|-------|---------|
| actuelle (deux premières phrases) | 0 |
| + guillemets d'ouverture retirés | 3 |
| + décision au score | 5 |
| + mot du jour refusé | 5 (un autre gagnant, sans « anniversaire ») |
| best-of-6 (groupes de six) | 4 sur 4 |

La meilleure paire de phrases consécutives au lieu des deux premières
(`sim_window.py`) : 6/8 propres, comme les deux premières. Rien gagné,
abandonné.

## 2. Runs

| run | graine | état | durée |
|-----|--------|------|-------|
| `20261119-014502` `-014513` `-014523` | 424242, 171197, 174597 | error : préflight refusé (mediaanalysisd 166 %) | ~10 s |
| `20261119-015227` | 424242 | error : préflight refusé (corespotlightd 117 %) | 10 s |
| `20261119-015237-ch07-anniversaire` | 171197 | ready | 335 s |
| `20261119-015812-ch07-anniversaire` | 174597 | ready | 330 s |
| `20261119-020704-ch07-anniversaire` | 424242 | ready | 324 s |

Le prompt servi de l'entrée 1 est identique octet par octet à celui du
2026-11-16.

## 3. Entrée 1 telle que servie (`chapitre.md`)

Les trois variants de chaque run sont dans `variants.md` (nouveau).

- **171197** — « J'ai posé le couteau sur le comptoir sans le laver. Les
  lames étaient encore tachées de sauce, le plat des grandes occasions
  n'était même pas sorti de son tiroir. » Retenu à −1 (« ne pose pas la
  décision ») : aucun des trois ne la pose dans ses deux phrases ; dans le
  retenu, elle était en phrase 3 (« La décision s'est … », coupée).
- **174597** — « Les photos dans l'armoire à double battant, les albums
  serrés côte à côte entre les chemises de lin, leurs dos en tissu vert
  défraîchi. La musique coupée sur le téléviseur, le silence épais comme une
  nappe étalée sur les haut-parleurs. » Retenu à −1 ; aucun des trois ne
  pose la décision. Sans « je ».
- **424242** — « J'ai décidé de ne rien faire. Plus de musique, les
  playlists supprimées avant que le geste ne devienne un réflexe. » Retenu
  à +3, propre. Avec la règle d'avant, le variant 1 (« J'ai posé
  l'invitation dans la corbeille sans la lire. Les photos sont rangées … »)
  gagnait à égalité.

**1 sur 3 pose la décision.** La sélection a choisi la décision chaque fois
qu'un tirage la portait (1 run) ; dans les deux autres, aucun des trois
tirages ne la portait dans ses deux phrases. Aucune ouverture entre
guillemets dans ces 9 tirages (9 sur 24 dans les lots bruts) : la variance
d'un lot de 3 est large. Sur 33 tirages au total, 9 posent la décision dans
les deux phrases servies (~27 %, défauts mis à part) : au moins un sur 3
tirages ≈ 61 %, sur 6 ≈ 85 %.

Relecture : rejetée par la garde sur les trois (citation, plus de deux
phrases, plus de 60 mots), comme le 2026-11-16.

## 4. Lecture

Le code fait ce qu'il dit : la décision gagne quand elle est tirée. Ce qui
manque, c'est qu'elle soit tirée : M écrit une liste de gestes, la décision
n'est qu'une des ouvertures possibles. Le best-of ne fabrique pas ce que le
modèle n'écrit pas.

Leviers, au propriétaire :

1. `n: 6` pour l'entrée 1 (~+100 s sur scène) : ~85 % au lieu de ~61 %.
2. La phrase servie : le mouvement (« Deux phrases, la porte fermée : elle
   efface l'anniversaire — range les photos … ») est à la troisième personne
   et ne nomme pas la décision ; la matière la nomme (« Décision de
   l'après-midi : ce jour n'aura pas lieu »). Texte du propriétaire.
3. Entrée 1 préparée la veille avec le plan (le propriétaire choisit parmi
   N), au lieu d'être tirée sur scène : décision de mise en scène, pas de
   code.
