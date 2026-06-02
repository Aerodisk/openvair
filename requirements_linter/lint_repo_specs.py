"""Backward-compatible entry point for batch linting (pre-commit)."""

from __future__ import annotations

import sys
from pathlib import Path

_BOOT = Path(__file__).resolve().parent.parent
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from requirements_linter.entrypoints.lint_repo_specs import (  # noqa: E402
    lint_all_specs,
    module_dir_for_spec,
    parse_args,
)

if __name__ == '__main__':
    _args = parse_args(sys.argv[1:])
    raise SystemExit(lint_all_specs(warn_extras=not _args.no_warn_extras))
