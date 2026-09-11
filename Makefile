PY ?= .venv/bin/python
RUFF ?= .venv/bin/ruff

.PHONY: venv check lint test snapshots

venv:
	python3 -m venv .venv
	.venv/bin/pip install -q -e ".[test]"

lint:
	$(RUFF) check .
	$(RUFF) check --select E,F,I,W tests

test:
	$(PY) -m pytest

# The invariant of the refactor: served prompts and assembled chapters must
# match the golden files. Regenerate ONLY when a change intends to move them.
snapshots:
	$(PY) -m pytest tests/snapshots --update-snapshots

check: lint test
