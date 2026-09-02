# Surface HTTP de la machine de génération — état réel au 2026-08-07 (rév. 2)

> **Rév. 5** — un flux **SSE `GET /events`** est ajouté, pour afficher les
> étapes de génération EN DIRECT sur le compteur (phase, sous-étape, et le récit
> des `notes`). C'est un **enrichissement optionnel** : il ne change rien au
> contrat gelé, le compteur reste autonome s'il tombe. Détail : section
> `GET /events`. Spécification complète côté deck :
> `docs/sse-live-steps-front.md`.
>
> **Rév. 4** — votre borne révisée (2'30-3'00, extrait joué en entier) est en
> place, réglée en secondes. **Un écart à connaître** : vos 375-450 mots
> supposent ~150 mots/min, le clone mesuré parle à 190 — vos 450 mots auraient
> donné 2'22, sous votre plancher. Voir la section extrait.
>
> **Rév. 3** — les deux marqueurs sont GARANTIS présents, et une route
> `POST /cancel` apparaît à cause d'une interaction avec votre politique de
> reprise (voir la section dédiée — c'est le seul point qui demande votre avis).
>
> **Rév. 2** : `/audio` branché, marqueur de bascule posé.

> **À qui ça s'adresse** : la session Code du dépôt `talk`, pour appliquer le
> changement openspec `remote-integration-contract` (jusqu'ici marqué
> « BLOQUÉ — la surface d'intégration côté machine n'existe pas encore »).
> Elle existe maintenant. Ce document dit ce qui répond, ce qui ne répond pas
> encore, et les deux endroits où je me suis écarté du contrat gelé.

Implémentation : `orchestrator/api.py` dans le dépôt `stack fictional writing`
(`http.server` de la bibliothèque standard, `ThreadingHTTPServer`).

```bash
cd "stack fictional writing/orchestrator"
.venv/bin/python api.py          # écoute sur 0.0.0.0:8420
```

Variables : `API_HOST`, `API_PORT` (8420), `API_CORS_ORIGIN` (`*` par défaut),
`API_OUTPUT_DIR` (défaut `../output`), `DEMO_BRIEF`, `DEMO_CHARACTERS`.

## Conformité au contrat gelé

| Op client | HTTP | Prêt | Pas prêt | État |
|---|---|---|---|---|
| `generate()` | `POST /generate` | `202` | — | **OK** |
| `chapter()` | `GET /chapter` | `200 text/markdown; charset=utf-8` | `204` | **OK** (avec les marqueurs, voir plus bas) |
| `audio()` | `GET /audio` | `200 audio/wav` | `204` | **OK** (mono 24 kHz) |
| `status()` | `GET /status` | `200 application/json` | — | **OK, enrichi** |

CORS : `Access-Control-Allow-Origin` (défaut `*`), `Allow-Methods: GET, POST,
OPTIONS`, `Allow-Headers: Content-Type`. `OPTIONS` répond `204`. Toutes les
réponses portent `Cache-Control: no-store` — vous interrogez la même URL pendant
que l'état change.

### Deux écarts assumés

**1. `phase` peut valoir `error`.** Le contrat listait `{generating, tts,
ready}`. J'émets aussi `error`, qui existe déjà dans votre type `GenStatus`
(`slides/lib/session.ts`). Raison : le savoir tôt vous laisse basculer sur les
assets embarqués immédiatement, au lieu d'attendre un timeout. Le silence côté
salle reste garanti par vous ; je ne mens pas sur mon état pour l'obtenir.

**2. « Pas prêt » = `204`, jamais `404`.** Le contrat acceptait les deux. `204`
dit « rien à donner pour l'instant » là où `404` dirait « cette route n'existe
pas » : plus facile à distinguer d'une faute d'URL en répétition.

## `POST /generate`

**Corps VIDE.** Le front POSTe sans payload : le récit — le **chapitre 7 de
« L'Involontaire »** — est construit côté serveur (`orchestrator/ch7.py`), le
deck n'a rien à décrire. Le corps est lu puis jeté (pour ne pas casser le
keep-alive). Répond **immédiatement** — le pipeline tourne dans un thread, y
compris le préflight machine qui prend ~10 s.

> Graine **aléatoire** à chaque run : la structure du chapitre est fixe (deux
> entrées, ancre, chute), mais le best-of-3 de l'entrée 1 et le tirage du
> glissement varient — c'est de la vraie génération live, pas un rejeu.

```
$ curl -sX POST http://MACHINE:8420/generate
{"accepted": true, "started": true, "state": "generating"}      # 202

$ curl -sX POST http://MACHINE:8420/generate      # pendant la génération
{"accepted": true, "started": false, "state": "generating"}     # 202
```

`202` dans les deux cas : c'est l'idempotence vue de chez vous, vous n'avez pas
à distinguer. `started` est indicatif.

**Après un échec, un nouveau POST RELANCE.** L'idempotence interdit deux
générations concurrentes, pas une reprise. Si `/status` rend `phase: "error"`,
vous pouvez re-POSTer une fois — à vous de décider si ça vaut le coup selon le
temps restant au compte à rebours. N'en faites pas une boucle.

## `GET /status`

Les deux champs du contrat, plus des champs **additifs** que vous pouvez ignorer
sans rien perdre — c'est la condition pour enrichir le compte à rebours sans
toucher au contrat.

```json
{
  "phase": "generating",
  "ready": false,

  "progress": 0.335,
  "label": "Écriture",
  "detail": "scène 2/4 (nemo)",
  "notes": ["3 faits dérivés, ils contraignent le plan"],
  "elapsed_s": 512,
  "budget_s": 1500,
  "gen_toks": 2148,
  "state": "generating",
  "duration_s": 1022
}
```

- `progress` : fraction 0..1, **monotone garantie**. Elle vient de bandes par
  phase calibrées sur un run réel, pas d'une prédiction : c'est une barre pour
  la salle, pas une estimation de fin. Une barre qui recule à la replanification
  se lirait comme un bug depuis la salle, d'où la monotonie.
- `label` / `detail` : phase lisible. Valeurs de `label` observables —
  `Invariants de la bible`, `Plan de scènes`, `Contrôle du plan contre la
  bible`, `Écriture`, `Relecture`, `Bascule des modèles`, `Réparation
  linguistique`, `Cohérence par faits`, `Lecture en voix clonée`.
- `notes` : les cinq derniers événements marquants. C'est là que vit le récit du
  dispositif — `PLAN REFUSÉ — contredit « … ». Replanification.`, `nemo déchargé,
  Qwen prend la main`, `génération coupée à 1400 tokens, continuation demandée`.
  Si vous voulez UNE chose à afficher au-delà du pourcentage, prenez celle-là :
  c'est le moment où le public voit la machine se corriger.
- `state` : mon état interne (`idle | generating | tts | ready | error`).
  Redondant avec `phase` aujourd'hui ; ne vous appuyez pas dessus.
- `error` : présent seulement en échec, texte brut destiné à l'opérateur.
  **Ne l'affichez pas à la salle** (le contrat interdit toute UI d'erreur).
- `budget_s` : mon budget interne (1500 s). Informatif — **votre compte à
  rebours reste autonome**, il ne doit jamais dépendre de mes réponses.

## `GET /events` — flux SSE des étapes (rév. 5, optionnel)

Un flux **Server-Sent Events** pour animer le compteur pendant la génération.
`Content-Type: text/event-stream; charset=utf-8`, CORS `*`, `Cache-Control:
no-store`, `Connection: close`.

- **Un événement par ~1 s**, format `data: {json}\n\n`. Le `{json}` est le
  **snapshot `/status` COMPLET** (mêmes champs : `phase, ready, progress, label,
  detail, notes, elapsed_s, budget_s, gen_toks, state`).
- **Événement ABSOLU**, pas incrémental : chaque event porte l'état entier. Une
  reconnexion reprend l'état courant — **pas de `Last-Event-ID`, pas d'IDs**.
- **Cycle de vie** : streame tant que `state ∈ {generating, tts}`, émet un
  dernier événement à l'état terminal (`ready`/`error`/`idle`), puis **ferme**.
  Connexion sur machine au repos : un seul événement `idle`, puis fermeture.

```
$ curl -N http://MACHINE:8420/events
data: {"phase":"generating","ready":false,"progress":0.12,"label":"Plan de scènes","detail":"","notes":["3 faits dérivés, ils contraignent le plan"],"state":"generating", ...}

data: {"phase":"generating","ready":false,"progress":0.34,"label":"Écriture","detail":"scène 2/4 (nemo)","notes":["nemo déchargé, Qwen prend la main"],"state":"generating", ...}
…
data: {"phase":"ready","ready":true,"progress":1.0,"state":"ready", ...}
# connexion fermée
```

**C'est un ENRICHISSEMENT, pas une dépendance.** Le contrat gelé (generate /
status / chapter / audio) est inchangé ; le compteur reste **autonome** si le
flux tombe. `notes` = les 5 dernières seulement — le deck accumule pour bâtir le
récit complet. `GET /status` reste disponible en repli (poll ponctuel).

## Les deux marqueurs du chapitre

`GET /chapter` rend le chapitre **entier**, avec deux commentaires HTML posés par
du code (jamais par le modèle — un LLM les mettrait ailleurs à chaque tirage) :

```markdown
Samedi 14. Beau temps.

J'ai inscrit dans mon carnet : ranger les photos d'elle dans le tiroir du bas…

<!-- BASCULE -->

Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui… »
…
Constat : anniversaire.

<!-- FIN AUDIO -->

(rien après : la chute est la dernière ligne)
```

- **`<!-- BASCULE -->` tombe avant le SECOND en-tête daté du chapitre.** Le
  chapitre 7 a deux entrées le même jour ; le speaker lit la première (l'entrée
  courte de l'après-midi) à voix nue, puis lance l'audio sur la seconde. `GET
  /audio` commence exactement là. (Règle CH7 = `sur_second_entete` ; pour un
  chapitre sans double en-tête, repli sur « après la 2ᵉ phrase ».)
- **`<!-- FIN AUDIO -->`** marque où la voix clonée s'arrête — pour le CH7,
  juste après la chute « Constat : anniversaire. ».

**Les deux marqueurs sont GARANTIS présents**, y compris dans les cas
dégénérés — chapitre de deux phrases, texte sans ponctuation finale, scènes
vides. Votre règle (« un chapitre sans les deux marqueurs est traité comme non
prêt ») nous a fait durcir ça : mon code ne posait `FIN AUDIO` que si la borne
d'extrait était calculable, si bien qu'un chapitre court aurait fait disparaître
le chapitre live **en silence**. Il y a maintenant un repli en fin de texte, et
cinq cas limites sont couverts par un test.

**Extrait calé sur 2 min 45**, au milieu de votre fenêtre 2'30-3'00. La borne se
règle désormais en SECONDES (`AUDIO_SECONDES=165`), pas en mots : c'est une
durée que vous demandez, et une consigne exprimée dans l'unité du besoin ne se
traduit pas de travers.

⚠ **Vos 375-450 mots supposent ~150 mots/min. Le clone parle à 190** (mesuré).
Vos 450 mots auraient donc donné **2 min 22 — sous votre propre plancher**, donc
un trou puisque l'extrait est maintenant joué en entier. La conversion se fait
chez nous : 165 s × 190 mots/min = **522 mots**.

Ce débit de 190 vient d'un seul échantillon de 117 mots. Le premier run complet
le confirmera : si la durée obtenue s'écarte de plus de 20 s de la cible, le
rendu émet une note dans `/status` avec le débit réel à reporter dans la
configuration. Autrement dit, l'erreur se signalera au lieu de se découvrir sur
scène.

**Le calcul TTS sera plus court que vous ne l'estimez** : ~1 min 45, pas 3 min.
Votre estimation suppose 1× temps réel (c'est ce que dit le RUNBOOK) ; la mesure
sur cette machine donne **1,57×** modèle chaud. Cycle complet attendu : **~19
min** contre 28 au compteur.

## Le point de timing qui vous concerne

Mesures sur la machine, pas des estimations :

| Étape | Mesuré |
|---|---|
| Génération du chapitre (4 scènes) | **17,0 min** (1022 s) |
| Rendu voix clonée (522 mots, 2'45 visées) | **~1,8 min** (1,57× temps réel) |
| **Total** | **~19 min** contre 28' au compteur → ~9 min de marge |

La lecture clonée est bornée à **2 min 45**, et non au chapitre entier : celui-ci
ferait 12,6 min d'écoute, injouable dans une keynote de cinquante minutes.

## Mode acteur — hors contrat, mais une contrainte de PLANNING pour vous

Hors du contrat gelé (il ne couvre que le chapitre), mais ça vous concerne :
la machine sert aussi une page de roleplay, à la racine — `http://MACHINE:8420/`.
Elle est autonome (aucun CDN, aucune police distante) et sur la même origine que
l'API, donc **affichable en iframe depuis une slide**.

**La contrainte** : le roleplay et la génération partagent le même modèle de
13 GB, et la machine n'en tient qu'un. `POST /chat` répond donc **`409`** tant
qu'un chapitre est en cours :

```json
{"error": "génération en cours",
 "detail": "Le mode acteur et la génération partagent le même modèle ; la
            machine n'en tient qu'un. Réessayer après la récolte du chapitre.",
 "state": "generating"}
```

Ce n'est pas une limite logicielle qu'on pourrait lever : faire cohabiter les
deux modèles demande 17,8 GB sur 19,3, ce qui a déjà fait paniquer cette
machine. Et sans ce refus, chaque réplique attendrait la fin de l'appel
d'écriture en cours — **jusqu'à deux minutes de silence sur scène**.

**Conséquence pour le déroulé** : la démo d'acteur se joue AVANT le lancement du
chapitre (section 3) ou APRÈS sa récolte (section 7), jamais entre les deux. Si
le plan du talk la prévoit dans l'intervalle, il faut le savoir maintenant.

## Votre politique de reprise — une interaction à trancher

Vos réglages nous vont : `/status` et `/chapter` répondent en millisecondes (ils
lisent un dict ou un fichier, jamais le modèle), donc **3 s de timeout est
large**, et un sondage toutes les 10 s ne coûte rien.

Le re-POST unique sur `phase: error` nous va aussi — chez nous, un POST après
échec relance bien (l'idempotence interdit deux générations concurrentes, pas
une reprise).

**Mais il a une conséquence que vous ne pouvez pas voir depuis le deck.** À
moins de trois minutes du décompte, la relance repart pour **dix-sept minutes**
de génération, soit bien après la fin du talk. Or `POST /chat` refuse pendant
qu'un chapitre se génère (même modèle, la machine n'en tient qu'un) : le mode
acteur serait donc bloqué pendant tout ce temps, précisément quand on veut le
montrer après la récolte.

D'où **`POST /cancel`** : `{"cancelled": true|false, "state": …}`. L'arrêt prend
effet à la frontière de nœud suivante — au pire après l'appel modèle en cours,
46 s mesurées. Le job repasse à `idle` et la machine redevient disponible.

Rien à faire de votre côté si ça vous va : c'est une sortie de secours
d'opérateur, pas une opération du deck. Mais si vous préférez que la reprise
tardive n'existe pas plutôt que d'avoir à l'annuler à la main, dites-le — le
choix vous appartient, c'est votre décompte.

## `phase` peut aussi valoir `idle`

En plus de `error` (déjà signalé en rév. 1) : avant tout lancement, et après une
annulation. C'est une valeur de votre `GenStatus`. Prétendre `generating` dans
ces deux cas vous ferait attendre un chapitre que personne n'écrit.

## Points ouverts, côté vous

- `VITE_GEN_HOST` : **IP fixe recommandée** plutôt que mDNS (votre « À trancher »
  #1). Le service écoute sur `0.0.0.0:8420`.
- **Un seul host** pour `/chapter` et `/audio` : confirmé, tout sortira de la
  machine de génération (votre « À trancher » #4).
- Valeurs de timeouts / retries : à caler en répétition réseau. Sachez seulement
  que `/status` et `/chapter` répondent en millisecondes — ils lisent un fichier
  ou un dict, ils n'attendent jamais le modèle. Un timeout de 3 s est large.

## Deux avertissements d'exploitation

- **La machine ne doit pas s'endormir.** Après une nuit de veille, le démon
  Ollama restait vivant, port ouvert, mais incapable de charger un modèle :
  toutes les générations en 500. Remède `launchctl kickstart -k
  gui/$(id -u)/local.ollama`, prévention `caffeinate -is`. Mon préflight le
  détecte maintenant en faisant réellement générer un token.
- **Un run par démarrage.** Le swap ne se rend pas à chaud ; le préflight refuse
  une machine qui n'a pas digéré le run précédent, et il a raison. En répétition,
  prévoyez le redémarrage entre deux essais complets.
