# ADR-0009 — Ollama on the host, bound to loopback, run by a project launchd agent

Date: 2026-08-06. Status: accepted.

## Context

Ollama needs direct Apple Silicon GPU access, so it runs outside containers.
The containerised indexer must still reach it. It was long believed this
required `OLLAMA_HOST=0.0.0.0`; on a conference WiFi that exposes an
unauthenticated API to the whole network. Separately, `brew services start`
regenerates Ollama's plist and erases hand-added variables.

## Decision

- Ollama listens on `127.0.0.1` only. With podman 5 (applehv + gvproxy),
  `host.containers.internal` resolves to gvproxy itself, which composes the
  connection FROM the host and reaches loopback. Verified end to end: host
  200, LAN refused, container → `/api/embed` 768 dims.
- Ollama is run by the project's launchd agent (`scripts/local.ollama.plist`),
  not by `brew services`. The agent fixes `OLLAMA_HOST`,
  `OLLAMA_MAX_LOADED_MODELS=2`, `OLLAMA_NUM_PARALLEL=1`. Never return to
  `brew services`: the two agents would fight for port 11434.
- The orchestrator runs in a host venv (fast iteration, direct localhost to
  Ollama and Chroma); containerisation is a packaging step, not a
  prerequisite.

## Consequences

- Remedy for the post-sleep failure where the daemon lives but cannot start
  `llama-server`: `launchctl kickstart -k gui/$(id -u)/local.ollama`.
- Preflight probes generation for real (ADR-0018), because `/api/ps` answers
  200 with an empty list in that state.
