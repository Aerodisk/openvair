"""Thin CLI wrapper and compatibility exports for the RDE linter.

Run ``python requirements_linter/rde_linter.py`` with paths or ``--demo``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_BOOT = Path(__file__).resolve().parent.parent
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from requirements_linter._paths import ensure_repo_root_on_syspath  # noqa: E402

ensure_repo_root_on_syspath()

from requirements_linter.cli import (  # noqa: E402
    SYNTHETIC_SPEC_YAML_DEMO,
    SYNTHETIC_INLINE_SOURCES_DEMO,
    main as main_cli,
    load_spec,
    parse_cli,
    run_demo_pipeline,
    run_on_openvair_module,
)
from requirements_linter.analyzer import AstAnalyzer  # noqa: E402
from requirements_linter.comparator import Comparator  # noqa: E402

__all__ = [
    'SYNTHETIC_INLINE_SOURCES_DEMO',
    'SYNTHETIC_SPEC_YAML_DEMO',
    'AstAnalyzer',
    'Comparator',
    'load_spec',
    'parse_cli',
    'run_demo_pipeline',
    'run_on_openvair_module',
]

if __name__ == '__main__':
    raise SystemExit(main_cli())
