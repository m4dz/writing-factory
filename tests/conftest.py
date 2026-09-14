"""Shared fixtures: the fake model, the fake vector store, a quiet progress sink.

The code is the installed ``factory`` package; ``fakes`` and ``snapshots``
import as modules because ``pyproject.toml`` adds ``tests/`` to pytest's
``pythonpath``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from fakes.chroma import FakeChromaClient
from fakes.llm import FakeModel

REPO = Path(__file__).resolve().parent.parent
# A stray Telegram token in the developer's shell must never make a test post.
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""


def pytest_addoption(parser):
    parser.addoption(
        "--update-snapshots", action="store_true", default=False,
        help="rewrite the golden files under tests/snapshots instead of comparing",
    )


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO


@pytest.fixture(scope="session")
def bible_chroma() -> FakeChromaClient:
    """One in-memory Chroma built from the indexer's own chunker over bible/."""
    return FakeChromaClient.from_bible(REPO / "bible")


@pytest.fixture
def fake_chroma(monkeypatch, bible_chroma):
    """Route every retrieval call to a fresh copy of the fake collections; no
    embeddings. A copy per test: the narrative-state node and `promote` upsert
    chunks, and one test's index must not become the next test's bible."""
    import copy

    from factory.retrieval import context as retrieval
    from factory.roleplay import session as roleplay

    client = copy.deepcopy(bible_chroma)
    monkeypatch.setattr(retrieval, "_client", client)
    monkeypatch.setattr(retrieval, "embed", lambda text: [0.0] * 768)
    # `from retrieval import embed` bound the name in roleplay at import time.
    monkeypatch.setattr(roleplay, "embed", lambda text: [0.0] * 768)
    retrieval.clear_routing()
    client.reset_sessions()
    return client


@pytest.fixture
def fake_model(monkeypatch):
    """Replace the one model client.

    Every module calls ``factory.infra.ollama.chat`` / ``chat_turns`` /
    ``unload``, which delegate to ``ollama.client`` at call time; patching the
    client's three methods covers every caller.
    """
    from factory.infra import ollama as llm

    model = FakeModel()
    monkeypatch.setattr(llm.client, "chat", model.chat, raising=True)
    monkeypatch.setattr(llm.client, "chat_turns", model.chat_turns, raising=True)
    monkeypatch.setattr(llm.client, "unload", lambda *a, **k: True, raising=True)
    return model


@pytest.fixture
def quiet_progress(monkeypatch):
    """A fresh, inactive progress sink whose notes the test can read."""
    from factory.infra import progress

    sink = progress.Progress(active=False)
    monkeypatch.setattr(progress, "SINK", sink)
    return sink
