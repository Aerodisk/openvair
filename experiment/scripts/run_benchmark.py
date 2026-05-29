#!/usr/bin/env python3
"""Full benchmark pipeline: mutations → linter → LLM → metrics → report → charts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import RESULTS_DIR  # noqa: E402

SCRIPTS = _BOOT / 'experiment' / 'scripts'


def _run_step(name: str, script: str, extra_args: list[str] | None = None) -> float:
    cmd = [sys.executable, str(SCRIPTS / script), *(extra_args or [])]
    print(f'\n=== {name} ===', flush=True)
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, cwd=str(_BOOT))
    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        print(f'STEP FAILED: {name} (exit {proc.returncode})', file=sys.stderr)
        raise SystemExit(proc.returncode)
    print(f'OK ({elapsed:.2f}s wall)', flush=True)
    return elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description='Run full RDE vs LLM benchmark.')
    parser.add_argument(
        '--skip-llm',
        action='store_true',
        help='Only linter + report (no API cost).',
    )
    parser.add_argument(
        '--skip-mutations',
        action='store_true',
        help='Reuse existing mutated_specs/ and ground_truth.json.',
    )
    parser.add_argument(
        '--only-report',
        action='store_true',
        help='Regenerate evaluation, markdown report and charts from existing JSON.',
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    wall: dict[str, float] = {}
    t_total = time.perf_counter()

    if args.only_report:
        wall['evaluate'] = _run_step('evaluate', 'evaluate.py')
        wall['report'] = _run_step('report', 'report_markdown.py')
        wall['visualize'] = _run_step('visualize', 'visualize.py')
    else:
        if not args.skip_mutations:
            wall['generate_mutations'] = _run_step('mutations', 'generate_mutations.py')
        wall['linter'] = _run_step('linter', 'run_linter.py')
        if not args.skip_llm:
            wall['llm'] = _run_step('llm', 'run_llm.py')
        wall['evaluate'] = _run_step('evaluate', 'evaluate.py')
        wall['report'] = _run_step('report', 'report_markdown.py')
        wall['visualize'] = _run_step('visualize', 'visualize.py')

    wall['total_wall_seconds'] = time.perf_counter() - t_total
    meta = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'skip_llm': args.skip_llm or args.only_report,
        'steps_wall_seconds': {k: round(v, 3) for k, v in wall.items()},
    }
    meta_path = RESULTS_DIR / 'benchmark_run_meta.json'
    meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')

    print('\n=== Benchmark complete ===')
    print(f'  Meta: {meta_path}')
    print(f'  Report: {RESULTS_DIR / "BENCHMARK_REPORT.md"}')
    print(f'  Figures: {RESULTS_DIR / "figures"}/')
    if args.skip_llm and not args.only_report:
        print('\nLLM skipped. For full benchmark run without --skip-llm after setting .env')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
