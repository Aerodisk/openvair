"""Read module sources and run ``build_code_artifacts`` on them."""

from __future__ import annotations

from typing import TYPE_CHECKING

from requirements_linter.core.ast_specs import (
    load_module_sources,
    build_code_artifacts,
)

if TYPE_CHECKING:
    from pathlib import Path


class AstAnalyzer:
    """Loads Python files for one Open vAIR module and parses them for the linter."""

    def __init__(self, code_files: dict[str, str]) -> None:
        """Store source texts keyed by path relative to the module root.

        Args:
            code_files: ``entrypoints/api.py`` → file contents, etc.
        """
        self.code_files = code_files
        self.code_artifacts: dict[str, dict[str, object]] = {}

    @classmethod
    def from_bounded_context_dir(cls, module_root: Path) -> AstAnalyzer:
        """Build an analyzer by reading all ``.py`` files under ``module_root``."""
        snapshot = load_module_sources(module_root)
        return cls(snapshot)

    def extract(self) -> dict[str, dict[str, object]]:
        """Parse ASTs and return the per-layer index (also stored on ``self``)."""
        self.code_artifacts = build_code_artifacts(self.code_files)
        return self.code_artifacts
