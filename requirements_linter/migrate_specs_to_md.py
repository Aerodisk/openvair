#!/usr/bin/env python3
"""One-shot migration: ``specs/*.yaml`` -> ``specs/*.md`` with ``rde`` blocks."""

from __future__ import annotations

import sys
from pathlib import Path

_BOOT = Path(__file__).resolve().parent.parent
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

import yaml  # noqa: E402

from requirements_linter._paths import REPO_ROOT  # noqa: E402
from requirements_linter.spec_document import (  # noqa: E402
    contract_to_markdown,
    normalize_contract_document,
)


def migrate_specs_dir(specs_dir: Path) -> int:
    """Convert every ``*.yaml`` in ``specs_dir`` to ``*.md`` and remove YAML."""
    converted = 0
    for yml in sorted(specs_dir.glob('*.yaml')):
        doc = yaml.safe_load(yml.read_text(encoding='utf-8')) or {}
        contract = normalize_contract_document(doc)
        md_path = specs_dir / f'{yml.stem}.md'
        md_path.write_text(contract_to_markdown(contract), encoding='utf-8')
        yml.unlink()
        print(f'Converted {yml.name} -> {md_path.name}')  # noqa: T201
        converted += 1
    return converted


if __name__ == '__main__':
    target = REPO_ROOT / 'specs'
    count = migrate_specs_dir(target)
    print(f'Done: {count} file(s).')  # noqa: T201
