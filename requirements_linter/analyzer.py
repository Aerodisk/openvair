"""Scan bounded-context sources into ``code_artifacts``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from requirements_linter.ast_specs import (
    load_module_sources,
    build_code_artifacts,
)

if TYPE_CHECKING:
    from pathlib import Path


class AstAnalyzer:
    """Contract graph builder shared by the YAML generator and Comparator."""

    def __init__(self, code_files: dict[str, str]) -> None:
        """Store mapping ``relative_path -> source`` for one context."""
        self.code_files = code_files
        self.code_artifacts: dict[str, dict[str, object]] = {}

    @classmethod
    def from_bounded_context_dir(cls, module_root: Path) -> AstAnalyzer:
        """Load ``*.py`` under ``module_root`` into a new analyzer."""
        snapshot = load_module_sources(module_root)
        return cls(snapshot)

    def extract(self) -> dict[str, dict[str, object]]:
        """Parse sources and cache ``build_code_artifacts`` output."""
        self.code_artifacts = build_code_artifacts(self.code_files)
        return self.code_artifacts
