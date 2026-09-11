"""Repository paths, resolved once.

The package lives in ``src/factory/``; author material (``bible/``,
``chapters/``), experiments and outputs live at the repository root. In an
editable install the root is two levels above this file; ``FACTORY_ROOT``
overrides it (containers, non-editable installs).
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(os.environ.get("FACTORY_ROOT") or Path(__file__).resolve().parents[2])
BIBLE_DIR = REPO_ROOT / "bible"
CHAPTERS_DIR = REPO_ROOT / "chapters"
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
SESSIONS_DIR = REPO_ROOT / "sessions"
OUTPUT_DIR = REPO_ROOT / "output"
DATA_DIR = Path(__file__).resolve().parent / "eval" / "data"
