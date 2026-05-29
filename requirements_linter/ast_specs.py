"""Shared AST and layer logic for the RDE linter and YAML spec generator.

Used by:
  * ``build_code_artifacts`` in the linter;
  * spec generation from sources.

Layer names and the public-symbol rule stay in one place.
"""

from __future__ import annotations

import ast
from typing import cast
from pathlib import Path

from requirements_linter.naming import is_contract_public_name
from requirements_linter.http_routes import extract_http_endpoints_from_module

# First path segment under ``openvair/modules/<context>/`` must match a known
# DDD-style layer name (first path segment).
KNOWN_LAYER_NAMES = frozenset({
    'domain',
    'service_layer',
    'adapters',
    'entrypoints',
})

MODULE_FUNCTIONS_BUCKET = '$module_functions$'

# FastAPI endpoints list; shapes match helpers in ``http_routes``.
HTTP_ENDPOINTS_BUCKET = '$http_endpoints$'


def normalize_rel_path(path_str: str) -> str:
    """Normalize a relative key to POSIX with '/' and no leading './'."""
    p = Path(path_str)
    parts = []
    for part in p.parts:
        if part in ('.',):
            continue
        parts.append(part)
    return Path(*parts).as_posix() if parts else ''


def infer_layer(rel_path_normalized: str) -> str | None:
    """First path segment as layer name, or None if unknown."""
    if not rel_path_normalized:
        return None
    first = Path(rel_path_normalized).parts[0]
    return first if first in KNOWN_LAYER_NAMES else None


def iter_public_methods(class_node: ast.ClassDef) -> list[str]:
    """Public methods declared directly on the class body."""
    names: list[str] = []
    for child in class_node.body:
        if (
            isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            and is_contract_public_name(child.name)
        ):
            names.append(child.name)
    return sorted(set(names))


def iter_public_module_functions(module_node: ast.Module) -> list[str]:
    """Public top-level function/coroutine names in the module."""
    names: list[str] = []
    for node in module_node.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and is_contract_public_name(node.name)
        ):
            names.append(node.name)
    return sorted(set(names))


def _merge_functions_for_file(
    bucket: dict[str, list[str]],
    rel_file: str,
    functions: list[str],
) -> None:
    if rel_file not in bucket:
        bucket[rel_file] = sorted(set(functions))
        return
    merged = set(bucket[rel_file])
    merged.update(functions)
    bucket[rel_file] = sorted(merged)


def _merge_class_methods_layer_inplace(
    layer_dict: dict[str, object],
    class_name: str,
    methods: list[str],
) -> None:
    if class_name in (MODULE_FUNCTIONS_BUCKET, HTTP_ENDPOINTS_BUCKET):
        msg = (
            f'Class name clashes with sentinel keys '
            f'{MODULE_FUNCTIONS_BUCKET!r} / {HTTP_ENDPOINTS_BUCKET!r}'
        )
        raise ValueError(
            msg
        )

    prev_raw = layer_dict.get(class_name, [])
    if not isinstance(prev_raw, list) or len(prev_raw) == 0:
        layer_dict[class_name] = sorted(set(methods))
        return
    prev = {str(x) for x in prev_raw}
    prev.update(methods)
    layer_dict[class_name] = sorted(prev)


def _ensure_module_functions_bucket(
    layer_dict: dict[str, object],
) -> dict[str, list[str]]:
    mf_raw = layer_dict.setdefault(MODULE_FUNCTIONS_BUCKET, {})
    if not isinstance(mf_raw, dict):
        mf_raw = {}
        layer_dict[MODULE_FUNCTIONS_BUCKET] = mf_raw
    return cast('dict[str, list[str]]', mf_raw)


def _merge_public_classes_from_ast(
    layer_dict: dict[str, object],
    tree: ast.Module,
) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = iter_public_methods(node)
            _merge_class_methods_layer_inplace(layer_dict, node.name, methods)


def _extend_entrypoints_http(
    layer_dict: dict[str, object],
    tree: ast.Module,
    norm: str,
) -> None:
    ep_list = extract_http_endpoints_from_module(tree, norm)
    if not ep_list:
        return
    acc_raw = layer_dict.get(HTTP_ENDPOINTS_BUCKET)
    acc = acc_raw if isinstance(acc_raw, list) else []
    if not isinstance(acc_raw, list):
        layer_dict[HTTP_ENDPOINTS_BUCKET] = acc
    acc.extend(ep_list)


def _ingest_functions_and_classes(
    mf_bucket_inner: dict[str, list[str]],
    layer_dict: dict[str, object],
    norm: str,
    text: str,
) -> ast.Module:
    tree = ast.parse(text)
    funcs_here = iter_public_module_functions(tree)
    if funcs_here:
        _merge_functions_for_file(mf_bucket_inner, norm, funcs_here)
    _merge_public_classes_from_ast(layer_dict, tree)
    return tree


def _process_python_file_into_artifacts(
    artifacts: dict[str, dict[str, object]],
    raw_path: str,
    text: str,
) -> None:
    norm = normalize_rel_path(raw_path)
    layer = infer_layer(norm)
    if layer is None:
        return

    layer_dict = artifacts.setdefault(layer, {})
    mf_bucket_inner = _ensure_module_functions_bucket(layer_dict)
    tree = _ingest_functions_and_classes(
        mf_bucket_inner,
        layer_dict,
        norm,
        text,
    )

    if layer == 'entrypoints':
        _extend_entrypoints_http(layer_dict, tree, norm)


def build_code_artifacts(
    code_files: dict[str, str],
) -> dict[str, dict[str, object]]:
    """Build layer artifacts (classes, module functions, HTTP routes)."""
    artifacts: dict[str, dict[str, object]] = {}
    for raw_path, text in sorted(code_files.items()):
        _process_python_file_into_artifacts(artifacts, raw_path, text)
    return artifacts


def load_module_sources(module_root: Path) -> dict[str, str]:
    """Read all *.py under module root; skip tests/ and __pycache__."""
    out: dict[str, str] = {}
    if not module_root.is_dir():
        return out
    for path in sorted(module_root.rglob('*.py')):
        if '__pycache__' in path.parts:
            continue
        if 'tests' in path.parts:
            continue
        rel = path.relative_to(module_root).as_posix()
        out[rel] = path.read_text(encoding='utf-8')
    return out
