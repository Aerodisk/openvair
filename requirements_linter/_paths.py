"""Repository root path and ``sys.path`` setup for script invocations."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def ensure_repo_root_on_syspath() -> None:
    """Put the repo root on ``sys.path`` so ``import requirements_linter`` works.

    Used when running ``python requirements_linter/rde_linter.py`` directly.
    """
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
