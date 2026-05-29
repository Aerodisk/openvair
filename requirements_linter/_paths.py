"""Prepend repo root on ``sys.path`` for ``python script.py`` style runs."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def ensure_repo_root_on_syspath() -> None:
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
