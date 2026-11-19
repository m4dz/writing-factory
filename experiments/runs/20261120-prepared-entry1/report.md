# prepared-entry1 — vraie préparation, vraie reprise

> Chapitre 7, auteur M, spec canonique (entrée 1 `prepared: true`, best-of-6),
> commit b2bb3ac. `factory prepare --chapter 7 --seed 424242`, plan approuvé,
> Entrée au choix du brouillon ; puis `factory generate --from
> 20261120-004421-ch07-prep --seed 424242 --no-voice`. Le 2026-11-20 à 00:44,
> machine non redémarrée (swap 12,6 Go sur 13,3, mais 34 % de mémoire libre,
> charge basse) : rien n'a rampé.

| Étape | Temps | |
|---|---|---|
| Préparation (état narratif, plan, 6 brouillons, choix, relecture entrée 1) | 141 s | `20261120-004421-ch07-prep` |
| Scène (entrée 2 seule) | 292 s | `20261120-004643-ch07-anniversaire`, `ready` |
| Scène sans préparation de l'entrée 1, avant (best-of-3 en scène) | 337–384 s | 7 runs `ready`, 2026-11-11 et 2026-11-16 |

Un seul tirage, machine dans un autre état que les runs d'avant : preuve de
fonctionnement, pas mesure. L'écart (45 à 90 s) est indicatif ; ce qui est
sûr, c'est que les 6 brouillons ne sont plus en scène.

## Ce qui a été vérifié

- La reprise ne fait aucun appel d'écriture pour l'entrée 1 (17 appels : les
  tirages de l'entrée 2, sa relecture, la cohérence Qwen).
- L'entrée 1 du `chapitre.md` est mot pour mot le brouillon retenu.
- Le manifeste de la préparation porte `entry_pick` (variant 5, rang 1) ;
  l'avertissement « best-of-6 préparé — variant 5 choisi par l'auteur »
  passe dans le run repris.

## Les six brouillons (`variants.md`)

| Variant | Score | Défauts |
|---|---|---|
| 5 — retenu | 3 | aucun |
| 3, 6 | −1 | ne pose pas la décision |
| 1, 2, 4 | −13 | cite, ne nomme pas l'effacement |

Un brouillon propre sur six. Trois sur six citent « Ce jour n'aura pas
lieu » : le modèle reprend la phrase du mouvement comme une réplique. Le
retenu a été borné à deux phrases ; la troisième, « La musique supprimée… »,
est tombée, et la relecture de préparation, hors bornes, a été rejetée
(texte d'avant gardé) :

> J'ai décidé de ne pas en faire une journée à elle. Les photos sont
> retournées face contre le mur dans le tiroir du haut, les enveloppes
> froissées une fois encore pour vérifier qu'elles tenaient.

À lire par le propriétaire.
