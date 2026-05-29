#!/usr/bin/env python3
"""Run RDE linter on mutated specs; save JSON results."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import (  # noqa: E402
    MODULES,
    MUTATED_SPECS_DIR,
    OPENVAIR_MODULES_DIR,
    RESULTS_DIR,
)
from requirements_linter.cli import run_on_openvair_module  # noqa: E402


def _active_modules() -> list[str]:
    import os

    raw = os.environ.get('BENCHMARK_MODULES', '').strip()
    if raw:
        return [m.strip() for m in raw.split(',') if m.strip()]
    return list(MODULES)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    modules = _active_modules()
    runs: list[dict] = []
    all_errors: list[str] = []
    t0 = time.perf_counter()

    for module in modules:
        spec_path = MUTATED_SPECS_DIR / f'{module}.md'
        mod_path = OPENVAIR_MODULES_DIR / module
        if not spec_path.is_file():
            print(f'SKIP {module}: no {spec_path}', file=sys.stderr)
            continue
        if not mod_path.is_dir():
            print(f'SKIP {module}: no {mod_path}', file=sys.stderr)
            continue

        t_mod = time.perf_counter()
        try:
            _artifacts, result = run_on_openvair_module(
                spec_path.resolve(),
                mod_path.resolve(),
                warn_extras=False,
            )
            elapsed = time.perf_counter() - t_mod
            runs.append({
                'module': module,
                'spec': str(spec_path),
                'exit_code': 1 if result.errors else 0,
                'error_count': len(result.errors),
                'errors': result.errors,
                'warnings': result.warnings,
                'seconds': round(elapsed, 4),
            })
            all_errors.extend(result.errors)
            print(
                f'{module}: {len(result.errors)} errors in {elapsed:.3f}s',
            )
        except Exception as exc:
            runs.append({
                'module': module,
                'spec': str(spec_path),
                'exit_code': -1,
                'error_count': 0,
                'errors': [],
                'fatal': str(exc),
                'seconds': round(time.perf_counter() - t_mod, 4),
            })
            print(f'{module}: FATAL {exc}', file=sys.stderr)

    total_sec = time.perf_counter() - t0
    out = {
        'tool': 'rde_linter',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'modules': modules,
        'total_errors': len(all_errors),
        'total_seconds': round(total_sec, 4),
        'runs': runs,
        'all_errors': all_errors,
    }
    path = RESULTS_DIR / 'linter_results.json'
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {path} ({len(all_errors)} errors, {total_sec:.3f}s total)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
