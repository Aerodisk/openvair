"""Tests for ``lint_repo_specs`` batch driver."""

from __future__ import annotations

from pathlib import Path

from requirements_linter.entrypoints.cli import run_on_openvair_module
from requirements_linter.entrypoints.lint_repo_specs import (
    lint_all_specs,
    module_dir_for_spec,
)
from requirements_linter.contract.spec_document import contract_to_markdown, load_spec


def test_module_dir_for_spec_prefers_feature_key(tmp_path: Path) -> None:
    """``feature:`` in the contract wins over the file stem."""
    spec_path = tmp_path / 'storage.md'
    contract = {
        'feature': 'custom_name',
        'meta': {'source': 'openvair/modules/custom_name'},
        'layers': {},
    }
    spec_path.write_text(contract_to_markdown(contract), encoding='utf-8')
    doc = load_spec(spec_path)
    got = module_dir_for_spec(tmp_path, spec_path, doc)
    assert got == tmp_path / 'openvair' / 'modules' / 'custom_name'


def test_module_dir_fallback_to_stem(tmp_path: Path) -> None:
    """Without ``feature``, use ``<stem>`` as module folder name."""
    spec_path = tmp_path / 'user.md'
    contract = {
        'feature': 'user',
        'meta': {'source': 'openvair/modules/user'},
        'layers': {},
    }
    spec_path.write_text(contract_to_markdown(contract), encoding='utf-8')
    got = module_dir_for_spec(tmp_path, spec_path, {})
    assert got == tmp_path / 'openvair' / 'modules' / 'user'


def test_lint_all_specs_mini_repo(tmp_path: Path) -> None:
    """Healthy tiny repo exits zero from ``lint_all_specs``."""
    specs = tmp_path / 'specs'
    specs.mkdir()
    feat = tmp_path / 'openvair' / 'modules' / 'tiny'
    (feat / 'domain').mkdir(parents=True)
    body = 'class Foo:\n    def bar(self):\n        pass\n'
    (feat / 'domain' / 'x.py').write_text(body, encoding='utf-8')
    contract = {
        'feature': 'tiny',
        'meta': {'source': 'openvair/modules/tiny'},
        'layers': {
            'domain': {
                'required_classes': [{'name': 'Foo', 'methods': ['bar']}],
            },
        },
    }
    (specs / 'tiny.md').write_text(
        contract_to_markdown(contract),
        encoding='utf-8',
    )

    code = lint_all_specs(tmp_path)
    assert code == 0


def test_lint_all_specs_reports_mismatch(tmp_path: Path) -> None:
    """Stale spec vs code returns exit code ``1``."""
    specs = tmp_path / 'specs'
    specs.mkdir()
    feat = tmp_path / 'openvair' / 'modules' / 'bad'
    (feat / 'domain').mkdir(parents=True)
    py = 'class Foo:\n    def bar(self):\n        pass\n'
    (feat / 'domain' / 'x.py').write_text(py, encoding='utf-8')

    contract = {
        'feature': 'bad',
        'meta': {'source': 'openvair/modules/bad'},
        'layers': {
            'domain': {
                'required_classes': [{'name': 'Foo', 'methods': ['nope']}],
            },
        },
    }
    (specs / 'bad.md').write_text(
        contract_to_markdown(contract),
        encoding='utf-8',
    )

    assert lint_all_specs(tmp_path) == 1


def test_run_on_real_user_module_if_present() -> None:
    """Optional smoke test when the real ``user`` module exists."""
    repo = Path(__file__).resolve().parents[2]
    spec = repo / 'specs' / 'user.md'
    mod = repo / 'openvair' / 'modules' / 'user'
    if not spec.is_file() or not mod.is_dir():
        return
    _, result = run_on_openvair_module(spec.resolve(), mod.resolve())
    assert result.errors == []
