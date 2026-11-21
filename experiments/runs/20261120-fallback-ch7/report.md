# Chapitre de repli (7.3) — trois candidats

> 2026-11-20, main 6e62a2c, auteur M. Une préparation réelle
> (`20261120-010038-ch07-prep`, plan approuvé, Entrée au choix : variant 1,
> 3 brouillons propres sur 6), puis trois reprises voix active, graine
> aléatoire. Prép 135 s ; scènes 282 / 286 / 279 s.

| Run | Graine | Mots (lint) | Lecture |
|---|---|---|---|
| A `20261120-010302` | 336073 | 528 [OK] | 127 s, 232 mots/min |
| B `20261120-010749` | 438604 | 346 [HORS CIBLE] | 86 s, 216 mots/min |
| C `20261120-011241` | 289920 | 259 [HORS CIBLE] | 68 s, 196 mots/min |

Même entrée 1 pour les trois (préparée) : « J'ai décidé que ce jour n'aurait
pas lieu. Pas d'albums ouverts sur la table basse, pas de mélodies choisies
pour traverser l'après-midi sans la voir. » Les trois finissent sur
« Constat : anniversaire. »

## La voix était cassée

Les trois runs ont fini `ready` sans `chapitre.wav` : macOS 27 refuse de
charger scipy 1.15.3 (`section '__DATA/__thread_bss' has a zero-fill section
type, but offset field is not zero`), dernière version pour Python 3.10.
`factory doctor` ne le voit pas (il importe `mlx_audio`, pas le modèle).
Aucun run voix depuis la mise à jour de macOS (2026-10-19) : tout était en
`--no-voice`.

Les `chapitre.wav` présents ont été rendus APRÈS les runs, par
`factory.infra.tts.render_chapter` dans un venv jetable Python 3.12
(scipy 1.18.1, mêmes mlx 0.32.4 / mlx-audio 0.5.9 / transformers 5.20.1) :
`voice-py312.log`. Le manifeste de chaque run garde `audio: null`.

Débit 196–232 mots/min contre 177 consignés : à écouter.

## Choix

2026-11-21 : le propriétaire retient **A**. `chapitre.md` et `chapitre.wav`
copiés dans le deck (`public/fallback/`, talk e70c7e1), les marques de gras
de « sauf une, une seule » retirées (le deck affiche du texte, pas du
Markdown). `plan.md` inchangé (identique à celui de la préparation).
