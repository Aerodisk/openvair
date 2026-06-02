"""Parse Python sources into a per-layer index for contract checking.

Reads files under ``openvair/modules/<feature>/``, groups them by DDD layer
(domain, service_layer, adapters, entrypoints), and records classes, top-level
functions, and (for entrypoints) HTTP routes.

Two keys in each layer dict are reserved for the linter itself, not for real
class names: ``MODULE_FUNCTIONS_BUCKET`` (file → function names) and
``HTTP_ENDPOINTS_BUCKET`` (list of routes).
"""

from __future__ import annotations

import ast
from typing import cast
from pathlib import Path

from requirements_linter.http.naming import is_contract_public_name
from requirements_linter.http.http_routes import extract_http_endpoints_from_module

# First path segment under the module root must be one of these folder names.
KNOWN_LAYER_NAMES = frozenset({
    'domain',
    'service_layer',
    'adapters',
    'entrypoints',
})

# Reserved key: maps relative file path → list of top-level function names.
MODULE_FUNCTIONS_BUCKET = '$module_functions$'

# Reserved key (entrypoints only): list of route description dicts.
HTTP_ENDPOINTS_BUCKET = '$http_endpoints$'


def normalize_rel_path(path_str: str) -> str:
    """Turn a path into POSIX form without a leading ``./``.

    Args:
        path_str: A path from the repo or from the contract ``relative_path`` field.
    """
    p = Path(path_str)
    parts = []
    for part in p.parts:
        if part in ('.',):
            continue
        parts.append(part)
    return Path(*parts).as_posix() if parts else ''


def infer_layer(rel_path_normalized: str) -> str | None:
    """Return the DDD layer name from the first segment of a file path.

    Example: ``entrypoints/api.py`` → ``entrypoints``. Returns ``None`` if the
    first segment is not a known layer folder.
    """
    if not rel_path_normalized:
        return None
    first = Path(rel_path_normalized).parts[0]
    return first if first in KNOWN_LAYER_NAMES else None


def iter_public_methods(class_node: ast.ClassDef) -> list[str]:
    """List public method names defined directly on a class body."""
    names: list[str] = []
    for child in class_node.body:
        if (
            isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            and is_contract_public_name(child.name)
        ):
            names.append(child.name)
    return sorted(set(names))


def iter_public_module_functions(module_node: ast.Module) -> list[str]:
    """List public function and async function names at module top level."""
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
    """Add or merge function names for one file into the module-functions map.

    Args:
        bucket: The dict stored under ``MODULE_FUNCTIONS_BUCKET`` for one layer.
        rel_file: Normalized path of the ``.py`` file being processed.
        functions: Function names found in that file on this pass.
    """
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
    """Store or update the method list for one class in a layer dict.

    Args:
        layer_dict: All parsed data for one layer (classes plus reserved keys).
        class_name: Name from ``ast.ClassDef.name``.
        methods: Method names to add for this class.

    Raises:
        ValueError: If ``class_name`` equals a reserved linter key string.
    """
    if class_name in (MODULE_FUNCTIONS_BUCKET, HTTP_ENDPOINTS_BUCKET):
        msg = (
            f'Class name clashes with sentinel keys '
            f'{MODULE_FUNCTIONS_BUCKET!r} / {HTTP_ENDPOINTS_BUCKET!r}'
        )
        raise ValueError(msg)

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
    """Return the per-file function map for this layer, creating it if missing.

    Args:
        layer_dict: Parsed data for one layer.

    Returns:
        ``layer_dict[MODULE_FUNCTIONS_BUCKET]`` as ``path → [function names]``.
    """
    mf_raw = layer_dict.setdefault(MODULE_FUNCTIONS_BUCKET, {})
    if not isinstance(mf_raw, dict):
        mf_raw = {}
        layer_dict[MODULE_FUNCTIONS_BUCKET] = mf_raw
    return cast('dict[str, list[str]]', mf_raw)


def _merge_public_classes_from_ast(
    layer_dict: dict[str, object],
    tree: ast.Module,
) -> None:
    """Find every public class in a module AST and record its methods."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = iter_public_methods(node)
            _merge_class_methods_layer_inplace(layer_dict, node.name, methods)


def _extend_entrypoints_http(
    layer_dict: dict[str, object],
    tree: ast.Module,
    norm: str,
) -> None:
    """Append FastAPI routes parsed from one entrypoints file to the HTTP list."""
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
    """Parse one file and update the layer's function map and class entries.

    Returns:
        The parsed module AST (reused for HTTP extraction on entrypoints).
    """
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
    """Parse one ``.py`` file and merge results into the full module index."""
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
    """Parse every file in ``code_files`` and build the full per-layer index.

    Args:
        code_files: ``relative/path.py`` → file source text.

    Returns:
        ``{layer_name: layer_dict}`` used by ``Comparator``.
    """
    artifacts: dict[str, dict[str, object]] = {}
    for raw_path, text in sorted(code_files.items()):
        _process_python_file_into_artifacts(artifacts, raw_path, text)
    return artifacts


def load_module_sources(module_root: Path) -> dict[str, str]:
    """Read all ``*.py`` files under a module directory (skip tests and cache).

    Args:
        module_root: Path like ``openvair/modules/user/``.

    Returns:
        Relative path → source text. Empty dict if the directory does not exist.
    """
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
