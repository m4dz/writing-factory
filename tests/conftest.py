"""Shared fixtures: the fake model, the fake vector store, a quiet progress sink.

The code is the installed ``factory`` package; only ``tests/`` itself is added
to the path so that ``fakes`` and ``snapshots`` import as modules.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
# A stray Telegram token in the developer's shell must never make a test post.
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""

sys.path.insert(0, str(REPO / "tests"))

from fakes.chroma import FakeChromaClient  # noqa: E402
from fakes.llm import FakeModel  # noqa: E402


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
    """Route every retrieval call to the fake collections; no embeddings."""
    from factory.retrieval import context as retrieval
    from factory.roleplay import session as roleplay

    monkeypatch.setattr(retrieval, "_client", bible_chroma)
    monkeypatch.setattr(retrieval, "embed", lambda text: [0.0] * 768)
    # `from retrieval import embed` bound the name in roleplay at import time.
    monkeypatch.setattr(roleplay, "embed", lambda text: [0.0] * 768)
    retrieval.vider_routage()
    bible_chroma.reset_sessions()
    return bible_chroma


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

    sink = progress.Progress(actif=False)
    monkeypatch.setattr(progress, "SINK", sink)
    return sink
