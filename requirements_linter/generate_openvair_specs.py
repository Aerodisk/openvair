#!/usr/bin/env python3

"""Emit a Markdown bounded-context spec (``rde`` block) from OpenVAir sources.

``load_module_sources`` plus ``build_code_artifacts`` reproduce the linter view.
Regenerate when the intended public contract changes.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

_BOOT = Path(__file__).resolve().parent.parent
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from requirements_linter._paths import (  # noqa: E402
    REPO_ROOT,
    ensure_repo_root_on_syspath,
)

ensure_repo_root_on_syspath()

from requirements_linter.ast_specs import (  # noqa: E402
    HTTP_ENDPOINTS_BUCKET,
    MODULE_FUNCTIONS_BUCKET,
    load_module_sources,
    build_code_artifacts,
)
from requirements_linter.spec_document import contract_to_markdown  # noqa: E402


def _serialize_endpoint_for_yaml(ep: dict[str, object]) -> dict[str, object]:
    """Serialize one endpoint dict for YAML (drop lint-only ``source_file``)."""
    raw_params = ep.get('parameters') or []
    params_in = raw_params if isinstance(raw_params, list) else []
    params_out = []
    for p in sorted(params_in, key=lambda row: str(row.get('name', ''))):
        if not isinstance(p, dict):
            continue
        params_out.append(
            {
                'name': p['name'],
                'kind': p['kind'],
                'required': p['required'],
                'type_hint': p.get('type_hint') or '',
            }
        )
    return {
        'method': ep['method'],
        'path': ep['path'],
        'handler': ep['handler'],
        'parameters': params_out,
    }


def _layer_classes_map(layer_bucket: dict[str, object]) -> dict[str, list[str]]:
    sentinel = frozenset({MODULE_FUNCTIONS_BUCKET, HTTP_ENDPOINTS_BUCKET})
    classes: dict[str, list[str]] = {}
    for k, v_obj in sorted(layer_bucket.items(), key=lambda item: item[0]):
        if k in sentinel:
            continue
        if isinstance(v_obj, list):
            classes[str(k)] = [str(x) for x in v_obj]
    return classes


def _sorted_endpoints_yaml(
    layer_bucket: dict[str, object],
) -> list[dict[str, object]]:
    eps_raw = layer_bucket.get(HTTP_ENDPOINTS_BUCKET, [])
    eps_in = eps_raw if isinstance(eps_raw, list) else []
    rows = [
        _serialize_endpoint_for_yaml(ep)
        for ep in eps_in
        if isinstance(ep, dict)
    ]
    rows.sort(
        key=lambda e: (
            str(e.get('path', '')),
            str(e.get('method', '')),
            str(e.get('handler', '')),
        )
    )
    return rows


def artifacts_to_contract_layers(
    artifacts: dict[str, dict[str, object]],
) -> dict[str, dict]:
    """Map ``build_code_artifacts`` output into YAML ``layers`` blocks."""
    layers_out: dict[str, dict] = {}
    for layer_name in sorted(artifacts.keys()):
        layer_bucket = artifacts[layer_name]

        mf_raw = layer_bucket.get(MODULE_FUNCTIONS_BUCKET, {})
        mf_map: dict[str, list[str]] = (
            mf_raw if isinstance(mf_raw, dict) else {}
        )

        classes = _layer_classes_map(layer_bucket)
        req_cls = [
            {'name': cname, 'methods': methods}
            for cname, methods in sorted(classes.items())
        ]
        layer_doc: dict[str, object] = {'required_classes': req_cls}

        mf_entries = [
            {'relative_path': rp, 'functions': fn_list}
            for rp, fn_list in sorted(mf_map.items())
        ]
        if mf_entries:
            layer_doc['required_module_functions'] = mf_entries

        endpoints_yaml = _sorted_endpoints_yaml(layer_bucket)
        if endpoints_yaml:
            layer_doc['required_http_endpoints'] = endpoints_yaml

        layers_out[layer_name] = layer_doc

    return layers_out


def build_spec_document(
    feature_name: str,
    module_root: Path,
    repo_root: Path,
) -> dict:
    """Read the bounded context on disk and build the document before YAML dump.

    Args:
        feature_name: Context folder name (becomes ``feature`` in YAML).
        module_root: ``openvair/modules/<feature>``.
        repo_root: Repository root for ``meta.source`` (relative when possible).

    Returns:
        Dict ready for ``yaml.safe_dump``.
    """
    sources = load_module_sources(module_root)
    artifacts = build_code_artifacts(sources)
    mod_res = module_root.resolve()
    repo_res = repo_root.resolve()
    try:
        rel_meta = mod_res.relative_to(repo_res)
        source_meta = rel_meta.as_posix()
    except ValueError:
        source_meta = str(mod_res)
    maint = 'Snapshot from disk. Trim after review to the public contract.'
    return {
        'meta': {
            'source': source_meta,
            'maintainer_notes': maint,
        },
        'feature': feature_name,
        'layers': artifacts_to_contract_layers(artifacts),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI args for the spec generator."""
    repo_default = REPO_ROOT

    parser = argparse.ArgumentParser(
        description=(
            'Generate specs/<feature>.md (``rde`` contract) for a bounded '
            'context (subdirectory openvair/modules/<feature>).'
        )
    )
    parser.add_argument(
        '--feature',
        metavar='NAME',
        required=True,
        help='Context directory name, e.g. storage or virtual_machines',
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=repo_default,
        help=(
            'Repo root with openvair/ (default: parent of requirements_linter/)'
        ),
    )
    parser.add_argument(
        '--out-dir',
        type=Path,
        default=repo_default / 'specs',
        help=(
            'Directory for <feature>.md (default: specs/ under repo root)'
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry for writing ``<feature>.md`` under ``--out-dir``."""
    opts = parse_args(argv if argv is not None else sys.argv[1:])

    module_root = opts.repo_root / 'openvair' / 'modules' / opts.feature
    doc = build_spec_document(
        opts.feature,
        module_root.resolve(),
        opts.repo_root.resolve(),
    )

    opts.out_dir.mkdir(parents=True, exist_ok=True)
    out_file = opts.out_dir / f'{opts.feature}.md'

    out_file.write_text(contract_to_markdown(doc), encoding='utf-8')
    print(f'Wrote {out_file}')  # noqa: T201
    return 0


if __name__ == '__main__':
    sys.exit(main())
