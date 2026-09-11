"""Test wiring for the CURRENT layout (before packaging, revamp step 4).

The code still lives in three script directories linked by ``sys.path``
insertions. The tests reproduce that wiring here, once, so that every test
module imports ``graph``, ``qa``, ``lint_style``, ``index`` the way the code
does. When step 4 moves the code into ``src/factory``, this file shrinks to the
fixtures and the imports in the tests are updated with the moves.

Several modules resolve data files relative to the CURRENT WORKING DIRECTORY
(``bible/style-auteur.md``, ``outillage/lexique-fuite.txt``, the pilot table).
The session runs from the repository root for that reason.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
for sub in ("orchestrator", "outillage", "indexer"):
    p = str(REPO / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

os.chdir(REPO)
os.environ.setdefault("BIBLE_DIR", str(REPO / "bible"))
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
    import retrieval
    import roleplay

    monkeypatch.setattr(retrieval, "_client", bible_chroma)
    monkeypatch.setattr(retrieval, "embed", lambda text: [0.0] * 768)
    # `from retrieval import embed` bound the name in roleplay at import time.
    monkeypatch.setattr(roleplay, "embed", lambda text: [0.0] * 768)
    retrieval.vider_routage()
    bible_chroma.reset_sessions()
    return bible_chroma


@pytest.fixture
def fake_model(monkeypatch):
    """Replace every model call in every module that bound ``chat`` at import.

    ``from llm import chat`` copies the function into the importing module, so
    patching ``llm.chat`` alone would leave ``graph.chat`` and ``qa.chat``
    pointing at the real client. Each binding is patched.
    """
    import graph
    import llm
    import qa
    import roleplay

    model = FakeModel()
    for mod in (llm, graph, qa, roleplay):
        monkeypatch.setattr(mod, "chat", model.chat, raising=True)
    for mod in (llm, roleplay):
        monkeypatch.setattr(mod, "chat_turns", model.chat_turns, raising=True)
    monkeypatch.setattr(graph, "unload", lambda *a, **k: True)
    monkeypatch.setattr(llm, "unload", lambda *a, **k: True)
    return model


@pytest.fixture
def quiet_progress(monkeypatch):
    """A fresh, inactive progress sink whose notes the test can read."""
    import progress

    sink = progress.Progress(actif=False)
    monkeypatch.setattr(progress, "SINK", sink)
    return sink
