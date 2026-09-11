# Runbook

Everything to run, in order: check the machine, start the backends, generate
a chapter, prepare the demo assets, serve the deck. One entry point,
`.venv/bin/factory` (or `factory` with the venv activated); every command
below is one of its subcommands (`factory --help` lists them).

One principle runs through it: **the machine is the fragile link, not the
code.** Every development incident was a machine incident: full disk,
saturated swap, indexing daemons, sleep. The state checks are not paperwork;
they decide the result.

## 0. Check the machine (2 min, before anything)

```bash
factory doctor
```

Runs the real probes and prints one line per check: machine state and the
preflight verdict, Ollama and the three models, ChromaDB, the voice reference
and the TTS dependencies, the bible and the style sheet. Exit code 1 when
something blocks. Expected, all green:

```
machine
  ✓ disque 213 GB libres | swap aucun swapfile (machine fraîche) | mémoire
    récupérable 13 GB, pression normale | entretien macOS : aucun | LLM chauds : aucun
  ✓ préflight : accepté
backends
  ✓ Ollama http://localhost:11434
  ✓ modèle auteur / QA / embeddings
  ✓ ChromaDB localhost:8000
voix
  ✓ référence vocale … ✓ dépendances TTS
```

The same preflight is the FIRST NODE of the generation graph: `factory
generate` and `POST /generate` refuse to start in five cases, all lived
(ADR-0016):

| Refusal | Cause | Remedy |
|---|---|---|
| Disk < 20 GB | macOS cannot grow the swap → kernel panic | Free space |
| Critical memory pressure | macOS's own verdict | `ollama stop <model>`, close big consumers |
| macOS maintenance > 80 % CPU | `spotlightknowledged`, `photoanalysisd`, `mediaanalysisd`… | Wait, or cut indexing (§7) |
| Ollama does not generate | Daemon alive but cannot start `llama-server` (after sleep) | `launchctl kickstart -k gui/$(id -u)/local.ollama` |
| 2+ warm LLMs | Co-residence: 17.8 GB requested on 19.3 | `ollama stop <model>` |

A consumed swap blocks only in timing mode (`factory generate`, the API,
the timed calibration stages), where the duration is the object. Remedy, in
order:

```bash
ollama stop mistral-nemo:12b-instruct-2407-q8_0   # returns memory AND shrinks the swap
sysctl vm.swapusage
sudo purge                                         # if not enough
```

Reboot is the last resort. Prevent sleep before any long session, and keep
the machine PLUGGED IN for any measurement that counts (`caffeinate` does not
stop Maintenance Sleep on battery):

```bash
caffeinate -is &        # kill after the demo
```

## 1. Backends

### 1.1 Ollama (host, direct GPU)

Installed once as the project's launchd agent, NOT via `brew services`
(ADR-0009):

```bash
brew services stop ollama
cp scripts/local.ollama.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.ollama.plist
launchctl print gui/$(id -u)/local.ollama | grep -E "OLLAMA_(HOST|MAX_LOADED)"
curl -s localhost:11434/api/ps
```

Models (~18 GB):

```bash
ollama pull mistral-nemo:12b-instruct-2407-q8_0   # author + actor
ollama pull qwen2.5:7b-instruct                   # QA / coherence
ollama pull nomic-embed-text                      # embeddings
```

### 1.2 ChromaDB (container)

```bash
podman machine start                              # after a Mac reboot
podman-compose up -d chromadb
curl -s -o /dev/null -w "%{http_code}\n" localhost:8000/api/v2/heartbeat   # 200
```

### 1.3 Index the bible

After EVERY change to `bible/`. ChromaDB is derived from the Markdown, never
the reverse. Idempotent, purges orphans, never touches the `sessions`
collection. From the host venv or from the container, same command:

```bash
factory index
factory query "les deux couverts"
# or, without a host venv:
podman-compose --profile tools run --rm indexer
podman-compose --profile tools run --rm indexer factory query "les deux couverts"
```

Then re-prove the seal (ADR-0017), never presume it:

```bash
factory eval seal > experiments/reports/rapport-etancheite-$(date +%Y%m%d).md
```

### 1.4 The venv

```bash
make venv                          # the package, the graph and the test deps
.venv/bin/pip install -e ".[tts]"  # stage machine only: mlx-audio, soundfile, numpy
```

One venv: LangGraph, the Chroma client AND the TTS. About 1 min, ~700 MB.
Dependency groups: core (indexer, query, eval; what the container installs),
`pipeline` (LangGraph: generate, calibrate, serve, chat), `tts`, `test`.

### 1.5 Development checks

```bash
make venv && make check      # ruff + pytest, no model, no Chroma, no macOS needed
```

### 1.6 Configuration

Every knob is a field of `factory.settings.Settings`, overridden by the
environment variable in the first column (paths may be relative to the
repository). Defaults are the values below.

| Variable | Field | Default |
|---|---|---|
| `OLLAMA_URL` | `ollama_url` | `http://localhost:11434` |
| `AUTHOR_MODEL` | `author_model` | `mistral-nemo:12b-instruct-2407-q8_0` |
| `QA_MODEL` | `qa_model` | `qwen2.5:7b-instruct` |
| `EMBED_MODEL` | `embed_model` | `nomic-embed-text` |
| `NUM_CTX` | `num_ctx` | `8192` |
| `GESTURE_MODEL` | `gesture_model` | empty: the author model |
| `GESTURE_TEMPERATURE` | `gesture_temperature` | `0.3` |
| `BEATS_N` | `beats_n` | `3` |
| `PRUNING` | `pruning_enabled` | `1` (`0` disables the assemble pass) |
| `CHROMA_HOST` / `CHROMA_PORT` | `chroma_host` / `chroma_port` | `localhost` / `8000` |
| `CHROMA_COLLECTION` | `author_collection` | `auteur` |
| `CHROMA_SESSIONS` | `sessions_collection` | `sessions` |
| `BIBLE_DIR` | `bible_dir` | `bible/` |
| `STYLE_PATH` | `style_path` | `bible/style-auteur.md` |
| `API_HOST` / `API_PORT` | `api_host` / `api_port` | `0.0.0.0` / `8420` |
| `API_CORS_ORIGIN` | `cors_origin` | `*` |
| `API_OUTPUT_DIR` | `output_dir` | `output/` |
| `API_SLIDES_DIR` | `slides_dir` | `../talk/slides/dist` |
| `CHAT_TTL_S` | `chat_ttl_s` | `7200` |
| `STAGE_BUDGET_MIN` | `stage_budget_min` | `25` |
| `SWITCH_AFTER_SENTENCES` | `switch_after_sentences` | `2` |
| `AUDIO_SECONDS` | `audio_seconds` | `165` |
| `AUDIO_WORDS_PER_MINUTE` | `audio_words_per_minute` | `177` (measured on the clone) |
| `AUDIO_TOLERANCE_S` | `audio_tolerance_s` | `15` |
| `AUDIO_MAX_WORDS` | `audio_max_words` | `0`: derived from seconds × rate |
| `TTS_MODEL` | `tts_model` | `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit` |
| `TTS_VOICE_DIR` | `voice_dir` | `../TTS/voix` |
| `TTS_MAX_CHARS` | `tts_max_chars` | `400` |
| `TTS_PAUSE_S` | `tts_pause_s` | `0.6` |
| `ROLEPLAY_KEEP_TURNS` | `keep_turns` | `6` |
| `SESSIONS_DIR` | `sessions_dir` | `sessions/` |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | `telegram_token` / `telegram_chat_id` | empty: no byte leaves |
| `TELEGRAM_TIMEOUT_S` | `telegram_timeout_s` | `5` |
| `TELEGRAM_PERIOD_S` | `telegram_period_s` | `300` |
| `PREFLIGHT_MIN_DISK_GB` | `min_disk_gb` | `20` |
| `PREFLIGHT_MIN_SWAP_FREE_GB` | `min_swap_free_gb` | `2` |
| `PREFLIGHT_PAGEOUT_KB_S` | `pageout_block_kb_s` | `1024` |
| `PREFLIGHT_DAEMON_WARN_CPU` / `PREFLIGHT_DAEMON_BLOCK_CPU` | `daemon_warn_cpu` / `daemon_block_cpu` | `30` / `80` |
| `PREFLIGHT_PROBE_MODEL` | `probe_model` | `qwen2.5:7b-instruct` (empty: no probe) |
| `XP_DRAWS` / `XP_TEMPERATURE` / `XP_NUM_PREDICT` | `xp_draws` / `xp_temperature` / `xp_num_predict` | `3` / `0.7` / `300` |

Renamed at step 4 (former French names no longer read): `AUDIO_SECONDES` →
`AUDIO_SECONDS`, `AUDIO_DEBIT_MOTS_MIN` → `AUDIO_WORDS_PER_MINUTE`,
`AUDIO_MOTS_MAX` → `AUDIO_MAX_WORDS`, `BASCULE_APRES_PHRASES` →
`SWITCH_AFTER_SENTENCES`, `MODELE_GESTES` → `GESTURE_MODEL`, `TEMP_GESTES` →
`GESTURE_TEMPERATURE`, `ASSEMBLAGE` → `PRUNING`, `TELEGRAM_PERIODE_S` →
`TELEGRAM_PERIOD_S`, `TTS_MAX_CAR` → `TTS_MAX_CHARS`, `RP_KEEP_TURNS` →
`ROLEPLAY_KEEP_TURNS`, `DEMO_BUDGET_MIN` → `STAGE_BUDGET_MIN`, `XP_TIRAGES` /
`XP_TEMP` → `XP_DRAWS` / `XP_TEMPERATURE`.

## 2. Phone notifications (optional)

The operator's pager: phase, percentage, failures. Never any content of the
work (ADR-0015).

1. In Telegram, talk to **@BotFather** → `/newbot` → get a token `123456789:AAE...`.
2. Send one message to the bot from your phone.
3. Get the chat id:

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -m json.tool | grep -m1 '"id"'
```

4. Export both before starting the API:

```bash
export TELEGRAM_BOT_TOKEN="123456789:AAE..."
export TELEGRAM_CHAT_ID="987654321"
```

Without both variables, no byte leaves. Test on the watch before the day.

The openspec CLI collects anonymous usage statistics by default; set
`OPENSPEC_TELEMETRY=0` in the shell profile of the machine.

## 3. Generate a chapter

### Command line (measurement, tuning)

```bash
factory generate                       # chapter 7, preflight, chapter + WAV in output/
factory generate --seed 424242         # replayable drift draw and best-of
factory generate --no-render --quiet   # text only, no countdown (measure at its truest)
factory generate --brief "Une entrée du carnet…" --characters judith   # ad hoc chapter, generated plan
```

The graph does everything: preflight (first node, strict and timed), plan,
writing, gestures, review, repair, coherence, then the render node writes
`output/chapitre.md` and `output/chapitre.wav`. The profiling report at the
end is the measure that counts: total time against the 25-minute budget,
tokens per call, the context alarms (`ctx_need`, `ctx_truncated`).

`--skip-preflight` turns the gate into warnings (dev only, NEVER on stage);
`--no-preflight` skips the probes (a non-macOS machine, tests). `--out DIR`
moves the artifacts. Exit code 1 on a preflight refusal.

A chapter is generated from its `chapters/NN-slug/spec.yaml`; chapters 2 and
7 have one. A chapter without a spec makes `factory generate --chapter N` say
so and stop. When the owner's brief carries workshop vocabulary the lint bans
in output, the command reports it and goes on: the brief is the author's.

**Launch in the FOREGROUND.** A detached launch (`&`, `nohup`) inherits
`nice 5` under zsh's `BG_NICE`; against an indexing daemon the generation
takes three times longer. `unsetopt BG_NICE` before any detached launch.
With `| tee`, `set -o pipefail`, or an abort-on-failure never fires.

### Calibration stages (chapter 2, chapter 7 rehearsal)

```bash
factory calibrate --stage S7                 # the runs of the stage, one file each
factory calibrate --stage CH7 --only CH7-1 --seed 424242
factory eval grid experiments/runs/20260911-s7 450-600 2   # the lint grid, chapter 2 scope
factory eval journal experiments/runs/20260911-s7 2        # archive the failed draws
factory eval lint run.md                                   # one file
factory eval lint --references                             # the lint's self-test
```

Runs land under `experiments/runs/<date>-<stage>/` with a French frontmatter
(ADR-0003). Preflight runs before each run, blocking on the timed stages
(S6, S7, CH7) and warning on the others.

### Through the API (what the deck does)

```bash
factory serve                                 # listens on 0.0.0.0:8420
```

```bash
curl -X POST http://MACHINE:8420/generate     # 202, idempotent
curl  http://MACHINE:8420/status              # progress
curl  http://MACHINE:8420/chapter -o chapitre.md
curl  http://MACHINE:8420/audio   -o chapitre.wav
curl -X POST http://MACHINE:8420/cancel       # emergency exit
```

Live P90 at the keynote: ~6 min for chapter 7. Rehearsal measured 7.6 min
end to end (5 min generation, 2.6 min voice, cold engine at 0.60× real time).

In series, unload models and wait for a green `factory doctor` BEFORE EACH
RUN: the previous run leaves nemo warm and the swap guard refuses the next.

## 4. Demo assets

### 4.1 Pre-generated roleplay sessions

Replayed on stage, never generated live.

1. Open `http://MACHINE:8420/acteur` (or `factory chat --character judith`
   in a terminal).
2. Pick the character, hold the conversation.
3. **Enregistrer** → writes `sessions/<character>/<timestamp>.md`.
4. **Edit the file by hand**: prune weak lines in `## Transcription`. This is
   the step that makes the quality; curation beats any prompt rule.
5. Check with the page's replay selector.

Two sections, two uses: `## Ce qui s'est dit` is the character's memory
(indexed), `## Transcription` is what replays. Pruning one does not touch the
other.

### 4.2 Fallback chapter and audio

Produce them BEFORE the day and drop them in the deck repository:

```bash
curl http://localhost:8420/chapter -o public/fallback/chapitre.md
curl http://localhost:8420/audio   -o public/fallback/chapitre.wav
```

## 5. The day

| When | What |
|---|---|
| D-1 | Fallback assets produced, roleplay sessions curated, `caffeinate` tested |
| H-60 | **Reboot the Mac.** Let macOS maintenance finish (§0) |
| H-30 | Backends: Ollama, podman + ChromaDB, index up to date, seal re-proved |
| H-20 | `caffeinate -is &`, then `factory doctor`: all green |
| H-15 | `factory serve` in the FOREGROUND, Telegram variables exported; preheat the TTS |
| H-10 | Blank test: `POST /chat` on a character, one reply must come back |
| Section 3 | The deck sends `POST /generate`. The countdown starts |
| During | The watch receives the beats. On `❌ ÉCHEC`, prepare plan B |
| Section 7 | The deck collects `/chapter` and `/audio` by itself |
| After | `POST /cancel` if a generation lingers (it would block the actor mode) |

Actor mode does not coexist with generation: `POST /chat` answers `409`
while a chapter is being written. Play it before the launch or after the
collection.

## 6. Common failures

| Symptom | Probable cause | Remedy |
|---|---|---|
| Every generation 500 | Ollama survived a sleep but loads no model | `launchctl kickstart -k gui/$(id -u)/local.ollama` |
| Preflight: saturated swap (timing mode) | A run already ran since boot | `ollama stop <model>`, then `sudo purge`; reboot last |
| Preflight: macOS maintenance | Spotlight / Photos indexing | Wait, or §7 |
| Very slow generation, multi-minute holes | Maintenance daemon + background process | Relaunch in the foreground, machine idle |
| `/chapter` 204 | Generation not finished, or failed | `GET /status` → `error` field |
| `/audio` 204 but chapter present | TTS failed; the chapter stays valid | Deck falls back to embedded audio; nothing to do |
| `POST /chat` 409 | A chapter is generating | Wait for collection, or `POST /cancel` |
| ChromaDB unreachable | Podman machine stopped after reboot | `podman machine start`, `podman-compose up -d chromadb` |
| Run reports 374 s of compute for 45 min of wall time | Machine slept (battery Maintenance Sleep) | Plug in; the run is NOT COMPARABLE, redo it |

## 7. Cut macOS indexing (optional, day only)

```bash
sudo mdutil -a -i off      # suspend Spotlight indexing
# after the talk:
sudo mdutil -a -i on
ps -Ao %cpu,comm -r | head -5
```
