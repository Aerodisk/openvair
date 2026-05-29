"""Shared aggregation for benchmark reports and charts."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from experiment.config import GROUND_TRUTH_PATH, RESULTS_DIR


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def load_ground_truth() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    gt = load_json(GROUND_TRUTH_PATH)
    return gt, list(gt.get('mutations', []))


def load_evaluation() -> dict[str, Any]:
    return load_json(RESULTS_DIR / 'evaluation_report.json')


def load_linter_results() -> dict[str, Any] | None:
    path = RESULTS_DIR / 'linter_results.json'
    return load_json(path) if path.is_file() else None


def load_llm_results() -> dict[str, Any] | None:
    path = RESULTS_DIR / 'llm_results.json'
    return load_json(path) if path.is_file() else None


def _recall_for_subset(
    mutations: list[dict],
    per_mutation: list[dict],
    *,
    key: str,
    value: str,
) -> dict[str, Any]:
    ids = {m['id'] for m in mutations if m.get(key) == value}
    rows = [r for r in per_mutation if r.get('id') in ids]
    total = len(ids)
    detected = sum(1 for r in rows if r.get('detected'))
    recall = detected / total if total else 0.0
    return {
        'total': total,
        'detected': detected,
        'missed': total - detected,
        'recall': round(recall, 4),
    }


def breakdown_by_kind(
    mutations: list[dict],
    per_mutation: list[dict],
) -> dict[str, dict[str, Any]]:
    kinds = sorted({str(m.get('kind', '')) for m in mutations})
    return {
        k: _recall_for_subset(mutations, per_mutation, key='kind', value=k)
        for k in kinds
        if k
    }


def breakdown_by_module(
    mutations: list[dict],
    per_mutation: list[dict],
) -> dict[str, dict[str, Any]]:
    modules = sorted({str(m.get('module', '')) for m in mutations})
    return {
        m: _recall_for_subset(mutations, per_mutation, key='module', value=m)
        for m in modules
        if m
    }


def timing_by_module(tool_data: dict[str, Any] | None) -> dict[str, float]:
    if not tool_data:
        return {}
    out: dict[str, float] = {}
    for run in tool_data.get('runs', []):
        mod = str(run.get('module', ''))
        if mod:
            out[mod] = float(run.get('seconds', 0.0))
    return out


def llm_usage_by_module(tool_data: dict[str, Any] | None) -> dict[str, dict[str, float]]:
    if not tool_data:
        return {}
    out: dict[str, dict[str, float]] = {}
    for run in tool_data.get('runs', []):
        mod = str(run.get('module', ''))
        if not mod:
            continue
        out[mod] = {
            'tokens_in': float(run.get('tokens_in', 0)),
            'tokens_out': float(run.get('tokens_out', 0)),
            'cost_usd': float(run.get('cost_usd', 0.0)),
            'seconds': float(run.get('seconds', 0.0)),
            'issues': float(run.get('issue_count', 0)),
        }
    return out


def build_analysis_payload() -> dict[str, Any]:
    """Full structured summary for report + charts."""
    gt, mutations = load_ground_truth()
    ev = load_evaluation()
    linter_data = load_linter_results()
    llm_data = load_llm_results()

    linter_pm = ev.get('linter', {}).get('per_mutation', [])
    llm_pm = ev.get('llm', {}).get('per_mutation', []) if 'precision' in ev.get('llm', {}) else []

    payload: dict[str, Any] = {
        'ground_truth_count': len(mutations),
        'modules': gt.get('modules', []),
        'linter': {
            'metrics': {k: ev['linter'][k] for k in ('tp', 'fp', 'fn', 'precision', 'recall', 'f1') if k in ev.get('linter', {})},
            'total_seconds': ev.get('linter', {}).get('total_seconds'),
            'total_errors_reported': ev.get('linter', {}).get('total_errors_reported'),
            'by_kind': breakdown_by_kind(mutations, linter_pm),
            'by_module': breakdown_by_module(mutations, linter_pm),
            'timing_by_module': timing_by_module(linter_data),
        },
        'llm': {'status': 'not_run'},
    }

    if llm_pm:
        payload['llm'] = {
            'metrics': {k: ev['llm'][k] for k in ('tp', 'fp', 'fn', 'precision', 'recall', 'f1') if k in ev.get('llm', {})},
            'total_seconds': ev.get('llm', {}).get('total_seconds'),
            'total_cost_usd': ev.get('llm', {}).get('total_cost_usd'),
            'total_issues_reported': ev.get('llm', {}).get('total_issues_reported'),
            'model': llm_data.get('model') if llm_data else None,
            'by_kind': breakdown_by_kind(mutations, llm_pm),
            'by_module': breakdown_by_module(mutations, llm_pm),
            'timing_by_module': timing_by_module(llm_data),
            'usage_by_module': llm_usage_by_module(llm_data),
        }

    if linter_data and payload['linter'].get('total_seconds'):
        secs = float(payload['linter']['total_seconds'])
        n = len(mutations)
        payload['linter']['throughput_defs_per_sec'] = round(n / secs, 2) if secs else 0.0

    if llm_data and payload.get('llm', {}).get('total_seconds'):
        secs = float(payload['llm']['total_seconds'])
        n = len(mutations)
        payload['llm']['throughput_defs_per_sec'] = round(n / secs, 4) if secs else 0.0

    return payload
