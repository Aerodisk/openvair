"""Backward-compatible entry point for single-module linting."""

from __future__ import annotations

import sys
from pathlib import Path

_BOOT = Path(__file__).resolve().parent.parent
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from requirements_linter.entrypoints.rde_linter import (  # noqa: E402
    AstAnalyzer,
    Comparator,
    SYNTHETIC_INLINE_SOURCES_DEMO,
    SYNTHETIC_SPEC_YAML_DEMO,
    load_spec,
    parse_cli,
    run_demo_pipeline,
    run_on_openvair_module,
)

if __name__ == '__main__':
    from requirements_linter.entrypoints.cli import main  # noqa: E402

    raise SystemExit(main())
