#!/usr/bin/env python3
"""Compute Precision / Recall / F1 vs ground_truth.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import GROUND_TRUTH_PATH, RESULTS_DIR  # noqa: E402


def _norm(text: str) -> str:
    return ' '.join(text.lower().split())


def _linter_hits(mutation: dict, error_lines: list[str]) -> bool:
    needles = mutation.get('linter_needles', [])
    if not needles:
        return False

    for raw_line in error_lines:
        blob = _norm(raw_line)
        if not all(_norm(str(n)) in blob for n in needles):
            continue
        if mutation.get('kind') == 'wrong_method':
            method_needle = next(
                (n for n in needles if str(n).startswith('expected method ')),
                None,
            )
            if method_needle:
                wrong = str(method_needle).removeprefix('expected method ').strip()
                if not re.search(
                    rf'expected method {re.escape(wrong)}(\s|$)',
                    blob,
                ):
                    continue
        return True
    return False


def _llm_hits(mutation: dict, issues: list[dict]) -> bool:
    needles = [str(n) for n in mutation.get('llm_needles', [])]
    if not needles:
        return False
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        if issue.get('module') and issue['module'] != mutation.get('module'):
            continue
        blob = _norm(
            ' '.join(
                str(issue.get(k, ''))
                for k in ('file_path', 'entity_name', 'error_type', 'description')
            ),
        )
        if all(_norm(n) in blob for n in needles):
            return True
    return False


def _metrics(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall)
        else 0.0
    )
    return {
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1': round(f1, 4),
    }


def _evaluate_tool(
    mutations: list[dict],
    hit_fn,
) -> tuple[dict, list[dict]]:
    per_mutation: list[dict] = []
    tp = fp = fn = 0

    matched_issue_ids: set[int] = set()

    for mut in mutations:
        found = hit_fn(mut)
        per_mutation.append({
            'id': mut['id'],
            'module': mut['module'],
            'kind': mut['kind'],
            'detected': found,
        })
        if found:
            tp += 1
        else:
            fn += 1

    return _metrics(tp, fp, fn), per_mutation


def _evaluate_llm(
    mutations: list[dict],
    issues: list[dict],
) -> tuple[dict, list[dict]]:
    per_mutation: list[dict] = []
    tp = fn = 0
    used_issues: set[int] = set()

    for mut in mutations:
        found_idx = None
        for i, issue in enumerate(issues):
            if i in used_issues:
                continue
            if issue.get('module') and issue['module'] != mut.get('module'):
                continue
            if _llm_hits(mut, [issue]):
                found_idx = i
                break
        found = found_idx is not None
        if found:
            tp += 1
            used_issues.add(found_idx)
        else:
            fn += 1
        per_mutation.append({
            'id': mut['id'],
            'module': mut['module'],
            'kind': mut['kind'],
            'detected': found,
        })

    fp_issues: list[dict] = []
    for i, issue in enumerate(issues):
        if i not in used_issues:
            fp_issues.append({**issue, '_issue_index': i})

    fp = len(fp_issues)
    return _metrics(tp, fp, fn), per_mutation, fp_issues


def main() -> int:
    gt_path = GROUND_TRUTH_PATH
    linter_path = RESULTS_DIR / 'linter_results.json'
    llm_path = RESULTS_DIR / 'llm_results.json'

    if not gt_path.is_file():
        print(f'Missing {gt_path}. Run generate_mutations.py first.', file=sys.stderr)
        return 1
    if not linter_path.is_file():
        print(f'Missing {linter_path}. Run run_linter.py first.', file=sys.stderr)
        return 1

    gt = json.loads(gt_path.read_text(encoding='utf-8'))
    mutations = gt.get('mutations', [])
    linter_data = json.loads(linter_path.read_text(encoding='utf-8'))
    errors_by_module: dict[str, list[str]] = {}
    for run in linter_data.get('runs', []):
        mod = run.get('module', '')
        errors_by_module[mod] = list(run.get('errors', []))

    def _linter_hit(mut: dict) -> bool:
        lines = errors_by_module.get(mut.get('module', ''), [])
        return _linter_hits(mut, lines)

    linter_metrics, linter_detail = _evaluate_tool(mutations, _linter_hit)

    report: dict = {
        'ground_truth_count': len(mutations),
        'linter': {
            **linter_metrics,
            'total_errors_reported': linter_data.get('total_errors', 0),
            'total_seconds': linter_data.get('total_seconds'),
            'per_mutation': linter_detail,
        },
    }

    if llm_path.is_file():
        llm_data = json.loads(llm_path.read_text(encoding='utf-8'))
        issues = llm_data.get('all_issues', [])
        llm_metrics, llm_detail, llm_fp = _evaluate_llm(mutations, issues)
        report['llm'] = {
            **llm_metrics,
            'total_issues_reported': len(issues),
            'total_seconds': llm_data.get('total_seconds'),
            'total_cost_usd': llm_data.get('total_cost_usd'),
            'per_mutation': llm_detail,
            'false_positives': [
                {k: v for k, v in item.items() if k != '_issue_index'}
                for item in llm_fp
            ],
        }
    else:
        report['llm'] = {'status': 'not_run'}

    out_path = RESULTS_DIR / 'evaluation_report.json'
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    print('=== Evaluation ===')
    print(f'Ground truth: {len(mutations)} mutations')
    print(
        f"Linter: P={report['linter']['precision']:.2%} "
        f"R={report['linter']['recall']:.2%} "
        f"F1={report['linter']['f1']:.2%} "
        f"({report['linter']['tp']} TP, {report['linter']['fn']} FN)"
    )
    if 'precision' in report.get('llm', {}):
        print(
            f"LLM:    P={report['llm']['precision']:.2%} "
            f"R={report['llm']['recall']:.2%} "
            f"F1={report['llm']['f1']:.2%} "
            f"(${report['llm'].get('total_cost_usd', 0):.4f})"
        )
    print(f'Wrote {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
