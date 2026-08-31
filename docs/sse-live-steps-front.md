# SSE « étapes en direct » — spécification pour la session Code du deck (jalon 4)

> **À qui** : la session Code du dépôt `talk` (Slidev), pour débloquer le change
> openspec `remote-integration-contract` (jalon 4 : client réel + flux d'étapes).
> **Côté machine** : l'endpoint SSE `GET /events` **existe** (`orchestrator/api.py`,
> branche `sse-live-steps`). Ce document dit ce qu'il envoie et comment le
> consommer, fichier par fichier.

## 0. L'objectif et l'invariant sacré

Pendant la génération (~17 min), le public doit **voir la machine travailler** :
la phase courante, la sous-étape, et surtout le **récit du dispositif** (les
`notes` — « PLAN REFUSÉ — replanification », « nemo déchargé, Qwen prend la main »).

**Invariant NON négociable** (contrat `remote-integration`, exigence « countdown
autonome ») : le flux d'étapes est un **enrichissement**. S'il tombe (endpoint
injoignable, réseau coupé, EventSource en erreur), **le compteur continue seul,
la génération se fait, le fallback embarqué joue** — indistinguable côté salle,
jamais d'UI d'erreur. Toute la logique SSE doit dégrader en silence.

## 1. Le contrat SSE (ce que la machine envoie)

`GET {VITE_GEN_HOST}/events` — `Content-Type: text/event-stream; charset=utf-8`,
CORS `*`, `Cache-Control: no-store`, `Connection: close`.

- **Un événement par ~1 s**, format SSE standard : `data: {json}\n\n`.
- Le `{json}` est le **snapshot `/status` complet** (mêmes champs) :
  ```json
  { "phase":"generating", "ready":false, "progress":0.34,
    "label":"Écriture", "detail":"scène 2/4 (nemo)",
    "notes":["nemo déchargé, Qwen prend la main"],
    "elapsed_s":512, "budget_s":1500, "gen_toks":2148, "state":"generating" }
  ```
- **Événement ABSOLU** (pas incrémental) : chaque event porte l'état complet. Une
  reconnexion reprend l'état courant — **pas de `Last-Event-ID`, pas d'IDs**.
- **Cycle de vie** : la machine streame tant que `state ∈ {generating, tts}`,
  émet **un dernier événement** à l'état terminal (`ready` / `error` / `idle`),
  puis **ferme** la connexion. À la connexion sur machine au repos : un seul
  événement `idle` puis fermeture.
- `phase` ∈ `{generating, tts, ready, error, idle}` — identique à votre type
  `GenStatus`. `progress` ∈ [0,1] **monotone**. `notes` = les **5 dernières**
  seulement (voir §3, l'accumulation est votre travail).

## 2. Env (`talk/.env.example` + `.env` local)

Trois corrections, la machine actuelle ne correspond pas :

| Var | Aujourd'hui | Correct | Pourquoi |
|---|---|---|---|
| `VITE_GEN_HOST` | `http://192.168.1.50:8000` | `http://<IP-FIXE>:8420` | l'API écoute sur **8420** |
| `VITE_TTS_HOST` | `http://192.168.1.50:8100` | **à supprimer** | fantôme, jamais lu ; l'audio sort de `${VITE_GEN_HOST}/audio` |
| `VITE_MOCK` | `1` | `0` pour le live (`1` en répétition offline) | bascule vers le client réel |

- URL SSE = `` `${import.meta.env.VITE_GEN_HOST}/events` `` — **pas de nouvelle var**.
- `VITE_COUNTDOWN_MINUTES=2` reste pratique pour répéter en accéléré.

## 3. Store (`talk/slides/lib/session.ts`)

Le store est la seule source durable inter-slides (il survit au démontage des
composants — c'est pour ça que l'état vit là). Il faut y porter l'étape + le feed.

1. **Interface `Session`** (L15-22) + init `reactive` (L24-30) — ajouter :
   ```ts
   step: { label: string; detail?: string } | null   // init null
   notes: string[]                                    // init []
   ```
2. **Mutateurs** — ajouter :
   - `setStep(label: string, detail?: string)` → `session.step = { label, detail }`.
   - `pushNotes(incoming: string[])` → **accumule** dans `session.notes` en
     dédupliquant : le SSE ne renvoie que les 5 dernières, c'est VOUS qui
     construisez le récit complet (append celles pas encore vues, garder l'ordre,
     borner à ~30 pour l'affichage).
3. **Remise à zéro** — dans `start()` (L38-45) ET `reset()` (L48-55), remettre
   `step = null` et `notes = []` (sinon un run garde le récit du précédent).
4. `applyStatus(status, chapter)` (L57-61) **ne change pas** : il continue de
   porter `status` + `chapter` ; l'étape et les notes passent par les nouveaux
   mutateurs.

## 4. Client réel + SSE (`talk/slides/lib/genClient.ts`)

Le vrai chemin remplit la branche non-mock (aujourd'hui `throw 'jalon 4'`, L60-61).
**Les composants ne changent pas** (but du contrat). Owner du cycle de vie SSE =
ce module (PAS un composant : le compteur se démonte entre slides, un EventSource
possédé par le composant serait tué au changement de slide).

```
const GEN = import.meta.env.VITE_GEN_HOST
let es: EventSource | null = null

generate() réel :
  1. POST `${GEN}/generate`            // 202, idempotent, corps vide
  2. es = new EventSource(`${GEN}/events`)
  3. es.onmessage = (e) => {
       const s = JSON.parse(e.data)
       applyStatus(s.phase)            // 'generating'|'tts'|'ready'|'error'|'idle'
       setStep(s.label, s.detail)
       pushNotes(s.notes ?? [])
       if (s.phase === 'ready') {
         const text = await fetch(`${GEN}/chapter`).then(r => r.text())
         applyStatus('ready', { text, audioUrl: `${GEN}/audio` })
         stop()                        // ferme l'ES (sinon reconnexion auto)
       }
       if (s.phase === 'error') { fallbackFixtures(); stop() }
     }
  4. es.onerror = () => { /* dégradation SILENCIEUSE — voir §5 */ }
```

- **`stop()`** (L83-85) : `es?.close(); es = null` en plus des timers mock ;
  câblé via `session.reset()`.
- `status()` / `chapter()` / `audio()` réels ne sont plus le chemin principal
  (le SSE porte le statut, `/chapter` est fetché à `ready`). Les garder en repli
  si vous voulez, mais le SSE suffit.

## 5. La dégradation silencieuse (le cœur de l'invariant)

`EventSource` **reconnecte tout seul** en cas de coupure — utile en pleine
génération (résilience gratuite). Mais il ne faut JAMAIS que son échec bloque ou
s'affiche. Échelle de repli, du mieux au pire, toutes muettes :

1. **SSE OK** → étapes + récit en direct. Nominal.
2. **SSE coupé en cours** → `onerror`, EventSource retente seul ; entre-temps le
   compteur tourne (ticker autonome), `session.step`/`notes` gèlent sur la
   dernière valeur. Rien à faire.
3. **SSE jamais connecté / machine injoignable** → le compteur tourne quand même
   (il n'a jamais dépendu du flux) ; à la fin, tenter UNE fois `GET ${GEN}/chapter`
   (200 → vrai chapitre ; 204/échec → fixtures). L'audio idem via `/audio`.
4. **Tout échoue** → fixtures embarquées `/fallback/chapitre.{md,wav}` (déjà la
   philosophie du mock). Le public ne voit aucune différence.

**Jamais** : un `throw` non attrapé, un spinner bloqué, un message d'erreur à
l'écran. `s.error` (présent en échec) est pour l'opérateur, **pas la salle**.

## 6. UI compteur (`talk/slides/components/Countdown.vue`)

- Après `countdown__note` (template L47), ajouter une ligne `countdown__step`
  liée à `session.step?.label` (et `detail` en plus discret).
- Sous elle, un `countdown__feed` optionnel qui déroule les dernières
  `session.notes` — **c'est ça, l'effet** « on voit la machine se corriger ».
- `global-bottom.vue` (pilule de coin, L37) : optionnellement `session.step.label`
  à côté du mm:ss.
- Ne rien afficher si `session.step` est `null` (pré-lancement / fallback).

## 7. Contrat openspec (`talk/openspec/changes/remote-integration-contract/`)

Le contrat gelé est **poll-only** (4 ops, `{phase, ready}`). Amender :
- `design.md` (table d'ops L19-24) : ajouter `GET /events` (SSE) + la charge.
- `specs/remote-integration/spec.md` : étendre l'exigence « Statut optionnel,
  countdown autonome » (L37-46) pour couvrir le flux — **en réaffirmant** qu'il
  est optionnel / non bloquant / indistinguable du fallback.
- C'est le débloquage du jalon 4 (le change est marqué BLOQUÉ aujourd'hui).

## 8. Vérification

- **Machine (déjà testable)** : `curl -N http://<IP>:8420/events` pendant qu'un
  `POST /generate` tourne → `data: {…}` toutes les ~1 s, `progress` croissante,
  `label`/`detail`/`notes` qui changent, puis un event terminal et fermeture.
  Couper le `curl` → pas de traceback serveur (garde `BrokenPipeError`).
- **Deck** : `VITE_MOCK=0`, `VITE_GEN_HOST` sur la machine, `VITE_COUNTDOWN_MINUTES=2` ;
  cliquer le trigger → le compteur montre les étapes défiler + le récit ; à
  `ready`, le chapitre + l'audio arrivent.
- **Résilience** : débrancher l'API en pleine génération → le compteur continue,
  aucun message, bascule fixtures. **C'est le test qui compte.**
