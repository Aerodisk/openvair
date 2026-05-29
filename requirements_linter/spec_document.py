"""Load RDE contracts from Markdown (``rde`` fence) or legacy YAML files."""

from __future__ import annotations

import re
from typing import Any, cast
from pathlib import Path

import yaml

from requirements_linter.http_routes import join_fastapi_route_path

_RDE_FENCE_RE = re.compile(
    r'^```[ \t]*rde[ \t]*\r?\n(.*)^```',
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

KNOWN_LAYER_NAMES = frozenset({
    'domain',
    'service_layer',
    'adapters',
    'entrypoints',
})


def extract_rde_block(markdown_text: str) -> str:
    """Return inner YAML from the first `` ```rde `` fenced block.

    Raises:
        ValueError: When no ``rde`` fence is present.
    """
    match = _RDE_FENCE_RE.search(markdown_text)
    if not match:
        msg = (
            'Markdown spec must contain a fenced code block opened with '
            '```rde (requirements contract in YAML).'
        )
        raise ValueError(msg)
    return match.group(1).strip()


def _layer_uses_rrd_shorthand(layer_data: dict[str, Any]) -> bool:
    return (
        'classes' in layer_data
        or 'module_functions' in layer_data
        or 'http' in layer_data
    )


def _normalize_http_endpoints(http_block: dict[str, Any]) -> list[dict[str, Any]]:
    prefix_raw = http_block.get('router_prefix')
    prefix = str(prefix_raw) if prefix_raw is not None else None
    endpoints_raw = http_block.get('endpoints', [])
    if not isinstance(endpoints_raw, list):
        return []

    out: list[dict[str, Any]] = []
    for ep in endpoints_raw:
        if not isinstance(ep, dict):
            continue
        route_path = str(ep.get('path', ''))
        if prefix and route_path and not route_path.startswith(prefix):
            full_path = join_fastapi_route_path(prefix, route_path)
        else:
            full_path = route_path if route_path.startswith('/') else f'/{route_path}'

        row: dict[str, Any] = {
            'method': str(ep.get('method', '')).upper(),
            'path': full_path,
            'handler': str(ep.get('handler', '')),
        }
        params = ep.get('parameters')
        if isinstance(params, list) and params:
            row['parameters'] = params
        out.append(row)
    return out


def _normalize_layer(layer_data: dict[str, Any]) -> dict[str, Any]:
    if not _layer_uses_rrd_shorthand(layer_data):
        return layer_data

    out: dict[str, Any] = {}

    classes_raw = layer_data.get('classes', {})
    if isinstance(classes_raw, dict) and classes_raw:
        req_cls: list[dict[str, Any]] = []
        for name, spec in sorted(classes_raw.items(), key=lambda item: item[0]):
            methods: list[str] = []
            if isinstance(spec, dict):
                raw_methods = spec.get('methods', [])
                if isinstance(raw_methods, list):
                    methods = [str(m) for m in raw_methods]
            req_cls.append({'name': str(name), 'methods': methods})
        out['required_classes'] = req_cls
    elif 'required_classes' in layer_data:
        out['required_classes'] = layer_data['required_classes']

    mf_raw = layer_data.get('module_functions', {})
    if isinstance(mf_raw, dict) and mf_raw:
        mf_entries = [
            {
                'relative_path': str(rel_path),
                'functions': (
                    [str(f) for f in fn_list]
                    if isinstance(fn_list, list)
                    else []
                ),
            }
            for rel_path, fn_list in sorted(mf_raw.items(), key=lambda item: item[0])
        ]
        out['required_module_functions'] = mf_entries
    elif 'required_module_functions' in layer_data:
        out['required_module_functions'] = layer_data['required_module_functions']

    http_raw = layer_data.get('http')
    if isinstance(http_raw, dict):
        eps = _normalize_http_endpoints(http_raw)
        if eps:
            out['required_http_endpoints'] = eps
    elif 'required_http_endpoints' in layer_data:
        out['required_http_endpoints'] = layer_data['required_http_endpoints']

    for key, val in layer_data.items():
        if key in {
            'classes',
            'module_functions',
            'http',
            'required_classes',
            'required_module_functions',
            'required_http_endpoints',
        }:
            continue
        out[key] = val
    return out


def normalize_contract_document(doc: object) -> dict[str, Any]:
    """Accept standard contract YAML or RRD shorthand (``classes``, ``http``, …)."""
    if not isinstance(doc, dict):
        msg = f'Contract root must be a mapping, got {type(doc).__name__}.'
        raise TypeError(msg)

    layers_in = doc.get('layers')
    if not isinstance(layers_in, dict):
        msg = "Contract must include a 'layers' mapping."
        raise ValueError(msg)

    layers_out: dict[str, Any] = {}
    for layer_name, layer_data in layers_in.items():
        if layer_name not in KNOWN_LAYER_NAMES:
            msg = (
                f"Unknown layer {layer_name!r}; expected one of "
                f'{sorted(KNOWN_LAYER_NAMES)}.'
            )
            raise ValueError(msg)
        if not isinstance(layer_data, dict):
            msg = f'Layer {layer_name!r} must be a mapping.'
            raise TypeError(msg)
        layers_out[layer_name] = _normalize_layer(layer_data)

    feature = doc.get('feature')
    if not isinstance(feature, str) or not feature.strip():
        msg = "Contract must include non-empty 'feature'."
        raise ValueError(msg)

    meta = doc.get('meta')
    meta_out = meta if isinstance(meta, dict) else {}

    return {
        'meta': meta_out,
        'feature': feature.strip(),
        'layers': layers_out,
    }


def load_spec(path: Path) -> dict[str, Any]:
    """Load a contract from ``.md`` (``rde`` block) or legacy ``.yaml`` / ``.yml``."""
    text = path.read_text(encoding='utf-8')
    suffix = path.suffix.lower()
    if suffix in {'.md', '.markdown'}:
        inner = extract_rde_block(text)
        doc = yaml.safe_load(inner)
    elif suffix in {'.yaml', '.yml'}:
        doc = yaml.safe_load(text)
    else:
        msg = (
            f'Unsupported spec extension {suffix!r} for {path}; '
            'use .md, .yaml, or .yml.'
        )
        raise ValueError(msg)

    if doc is None:
        msg = f'Empty contract in {path}.'
        raise ValueError(msg)
    return normalize_contract_document(doc)


def contract_to_markdown(doc: dict[str, Any], *, title: str | None = None) -> str:
    """Render a contract dict as a Markdown file with an ``rde`` fence."""
    feature = str(doc.get('feature', 'unknown'))
    heading = title or f'Open vAIR contract: {feature}'
    meta = doc.get('meta') or {}
    source = meta.get('source', f'openvair/modules/{feature}')
    dumped = yaml.safe_dump(
        doc,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    ).strip()
    return (
        f'# {heading}\n\n'
        f'Архитектурный контракт модуля `{feature}` для RDE-линтера.\n'
        f'Источник кода: `{source}`.\n\n'
        f'Машиночитаемый контракт — блок ``rde`` ниже.\n\n'
        f'```rde\n{dumped}\n```\n'
    )
