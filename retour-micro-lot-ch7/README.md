# L'Involontaire — micro-lot pré-répétition et première génération du chapitre 7

Suite de `retour-session-7`. Sept corrections de consignes et de lints (la bible
n'a pas bougé, rien n'a été réindexé), puis **la première génération du
chapitre 7 en conditions réelles, chronométrée bout à bout**.

## Le chiffre

```
génération   297 s
voix clonée  157 s
─────────────────
TOTAL        454 s = 7,6 min       marge sur 28' : 20,4 min
```

Zéro seconde de veille, machine branchée, horloges de mur et de calcul
coïncidentes. Audio à 92,5 s pour une cible de 90 (tolérance 15). Débit du clone
mesuré à 173,9 mots/min contre 177 supposés — 1,8 % d'écart.

⚠ Facteur temps réel **0,60×**, contre 1,55 en référence : le moteur vocal était
**froid**. Préchauffer avant la scène.

## Contenu

| Fichier | Rôle |
|---|---|
| `SYNTHESE.md` | La note : les six tirages et leurs six causes, les trois lignes que le code a reprises au modèle, ce que la lecture doit trancher. **C'est le document à lire.** |
| `grille-lint-chapitre-7.md` | Grille du chapitre. Lignes AUTO remplies, MANUEL vides. |
| `runs/run-CH7.md` | Le tirage retenu, texte intact. |
| `runs/chapitre-7.md` | Le chapitre assemblé, avec sa bascule et sa borne d'audio. |
| `ecartes/` | Les cinq tirages écartés, un par cause. Rien ne se jette. |
| `rapports/chronometrage.json` | La fiche complète. |
| `rapports/lancement-*.log` | Un journal par tirage : préflights, déchargements, durées. |
| `rapports/diff-de-cablage.txt` | Décompte par fichier. |

## Ce qui tient, et ce qui ne tient pas

**Tient** : deux entrées du même jour, bascule avant le second en-tête, citation
d'ancre verbatim une seule fois, chute en dernière ligne, glissement sur la seule
entrée qui en prévoit un, aucun interdit matériel, aucune citation fabriquée,
aucune troisième personne.

**Ne tient pas** : le couperet paraphrasé (« le coup de couteau »), un verdict
emprunté au chapitre 3, l'entrée d'ouverture à sept phrases là où le brief en
demande deux, et l'entrée de nuit à 271 mots contre 450-600.

## Avertissement de lecture

Archive **SURFACE**, passée au lint fichier par fichier : aucun marqueur profond,
aucun prénom, aucune source firewallée. Deux champs de frontmatter (`plan`,
`coherence`) ont été retirés des runs — ils recopiaient le brief et les faits
dérivés. **Les textes générés sont intacts.**

Le lint a d'ailleurs trouvé une fuite réelle en préparant cette archive : le
brief machine du chapitre 7 nommait un fichier de la couche cachée, et ce brief
est servi au modèle auteur. Fermé au service, gardé par une assertion.
