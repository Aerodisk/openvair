"""Command-line entry points for linting one module or running the built-in demo."""

from __future__ import annotations

import sys
import argparse
from typing import Any
from pathlib import Path

import yaml

from requirements_linter._paths import REPO_ROOT, ensure_repo_root_on_syspath

ensure_repo_root_on_syspath()

from requirements_linter.core.analyzer import AstAnalyzer  # noqa: E402
from requirements_linter.core.comparator import Comparator, CompareResult  # noqa: E402
from requirements_linter.contract.spec_document import load_spec  # noqa: E402

SYNTHETIC_SPEC_YAML_DEMO = """
meta:
  example: pedagogical_mini_contract
feature: demo_context
layers:
  domain:
    required_classes:
      - name: UserDomainModel
        methods:
          - validate
  service_layer:
    required_classes:
      - name: UserApplicationService
        methods:
          - create_user
          - delete_user
"""

SYNTHETIC_INLINE_SOURCES_DEMO = {
    'domain/models.py': '''
class UserDomainModel:
    def validate(self):
        """Public domain-layer contract method."""
''',
    'service_layer/application.py': '''
class UserApplicationService:
    def create_user(self): ...
    def delete_user(self): ...
''',
}


def parse_cli(argv: list[str]) -> argparse.Namespace:
    """Parse arguments for ``rde_linter.py`` (paths, ``--demo``, ``--no-warn-extras``)."""
    parser = argparse.ArgumentParser(
        description=(
            'RDE lint: load contract from specs/<feature>.md (``rde`` block) '
            'or legacy YAML and compare against openvair/modules/<feature>.'
        )
    )
    parser.add_argument(
        'spec_path',
        type=Path,
        nargs='?',
        default=REPO_ROOT / 'specs' / 'storage.md',
        help=(
            'Contract path: specs/<feature>.md or legacy .yaml '
            '(default: specs/storage.md)'
        ),
    )
    parser.add_argument(
        'module_dir',
        type=Path,
        nargs='?',
        default=REPO_ROOT / 'openvair' / 'modules' / 'storage',
        help='Bounded context root (default: openvair/modules/storage)',
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='In-memory demo contract; no disk reads.',
    )
    parser.add_argument(
        '--no-warn-extras',
        action='store_true',
        help=(
            'Do not print warnings for public symbols present in code but '
            'absent from the contract.'
        ),
    )
    return parser.parse_args(argv)


def run_on_openvair_module(
    spec_path: Path,
    module_dir: Path,
    *,
    warn_extras: bool = True,
) -> tuple[dict[str, dict[str, object]], CompareResult]:
    """Load ``spec_path``, parse Python under ``module_dir``, and run ``Comparator``."""
    reqs = load_spec(spec_path)
    analyzer = AstAnalyzer.from_bounded_context_dir(module_dir)
    artifacts = analyzer.extract()
    result = Comparator(reqs, artifacts).compare(report_extras=warn_extras)
    return artifacts, result


def run_demo_pipeline(*, warn_extras: bool = True) -> CompareResult:
    """Run the linter on built-in sample contract and source strings (no disk I/O)."""
    reqs = yaml.safe_load(SYNTHETIC_SPEC_YAML_DEMO)
    arts = AstAnalyzer(SYNTHETIC_INLINE_SOURCES_DEMO).extract()
    return Comparator(reqs, arts).compare(report_extras=warn_extras)


def _print_warnings(warnings: list[str]) -> None:
    """Print non-blocking warnings to stdout."""
    if not warnings:
        return
    print('[RDE-LINTER] WARNINGS (code not listed in contract):')  # noqa: T201
    for warn in warnings:
        print(f' ! {warn}')  # noqa: T201


def main(argv: list[str] | None = None) -> int:
    """Run demo or compare spec file vs module directory. Exit ``0`` ok, ``1`` on errors."""
    opts = parse_cli(argv if argv is not None else sys.argv[1:])
    warn_extras = not opts.no_warn_extras

    if opts.demo:
        result = run_demo_pipeline(warn_extras=warn_extras)
    else:
        spec_res = opts.spec_path.resolve()
        mod_res = opts.module_dir.resolve()
        result = run_on_openvair_module(
            spec_res,
            mod_res,
            warn_extras=warn_extras,
        )[1]

    _print_warnings(result.warnings)

    if result.errors:
        print('[RDE-LINTER] SPECS MISMATCH FOUND:')  # noqa: T201
        for err in result.errors:
            print(f' - {err}')  # noqa: T201
        return 1
    print('[RDE-LINTER] Specs are fulfilled — no mismatches found.')  # noqa: T201
    return 0
