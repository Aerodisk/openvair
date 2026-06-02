"""Lint every contract in ``specs/`` against the matching Open vAIR module."""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

from requirements_linter._paths import REPO_ROOT, ensure_repo_root_on_syspath  # noqa: E402

ensure_repo_root_on_syspath()

from requirements_linter.entrypoints.cli import run_on_openvair_module  # noqa: E402
from requirements_linter.contract.spec_document import load_spec  # noqa: E402


def module_dir_for_spec(repo_root: Path, spec_path: Path, doc: dict) -> Path:
    """Return ``openvair/modules/<feature>`` for a spec file (``feature`` field or file stem)."""
    feat = doc.get('feature')
    if isinstance(feat, str) and feat.strip():
        return repo_root / 'openvair' / 'modules' / feat.strip()
    return repo_root / 'openvair' / 'modules' / spec_path.stem


def _rel_module_posix(root: Path, mod: Path) -> str:
    """Relative path of the module directory from ``root`` (for error messages)."""
    if not mod.is_dir():
        return mod.as_posix()
    return mod.resolve().relative_to(root.resolve()).as_posix()


def _iter_spec_files(specs_dir: Path) -> list[Path]:
    """List spec files: ``*.md`` first; orphan ``*.yaml`` only if no matching ``.md``."""
    md_files = sorted(specs_dir.glob('*.md'))
    if md_files:
        yaml_orphans = [
            y
            for y in sorted(specs_dir.glob('*.yaml'))
            if not (specs_dir / f'{y.stem}.md').is_file()
        ]
        return md_files + yaml_orphans
    return sorted(specs_dir.glob('*.yaml'))


def _lint_one_spec(
    root: Path,
    spec_path: Path,
    *,
    warn_extras: bool,
) -> int:
    """Lint one spec against its module. Return ``1`` on failure, ``0`` on success."""
    doc = load_spec(spec_path)
    mod = module_dir_for_spec(root, spec_path, doc)
    rel_mod = _rel_module_posix(root, mod)

    if not mod.is_dir():
        tag = '[RDE-LINTER]'
        msg = (
            f'{tag} {spec_path.name}: skip — bounded context directory missing '
            f'({rel_mod})'
        )
        print(msg, file=sys.stderr)  # noqa: T201
        return 1

    feature = doc.get('feature', spec_path.stem)
    result = run_on_openvair_module(
        spec_path.resolve(),
        mod.resolve(),
        warn_extras=warn_extras,
    )[1]

    if result.warnings:
        head = f'[RDE-LINTER] {spec_path.name} (feature={feature!r})'
        print(f'{head} WARNINGS (code not in contract):')  # noqa: T201
        for warn in result.warnings:
            print(f' ! {warn}')  # noqa: T201

    if result.errors:
        head = f'[RDE-LINTER] {spec_path.name} (feature={feature!r})'
        print(f'{head} SPECS MISMATCH FOUND:')  # noqa: T201
        for err in result.errors:
            print(f' - {err}')  # noqa: T201
        return 1

    print(f'[RDE-LINTER] OK {spec_path.name} (feature={feature!r})')  # noqa: T201
    return 0


def lint_all_specs(
    repo_root: Path | None = None,
    *,
    warn_extras: bool = True,
) -> int:
    """Lint all specs under ``repo_root/specs``. Return ``0`` if all pass, else ``1``."""
    root = repo_root or REPO_ROOT
    specs_dir = root / 'specs'
    if not specs_dir.is_dir():
        print(  # noqa: T201
            f'[RDE-LINTER] Specs directory not found: {specs_dir}',
            file=sys.stderr,
        )
        return 0

    spec_files = _iter_spec_files(specs_dir)
    if not spec_files:
        print(  # noqa: T201
            f'[RDE-LINTER] No spec files (*.md or *.yaml) in {specs_dir}',
            file=sys.stderr,
        )
        return 0

    exit_code = 0
    for spec_path in spec_files:
        if _lint_one_spec(root, spec_path, warn_extras=warn_extras):
            exit_code = 1
    return exit_code


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse arguments for batch lint (``--no-warn-extras``)."""
    parser = argparse.ArgumentParser(
        description='Lint all specs/*.md contracts against OpenVAir modules.',
    )
    parser.add_argument(
        '--no-warn-extras',
        action='store_true',
        help='Suppress warnings for code symbols not listed in the contract.',
    )
    return parser.parse_args(argv)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    raise SystemExit(
        lint_all_specs(warn_extras=not args.no_warn_extras),
    )
