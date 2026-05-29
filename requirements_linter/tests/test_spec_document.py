"""Tests for Markdown ``rde`` contract loading."""

from __future__ import annotations

from pathlib import Path

import yaml

from requirements_linter.spec_document import (
    contract_to_markdown,
    extract_rde_block,
    load_spec,
    normalize_contract_document,
)


def test_extract_rde_block() -> None:
    """Parser finds the fenced ``rde`` YAML body."""
    md = '# Title\n\n```rde\nfeature: tiny\nlayers: {}\n```\n'
    inner = extract_rde_block(md)
    doc = yaml.safe_load(inner)
    assert doc['feature'] == 'tiny'


def test_load_spec_from_markdown_file(tmp_path: Path) -> None:
    """Round-trip markdown spec file through ``load_spec``."""
    contract = {
        'feature': 'demo',
        'meta': {'source': 'openvair/modules/demo'},
        'layers': {
            'domain': {
                'required_classes': [{'name': 'Foo', 'methods': ['bar']}],
            },
        },
    }
    md_path = tmp_path / 'demo.md'
    md_path.write_text(contract_to_markdown(contract), encoding='utf-8')
    loaded = load_spec(md_path)
    assert loaded['feature'] == 'demo'
    assert loaded['layers']['domain']['required_classes'][0]['name'] == 'Foo'


def test_rrd_shorthand_normalization() -> None:
    """RRD ``classes`` / ``http`` shorthand maps to linter contract keys."""
    rrd = {
        'feature': 'sched',
        'meta': {'source': 'openvair/modules/sched'},
        'layers': {
            'entrypoints': {
                'classes': {
                    'SchedulerCRUD': {'methods': ['get_jobs']},
                    'JobResponse': {},
                },
                'http': {
                    'router_prefix': '/scheduler',
                    'endpoints': [
                        {
                            'method': 'get',
                            'path': '/jobs',
                            'handler': 'get_jobs',
                        },
                    ],
                },
            },
        },
    }
    norm = normalize_contract_document(rrd)
    ep = norm['layers']['entrypoints']['required_http_endpoints'][0]
    assert ep['path'] == '/scheduler/jobs'
    assert ep['handler'] == 'get_jobs'
