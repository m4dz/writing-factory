# Mesure prepared-plan §6 + lecture entrée 1 (M) — rapport

> Changes : `openspec/changes/prepared-plan` (§6, mesure machine réelle) et
> `openspec/changes/entry1-notebook-checks` (tâche 3, lecture de l'entrée 1).
> Auteur M (`ministral3-14b-q5`, ADR-0029), chapitre 7, main `7eaea07`,
> `--no-voice`. Dossier de runs à part (`--runs-dir` ici) : `prepared:
> "latest"` ne lit que le niveau supérieur de `experiments/runs/`, cette
> préparation ne peut pas être reprise sur scène. Approuvée au nom du
> propriétaire (go du 2026-11-11), retirée de fait : la spec du chapitre 7
> change avec `stage_plan`, l'empreinte la refuserait.

## Runs

| run | rôle | graine | durée |
|-----|------|--------|-------|
| `20261111-014724-ch07-prep` | préparation, approuvée | 460930 | 12 s |
| `20261111-014735-ch07-anniversaire` | reprise, graine imposée | 424242 | 385 s |
| `20261111-015400-ch07-anniversaire` | reprise, graine tirée | 171197 | 339 s |
| `20261111-015939-ch07-anniversaire` | reprise, graine tirée | 174597 | 361 s |
| `20261111-020540-ch07-anniversaire` | run non scindé (témoin) | 424242 | 338 s |

Durées : `timings.log` (horloge murale du processus) ; aucun sommeil
(`sleep_s: 0.0`). Préflight : 0,35 Go de swap libre sur 10 Go.

## prepared-plan §6

- **Temps gagné : ~12 s.** La préparation du chapitre 7 = préflight (9 s) +
  état narratif inchangé (1 s) + plan imposé (aucun appel modèle). Ce que la
  scène gagne n'est pas du temps : c'est un plan relu et approuvé, et
  l'empreinte. Un chapitre à plan généré gagnerait l'appel `plan` en plus.
- **Taille des checkpoints.** Préparation : 192 Ko. Run complet : 704–832 Ko.
- **Prompts servis, reprise contre témoin (même graine 424242).** Appels 1 à
  6 identiques octet par octet (corps system + user ; seul l'en-tête de
  l'appel diffère : `wall_s`). L'appel 7 diffère par une réponse du modèle
  réinjectée (variante d'un beat précédent) : Ollama n'est pas déterministe
  à graine égale sur cette machine. La scission ne change rien à ce qui est
  servi ; l'égalité de bout en bout reste prouvée au modèle factice (tests).

## Entrée 1 — sélection (avant relecture)

Le best-of + contrôles carnet retiennent, tel que servi à la relecture :

- **424242 (reprise)** — « J'ai retiré le cadre du miroir du salon avant le
  déjeuner, les deux photos fixées au dos avec du ruban adhésif depuis le
  printemps dernier. Elles sont maintenant dans le troisième tiroir de la
  commode, sous les chaussettes de laine, pliées en quatre avec leur bord
  déchiré par le scotch. »
- **171197** — « « Je n'ai pas sorti le service à vin des grands jours. » À
  la place, la vaisselle de tous les jours, celle qui ne porte pas
  d'histoire : assiettes sans relief, couverts sans gravure. » (cite ; les
  variants de l'entrée 1 ne sont pas enregistrés dans `variants.md`, on ne
  sait pas si les trois citaient)
- **174597** — « J'ai repéré les photos avant midi : trois albums posés sur
  l'étagère du salon, les coins encore marqués par les doigts. Le premier
  geste fut de soulever le couvercle du plus épais — celui avec les pages
  collées aux angles —, puis de le reposer sans l'ouvrir. »
- **424242 (témoin)** — « J'ai noté l'après-midi : *ce jour n'aura pas
  lieu*. La décision s'est posée comme une évidence, sans hésitation, comme
  un objet posé sur la table qui n'aurait pas besoin d'être regardé pour
  exister. »

3 sur 4 : première personne, deux phrases, sans citation.

## Entrée 1 — après relecture : la relecture la défait

La relecture (M, température 0,5, « RÉÉCRIS INTÉGRALEMENT … resserrer »)
reçoit l'entrée sans ses bornes (`sentences_max: 2`, `citation: ""`) et :

- **allonge** : 424242 (reprise) passe de 2 phrases à 11 paragraphes, dont
  des faits contradictoires (« Les photos ne sont pas dans le tiroir. Elles
  sont toujours sur la table de nuit. ») ; 171197 et le témoin, de 2 phrases
  à 3 et 2 paragraphes ;
- **met entre guillemets** la première phrase (424242 reprise, témoin) ;
- **change l'en-tête** : « Ciel dégagé. » (174597), « Ciel blanc. » (témoin)
  au lieu de « Beau temps. ».

Seule 174597 sort à peu près bornée (3 phrases, sans citation). Les contrôles
d'`entry1-notebook-checks` agissent à la sélection, avant la relecture : ils
ne voient pas ce défaut. La lecture de l'entrée 1 sur `chapitre.md` mesure
donc la relecture, pas la sélection.

## Suite proposée (non faite, attend un go)

Garde de relecture pour les entrées bornées : l'en-tête réimposé par le code
après relecture, et une entrée qui sort de ses bornes (phrases, mots,
citation, troisième personne) garde son texte d'avant relecture — ou pas de
relecture pour une entrée à `sentences_max`. Une variable, à mesurer sur 3
graines.
