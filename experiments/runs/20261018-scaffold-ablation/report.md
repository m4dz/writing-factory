# scaffold-ablation — rapport provisoire

> Change : `openspec/changes/scaffold-ablation`. Runs du 2026-10-18, 01:48–04:10,
> commit `8218bb6`. **Provisoire** : le verdict de chaque bras est la lecture
> debout de l'auteur, à l'aveugle (`blind/`), pas encore rendue. Ce qui suit
> est la grille en véto et ce qu'elle permet de dire honnêtement.

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
   glissement. A3 est retiré de la lecture à l'aveugle et doit être rejoué
   avec un interrupteur propre à l'accumulation (à écrire : un override
   `accumulation_enabled`).
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
| A3 — invalide | — | — | — | — | — | retiré |
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

## Ce que la grille permet de dire, et pas plus

Règle écrite avant les runs : une pièce est **porteuse** si son bras montre le
défaut contre lequel elle a été construite sur 2 graines sur 3 ; **retirable**
si la lecture de l'auteur n'est pas pire que R sur 2 sur 3 ET qu'aucun défaut
de véto absent de R n'apparaît.

- **Pruning (A2) : porteur selon la grille.** Résolution sur 2/3 sans lui,
  dont la litanie de résolutions la plus nette de la série. La lecture peut
  encore nuancer, pas renverser un défaut de véto.
- **Best-of (A1) : candidat au retrait, sous condition de lecture.** Aucun
  défaut de résolution, présence ou récursion sur 3/3 ; mais redémarrage
  2/3 — défaut que R a aussi (1/3) et que la sélection ne combat pas au
  premier beat. Trancher demande la lecture.
- **Beats plafonnés par le code (A4) : non tranché.** Plus long et plus
  litanique, une résolution, la doctrine 8 qui revient. La lecture dira si la
  longueur gagnée porte quelque chose.
- **Accumulation (A3) : à rejouer.**

Rappel : la production elle-même (R) laisse passer une résolution, une
présence et une récursion sur une graine sur trois. L'échafaudage actuel
n'est pas étanche.

## Temps

Non interprétable (doctrine 5) : le premier run a calé ~9 min sur un appel à
0,4 tok/s sous pression mémoire (swap 15,8/16,4 Go, navigateur ~13 Go
résident). Les autres runs : 6 à 12 min. Le temps n'est pas un critère.

## À faire

1. Lecture à l'aveugle : `blind/E01.md` … `E12.md`, verdicts dans
   `blind/verdicts.md` ; la clé (`blind-key.yaml`) n'est à ouvrir qu'après.
2. Rejouer A3 avec un interrupteur limité à l'accumulation (3 runs).
3. Instruments, avant `storyboard-density` : présence par la perception
   (« entendu », « j'entends »), doctrine 8 (« je décide de ») dans la
   sélection, redémarrage au premier beat quand l'entrée n'est pas la
   première du jour, et l'exclusion « automatisme » du congé.
4. Journal : un fichier par cause pour les défauts ci-dessus, après lecture.
