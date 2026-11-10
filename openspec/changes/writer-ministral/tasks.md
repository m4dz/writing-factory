# Tasks: writer-ministral

- [x] Tag `ministral3-14b-q5` on the stage machine (`ollama cp` of the
      measured tag, digest `87501e5270dc`); Modelfile versioned.
- [x] Default `author_model`; docs; ADR-0029.
- [x] Snapshots: only the gesture calls' `model=` header moves.
- [x] `make check` green.
- [ ] Actor-mode check: one `factory chat --character judith` session with
      M (in character, French, memory written and reloaded). Blocked
      2026-11-10: the Podman VM does not start (ssh handshake), so no
      ChromaDB.
