# RUNBOOK — faire tourner la fabrique

Tout ce qu'il faut exécuter, dans l'ordre, pour : produire la version finale du
chapitre, préparer les assets de démo, et servir le deck le jour J.

Un principe traverse ce document : **la machine est le maillon fragile, pas le
code**. Les incidents de développement ont tous été des problèmes de machine —
disque plein, swap saturé, démons d'indexation, veille. Les vérifications
d'état ne sont donc pas de la paperasse, ce sont les étapes qui décident du
résultat.

---

## 0. Vérifier la machine (2 min, avant tout)

```bash
cd "stack fictional writing/orchestrator"
.venv/bin/python preflight.py
```

Sortie attendue, tout vert :

```
disque 213 GB libres | swap aucun swapfile (machine fraîche) |
mémoire récupérable 13 GB, pression normale | entretien macOS : aucun |
LLM chauds : aucun
```

Le préflight **refuse de démarrer** dans cinq cas, tous vécus :

| Refus | Cause | Remède |
|---|---|---|
| Disque < 20 GB | macOS ne peut plus agrandir le swap → kernel panic | Libérer de l'espace |
| Pression mémoire critique | Verdict de macOS lui-même | `ollama stop <modèle>`, fermer les gros consommateurs |
| Entretien macOS > 80 % CPU | `spotlightknowledged`, `photoanalysisd`, `mediaanalysisd`… | Attendre, ou couper l'indexation (§ 7) |
| Ollama ne génère pas | Démon vivant mais incapable de lancer `llama-server` (typique après une veille) | `launchctl kickstart -k gui/$(id -u)/local.ollama` |
| 2+ LLM chauds | Co-résidence : 17,8 GB demandés sur 19,3 | `ollama stop <modèle>` |

**Le swap saturé n'est plus bloquant qu'en mode chronomètre** (révision du
2026-08-09). `run_chapter.py` et l'API passent `chrono=True` — là, la durée EST
l'objet, et une machine qui pagine rend un chiffre ininterprétable. L'outillage
de calibration, lui, juge de la prose : il se contente d'un avertissement.

Le raisonnement précédent (« redémarrer, macOS ne rend pas les swapfiles à
chaud ») était faux sur les deux points. Mesuré : sans autre intervention que
l'expiration de `keep_alive` d'Ollama, la mémoire libre est passée de 11 % à
87 %, le swap `used` a chuté de 1,35 GB et le `total` de 4096 à 3072 MB. Et les
deux incidents qui avaient motivé ce blocage relevaient d'autre chose — les
kernel panics d'un **disque à 99 %**, les trous de génération de
**`mediaanalysisd`** (reproduits sur une machine fraîchement redémarrée, swap à
zéro). Les deux ont leur propre garde-fou.

**Remède au swap, dans l'ordre :**

```bash
ollama stop mistral-nemo:12b-instruct-2407-q8_0   # rend la mémoire ET rétrécit le swap
sysctl vm.swapusage                                # vérifier
sudo purge                                         # si ça ne suffit pas (demande le mot de passe)
```

Redémarrer reste le dernier recours, pas le premier réflexe.

**Empêcher la veille** avant toute session longue :

```bash
caffeinate -is &        # à tuer après la démo
```

---

## 1. Backends

### 1.1 Ollama (hors conteneur, accès GPU direct)

Installé une fois pour toutes comme agent launchd du projet — **pas** via
`brew services`, qui régénère son plist et efface les variables :

```bash
brew services stop ollama                      # si jamais il tourne encore
cp scripts/local.ollama.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.ollama.plist
```

Vérifier :

```bash
launchctl print gui/$(id -u)/local.ollama | grep -E "OLLAMA_(HOST|MAX_LOADED)"
# OLLAMA_HOST => 127.0.0.1
# OLLAMA_MAX_LOADED_MODELS => 2
curl -s localhost:11434/api/ps
```

Modèles nécessaires (~18 GB) :

```bash
ollama pull mistral-nemo:12b-instruct-2407-q8_0   # auteur + acteur
ollama pull qwen2.5:7b-instruct                   # QA / cohérence
ollama pull nomic-embed-text                      # embeddings
```

### 1.2 ChromaDB (conteneur)

```bash
podman machine start                              # après un redémarrage du Mac
podman start stackfictionalwriting_chromadb_1     # ou : podman-compose up -d chromadb
curl -s -o /dev/null -w "%{http_code}\n" localhost:8000/api/v2/heartbeat   # 200
```

### 1.3 Indexer la bible

À refaire **à chaque modification** de `bible/` : ChromaDB est toujours dérivé
du Markdown, jamais l'inverse.

```bash
podman-compose --profile tools run --rm indexer
podman-compose --profile tools run --rm indexer python query_test.py "la forge en ruine"
```

L'indexation est idempotente et purge les chunks orphelins. Elle ne touche
**pas** la collection `sessions` (mémoire du mode acteur), qui vit à part
précisément pour survivre à un réindexage.

### 1.4 Venv de l'orchestrateur

```bash
python3 -m venv orchestrator/.venv
orchestrator/.venv/bin/pip install -r orchestrator/requirements.txt
```

Un seul venv : LangGraph, le client Chroma **et** le TTS (`mlx-audio` tourne sur
notre Python 3.10). Compter ~1 min et ~700 MB.

---

## 2. Notifications téléphone (facultatif)

Le bipeur d'opérateur : phase, pourcentage, échecs. Il n'envoie **jamais** de
contenu (ni chapitre, ni bible) — cf. `orchestrator/notify.py`.

1. Dans Telegram, parler à **@BotFather** → `/newbot` → nom et pseudo du bot →
   il rend un jeton de la forme `123456789:AAE...`.
2. Écrire un message au bot depuis son téléphone (sinon il ne peut pas répondre).
3. Récupérer l'identifiant de conversation :

```bash
curl -s "https://api.telegram.org/bot<JETON>/getUpdates" | python3 -m json.tool | grep -m1 '"id"'
```

4. Exporter les deux valeurs avant de lancer l'API :

```bash
export TELEGRAM_BOT_TOKEN="123456789:AAE..."
export TELEGRAM_CHAT_ID="987654321"
```

Sans ces variables, aucun octet ne part sur le réseau. Vérifier l'installation
sur la montre avec un run de test avant le jour J.

---

## 3. Générer un chapitre

### En ligne de commande (mesure, mise au point)

```bash
cd orchestrator
.venv/bin/python -u run_chapter.py \
  --brief "Élara arrive à la forge de Valmir…" \
  --characters elara-vance kael-doran
```

**Lancer au PREMIER PLAN.** Un lancement détaché (`&`, `nohup`) hérite d'une
priorité basse (`nice 5`) : sans concurrence ça ne se voit pas, mais face à un
démon d'indexation le processus se fait doubler et la génération prend le
triple. `--muet` supprime l'habillage si l'on veut mesurer au plus juste.

### Par l'API (ce que fait le deck)

```bash
cd orchestrator
.venv/bin/python api.py            # écoute sur 0.0.0.0:8420
```

Puis, depuis n'importe où sur le réseau local :

```bash
curl -X POST http://MACHINE:8420/generate     # 202, idempotent
curl  http://MACHINE:8420/status              # avancement
curl  http://MACHINE:8420/chapter -o chapitre.md
curl  http://MACHINE:8420/audio   -o chapitre.wav
curl -X POST http://MACHINE:8420/cancel       # sortie de secours
```

Compter **~19 min** au total (17 de génération, ~2 de voix clonée).

---

## 4. Préparer les assets de démo

### 4.1 Sessions de roleplay pré-générées

Elles sont **rejouées** sur scène, jamais générées en direct : zéro latence,
zéro risque de sortie de personnage devant la salle, et ça fonctionne même
pendant qu'un chapitre se génère.

1. Ouvrir `http://MACHINE:8420/` (ou en iframe dans une slide).
2. Choisir le personnage, mener la conversation.
3. **Enregistrer** → écrit `sessions/<personnage>/<horodatage>.md`.
4. **Éditer le fichier à la main** : supprimer les répliques faibles dans la
   section `## Transcription`. C'est l'étape qui fait la qualité — le modèle
   garde des tics (il s'interpelle parfois lui-même, esquive deux fois de la
   même façon) et la curation les traite mieux que n'importe quel prompt.
5. Vérifier le rendu via le sélecteur « rejouer » de la page.

Deux sections, deux usages : `## Ce qui s'est dit` est la mémoire du personnage
(indexée, elle nourrit les sessions suivantes), `## Transcription` est ce qui se
rejoue. Élaguer l'une ne touche pas à l'autre.

### 4.2 Chapitre et audio de secours

Le deck bascule en silence sur ses assets embarqués à la moindre défaillance.
Les produire **avant** le jour J :

```bash
curl http://localhost:8420/chapter -o public/fallback/chapitre.md
curl http://localhost:8420/audio   -o public/fallback/chapitre.wav
```

(à déposer dans le dépôt du deck). Ne pas écouter le rendu de secours en entier
avant le talk — la promesse « pas même moi » n'aime pas les répétitions.

---

## 5. Le jour J

| Quand | Quoi |
|---|---|
| J-1 | Assets de secours produits, sessions de roleplay curées, `caffeinate` testé |
| H-60 | **Redémarrer le Mac.** Laisser l'entretien macOS finir (§ 0) |
| H-30 | Backends : Ollama, podman + ChromaDB, indexation à jour |
| H-20 | `caffeinate -is &`, puis `preflight.py` — tout doit être vert |
| H-15 | Lancer l'API **au premier plan**, avec les variables Telegram |
| H-10 | Test à blanc : `POST /chat` sur un personnage, une réplique doit revenir |
| Section 3 | Le deck envoie `POST /generate`. Le compte à rebours part |
| Pendant | La montre reçoit les battements. Sur `❌ ÉCHEC`, préparer le plan B |
| Section 7 | Le deck récolte `/chapter` et `/audio` tout seul |
| Après | `POST /cancel` si une génération traîne (elle bloquerait le mode acteur) |

**Le mode acteur ne cohabite pas avec la génération** : `POST /chat` répond
`409` tant qu'un chapitre s'écrit. Les deux partagent le même modèle de 13 GB, et
la machine n'en tient qu'un. La démo d'acteur se joue donc avant le lancement ou
après la récolte.

---

## 6. Pannes courantes

| Symptôme | Cause probable | Remède |
|---|---|---|
| Toutes les générations en 500 | Ollama survit à une veille mais ne charge plus de modèle | `launchctl kickstart -k gui/$(id -u)/local.ollama` |
| Préflight : « swap saturé » (mode chrono seulement) | Un run a déjà tourné depuis le démarrage | `ollama stop <modèle>`, puis `sudo purge` si besoin. Redémarrer en dernier recours |
| Préflight : « entretien macOS » | Indexation Spotlight / Photos | Attendre, ou § 7 |
| Génération très lente, trous de plusieurs minutes | Démon d'entretien + processus lancé en tâche de fond | Relancer au premier plan, machine au repos |
| `/chapter` en 204 | Génération non finie, ou échouée | `GET /status` → champ `error` |
| `/audio` en 204 mais chapitre présent | TTS en échec — le chapitre reste valide | Le deck bascule sur l'audio embarqué, rien à faire |
| `POST /chat` en 409 | Un chapitre se génère | Attendre la récolte, ou `POST /cancel` |
| ChromaDB injoignable | Machine Podman arrêtée après un reboot | `podman machine start` puis `podman start …` |

---

## 7. Couper l'indexation macOS (optionnel, jour J)

Les démons d'indexation sont le premier risque de scène : ils ont produit des
trous de dix-sept minutes en pleine génération.

```bash
sudo mdutil -a -i off      # suspend l'indexation Spotlight
# après le talk :
sudo mdutil -a -i on
```

À faire seulement si l'entretien ne retombe pas de lui-même. Vérifier ensuite :

```bash
ps -Ao %cpu,comm -r | head -5
```
