# Le pipeline LangGraph, pour qui travaille le style

Document de passation vers la conversation d'assistance stylistique. Il décrit
la machine telle qu'elle est au 2026-08-10, pas telle qu'on la voudrait.

**Ce qu'il faut savoir avant tout le reste : la fiche de style n'est PAS dans le
pipeline.** Les trois sessions de calibration (scène test, puis chapitre 2) ont
frappé Ollama en direct, la fiche entière en prompt système via un Modelfile,
sans passer par LangGraph ni par le RAG. Le graphe décrit ci-dessous tourne
aujourd'hui avec un préambule codé en dur qui **contredit la fiche v3** (§ 4).
Tout ce qui suit sert donc à préparer le câblage, pas à documenter un existant.

---

## 1. Forme du graphe

Séquentiel, avec une seule boucle. Le contrôle de flux est déterministe ; la
créativité est déléguée au modèle à chaque nœud.

```
START → plan → write ⟲ (une passe par scène) → review → repair → coherence → END
```

`write` boucle sur lui-même tant qu'il reste des scènes au plan
(`route_after_write`). Tous les autres liens sont fixes. Il n'existe **aucune
boucle de reprise sur la prose** : ni le lint, ni la relecture, ni la cohérence
ne peuvent renvoyer une scène à la réécriture. Ce qui est écrit est écrit.

L'état partagé (`ChapterState`) porte : `brief`, `characters`, `facts`, `plan`,
`plan_report`, `idx`, `scenes`, `reviewed`, `repaired`, `coherence`, `metrics`,
`warnings`.

## 2. Les appels au modèle, nœud par nœud

Deux modèles, jamais chauds ensemble (13 GB + 4,8 GB = 17,8 sur 19,3 disponibles,
c'est la pression qui a fait paniquer la machine). Chaque bascule décharge le
précédent.

| Nœud | Modèle | T | `num_predict` | Reçoit |
|---|---|---|---|---|
| `derive_facts` (dans `plan`) | Qwen 2.5 7B | 0.1 | 400 | fiches des personnages |
| `plan` | mistral-nemo 12B Q8 | **0.5** | 500 | brief + invariants en contrainte |
| `check_plan` (dans `plan`) | Qwen | 0.0-0.1 | 8 à 500 | faits + beats |
| `write` (×N scènes) | nemo | **0.7** | 1400 | plan annoté + 2 dernières scènes |
| `review` (×N scènes) | nemo | **0.5** | adaptatif 1200-2000 | une scène à la fois |
| `repair` (×N scènes) | Qwen | 0.2 | adaptatif | une scène à la fois |
| `coherence` | Qwen | 0.0 | 8 à 400 | questions + scène par scène |

`num_ctx` = 8192 partout. `FRENCH_GUARD` (une consigne anti-code-switching) est
préfixé à **tout** prompt système, y compris ceux des sessions de calibration —
c'est ce qui les rend comparables.

Deux garde-fous de volume, à connaître parce qu'ils peuvent **annuler
silencieusement** un travail de style : `review` et `repair` conservent
l'original si leur sortie fait moins de **60 %** des mots de l'entrée. Une
réécriture qui resserre fort est donc rejetée en bloc.

## 3. Ce que chaque nœud fait au texte

**`plan`** — dérive d'abord les invariants de la bible (Qwen), planifie sous
cette contrainte (nemo), puis confronte le plan aux faits *avant* d'écrire. Une
replanification au plus (`MAX_PLAN_ATTEMPTS = 2`). Le plan passe au lint comme
la prose : un token collé dans un beat contaminerait le prompt d'écriture.

Le prompt demande littéralement « un plan de **3 ou 4 scènes** MAXIMUM », une
ligne par scène, au format `[lieu] ce qui se passe — l'état NOUVEAU à la fin`.

**`write`** — reçoit le plan complet avec sa position marquée (`[fait]` / `>>` /
`[à venir]`) et les **deux dernières scènes en entier**. Consigne : « Écris
UNIQUEMENT la scène N (~600 mots) ». Les scènes précédentes ne sont
délibérément **pas** injectées par le RAG (`include_scenes=False`) : le modèle
recopiait une scène présente dans son contexte au lieu de s'en servir de toile
de fond.

**`review`** — réécriture intégrale, scène par scène, à T=0.5. Consigne :
resserrer, supprimer les répétitions, « garde EXACTEMENT la voix des
personnages et les faits ».

**`repair`** — Qwen réécrit les fuites d'anglais de nemo sans toucher au sens.
C'est ici qu'a lieu l'unique bascule de modèle du pipeline.

**`coherence`** — protocole en trois temps, né de trois échecs : les faits sont
convertis en **questions d'événement dont le OUI vaut violation**, posées
**scène par scène** ; chaque OUI doit citer le texte, et le code vérifie que la
citation s'y trouve vraiment ; chaque OUI subit enfin un contre-appel isolé.
Leçon générale, réutilisable : on donne au petit modèle une tâche de **lecture**,
jamais d'**inférence**.

**Amputation.** Ollama ne signale une génération coupée que par
`done_reason: "length"`. `_generate_whole` demande une continuation (une seule),
recolle en retirant le chevauchement au caractère près, et en dernier filet
coupe à la dernière phrase complète. nemo émet parfois son EOS **en pleine
phrase** hors de toute troncature — le filet sert aussi à ça.

## 4. Le prompt système, et la contradiction à traiter

`assemble_system_prompt` (retrieval.py) construit le prompt système de `plan`,
`write` et `review`. Il empile, dans cet ordre :

1. **Un préambule codé en dur** ;
2. les chunks des personnages présents, récupérés par **id déterministe** (voix,
   état narratif courant, psychologie — 3 des 7 chunks d'une fiche) ;
3. le lieu, récupéré par **similarité sémantique** (top-1) ;
4. optionnellement les scènes précédentes (désactivé pour `write` et `review`).

Le préambule dit aujourd'hui, mot pour mot :

> « Tu es l'auteur d'un roman de **fantasy** en français. Prose littéraire
> soignée, **au passé simple**, immersive. »

**La fiche v3 classe le passé simple parmi les interdits bloquants** et prescrit
passé composé et présent. Elle décrit un fantastique psychologique contemporain
à la première personne, en forme de journal, dans une maison unique. Le
préambule et la fiche se contrediraient donc dans le même prompt système — et
ce genre de conflit produit du texte moyen sans jamais lever d'erreur. Il est à
réécrire au moment du câblage, ce n'est pas négociable.

## 5. Trois désaccords de structure entre le graphe et la fiche v3

Ils ne sont pas des bugs : le graphe a été écrit pour un roman de fantasy à
plusieurs personnages, la fiche v3 pour un journal à une voix. Ce sont les
points sur lesquels une décision est attendue.

**L'unité de composition.** Le graphe planifie et écrit des **scènes** (3 ou 4,
~600 mots chacune). Le delta D1 de la fiche v3 a re-scopé tous les quotas —
accumulation, physiologie, couperet — sur l'**entrée de journal**. Rien dans le
graphe ne connaît la notion d'entrée. Soit `plan_node` produit des entrées
datées plutôt que des scènes, soit la fiche compte sur une unité que la machine
ne fabrique pas.

**Les voix.** Le prompt de `write` demande de « faire entendre les voix
distinctes », et `assemble_system_prompt` charge des fiches de personnages
présents. L'Involontaire est un roman **sans dialogue**, à une narratrice, dont
l'unique autre personnage est absent. La consigne pousse exactement dans la
direction que la fiche interdit.

**Le lieu.** Le retrieval cherche un lieu par similarité sémantique à chaque
scène. Il n'y a qu'une maison, et aucune scène hors les murs. L'appel est au
mieux inutile, au pire une source de variation.

## 6. Ce qui est mécaniquement contraint (et donc gratuit pour le style)

Le projet a une doctrine constante, payée trois fois : **le garde-fou qui tient
est dans le code ; le prompt prépare, il ne garantit pas.** Ce qui est
aujourd'hui dans le code :

- `delint()` — remplace les fuites d'anglais 1:1 sûres, signale les autres et
  les tokens collés (`confessionUnexpected`). **Ne connaît que l'anglais** : une
  fuite d'espagnol est passée sans être vue.
- `ends_mid_sentence` / `trim_to_sentence` — une seule définition de « fin de
  phrase » dans tout le projet, guillemet français compris.
- Détecteurs de la grille de calibration (`outillage/lint_style.py`, hors
  pipeline) : pastiche gothique, tics d'IA, incise adverbiale **et sa version
  prépositionnelle**, élision manquante, passé simple (formes non ambiguës),
  accumulation comptée, **recopie d'étalon**, noms propres, fuite lexicale,
  points de suspension hors champ du départ.

Ce dernier point mérite un développement, il est le plus utile à connaître pour
rédiger une fiche.

## 7. Ce que trois sessions ont réfuté

**Une forme syntaxique décrite en prose ne se reproduit pas.** L'accumulation —
une phrase longue en propositions juxtaposées — manque sur **7 tirages sur 7**
en session 1-2, puis sur **6 sur 6** en session 3, à trois formulations
différentes de la consigne. Y compris sur un run de 673 mots dont la phrase la
plus longue plafonnait à 38 mots et **une** virgule. Chiffrer le seuil dans la
fiche (60 mots, 6 virgules) n'a rien changé.

**Montrer un exemple le fait recopier.** La consigne « voici la forme exacte à
reproduire » suivie du texte étalon a produit deux « réussites » qui étaient
l'étalon copié **caractère pour caractère**, dans une scène qui parlait d'autre
chose. C'est la leçon déjà acquise sur le mode roleplay : les exemples se
formulent comme des **attitudes**, pas comme du texte. La fiche v3 réintroduit
cette formulation (section *Phrase et rythme*) — la session 3 ne l'a pas
déclenchée, sans doute parce que le matériau du chapitre 2 est trop éloigné de
celui de l'étalon, mais le piège est armé.

**Une boucle de renvoi ne rattrape pas ce que la fiche n'obtient pas.** Testée :
elle n'a jamais produit une accumulation authentique. Un second renvoi n'apporte
rien — le modèle donne sa meilleure réponse au premier reproche et plafonne.

**Ce qui, en revanche, transfère bien.** Les interdits négatifs passent : zéro
passé simple, zéro pastiche gothique, zéro nom propre en session 3, et la
vérification matérielle de l'anomalie (« je l'ai touchée deux fois, j'ai vérifié
la poubelle ») apparaît dans tous les runs. La fiche est efficace pour interdire
et pour installer une structure de scène. Elle échoue à imposer une **forme de
phrase**.

## 8. Budgets

**Contexte.** `num_ctx` = 8192. La fiche v3 en prompt système pèse ~4 200 tokens
(13 927 caractères). Avec `num_predict` = 1400 pour l'écriture, on est à ~0,69
de remplissage **avant** d'ajouter les chunks de la bible, le plan annoté et les
deux scènes précédentes. Servir la fiche entière à chaque appel d'écriture ne
tiendra pas : il faudra choisir les sections servies, et cette sélection est une
décision de style autant que de mémoire.

⚠ Au dépassement, Ollama fait **glisser** la fenêtre et ampute le DÉBUT du
prompt — c'est-à-dire `FRENCH_GUARD` puis les faits — **sans aucune erreur**.

**Temps.** Chaîne complète mesurée : 14 min 02 pour 3 scènes (dont 2 min de voix
clonée), ~17-18 min attendues à 4 scènes, contre 28 min au compteur du deck.
Chaque nœud supplémentaire, chaque reprise, se paie sur cette marge.

## 9. Ce qui reste à décider

1. **L'unité** : le plan produit-il des scènes ou des entrées datées ? Tout le
   comptage de la fiche en dépend.
2. **Quelles sections de la fiche sont servies** à `write` et à `review`, sachant
   que la fiche entière ne tient pas dans le budget. Les *interdits* et la
   *voix* semblent non négociables ; les *étalons* sont les plus lourds et les
   plus dangereux (recopie).
3. **Le préambule** de `assemble_system_prompt`, à réécrire pour L'Involontaire.
4. **L'accumulation** : trois sessions disent que ni la fiche ni une boucle de
   reproche ne l'obtiennent. Reste à décider si on l'abandonne comme marqueur
   obligatoire, si on la traite hors modèle, ou si on change de modèle pour
   elle.

---

*Sources dans le dépôt : `orchestrator/graph.py`, `orchestrator/retrieval.py`,
`orchestrator/qa.py`, `orchestrator/llm.py`, `outillage/lint_style.py`,
`grille-lint-session-{1,2,3}.md`, `journal-des-murs/`.*
