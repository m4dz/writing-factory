# Surface HTTP de la machine de génération — état réel au 2026-08-07

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
| `chapter()` | `GET /chapter` | `200 text/markdown; charset=utf-8` | `204` | **OK** (sans le marqueur, voir plus bas) |
| `audio()` | `GET /audio` | `200 audio/wav` | `204` | **route OK, rend toujours 204** (TTS pas branché) |
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

Corps ignoré (lu puis jeté, pour ne pas casser le keep-alive). Répond
**immédiatement** — le pipeline tourne dans un thread, y compris le préflight
machine qui prend ~10 s.

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

## Ce qui n'est pas encore vrai

**`GET /audio` rend toujours `204`.** L'étape TTS n'est pas branchée. Votre
fallback silencieux est donc le chemin nominal pour l'audio à cette heure — ce
qui est un bon terrain d'essai pour le vérifier.

**`GET /chapter` ne contient pas encore `<!-- BASCULE -->`.** Le marqueur sera
posé **par le code**, pas par le modèle : c'est la charnière du tour de magie, un
marqueur placé par un LLM serait aléatoire.

## Le point de timing qui vous concerne

Le run de référence mesuré (machine au repos, 4 scènes) : **1022 s, soit 17,0
min** pour la génération seule. Il reste le TTS.

Et là, une contrainte que le contrat ne pouvait pas voir : le runbook TTS donne
~1× temps réel. Si la bascule tombe après le premier paragraphe, le clone doit
lire ~2300 mots, soit **~15 min d'audio et ~15 min de calcul** — 32 min contre
28' au compteur, et une lecture de quinze minutes dans une keynote de cinquante.

Décision prise côté machine : **la lecture clonée est bornée à ~3-4 min
(450-600 mots)**, le pipeline posera la bascule ET bornera l'extrait rendu en
audio. Cible totale ~21 min, marge ~7 min sur les 28'.

Conséquence pour vous : rien à changer si votre section 7 lit un extrait. Si le
deck prévoyait de lire tout le chapitre en voix clonée, c'est le moment de le
dire — c'est un désaccord de conception, pas un détail d'implémentation.

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
