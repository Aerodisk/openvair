#!/usr/bin/env python3
"""Run OpenAI API benchmark (structured JSON) on mutated specs."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import (  # noqa: E402
    DEFAULT_LLM_CACHED_INPUT_COST_PER_1M,
    DEFAULT_LLM_INPUT_COST_PER_1M,
    DEFAULT_LLM_OUTPUT_COST_PER_1M,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_REASONING_EFFORT,
    MODULES,
    MUTATED_SPECS_DIR,
    OPENVAIR_MODULES_DIR,
    RESULTS_DIR,
)

LLM_RESPONSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'issues': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'file_path': {'type': 'string'},
                    'entity_name': {'type': 'string'},
                    'error_type': {
                        'type': 'string',
                        'enum': [
                            'missing_in_code',
                            'missing_in_spec',
                            'layer_violation',
                            'type_mismatch',
                        ],
                    },
                    'description': {'type': 'string'},
                },
                'required': [
                    'file_path',
                    'entity_name',
                    'error_type',
                    'description',
                ],
                'additionalProperties': False,
            },
        },
    },
    'required': ['issues'],
    'additionalProperties': False,
}

# Outcome-first prompt (recommended for GPT-5.x); schema is in Structured Outputs.
SYSTEM_PROMPT = """\
Роль: статический анализатор архитектуры Open vAIR (RDE).

Цель: найти несоответствия, где в блоке rde (YAML) заявлены сущности или HTTP-маршруты,
которых нет в приложенном Python-коде модуля (слои DDD: domain, service_layer, adapters, entrypoints).

Критерий успеха: каждая запись в issues[] — реальное расхождение spec→code.
Не сообщай о коде, отсутствующем в spec. Не выдумывай проблемы.
Публичные методы — без ведущего '_'. FastAPI: method, path, handler, parameters как в spec.

Для каждой находки: error_type=missing_in_code, краткое description, entity_name, file_path.
"""


def _load_dotenv() -> None:
    env_path = _BOOT / 'experiment' / '.env'
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except ImportError:
        if env_path.is_file():
            for line in env_path.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


def _read_module_sources(module: str, max_chars: int = 400_000) -> str:
    root = OPENVAIR_MODULES_DIR / module
    parts: list[str] = []
    total = 0
    for path in sorted(root.rglob('*.py')):
        if 'tests' in path.parts or '__pycache__' in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding='utf-8', errors='replace')
        chunk = f'\n# FILE: {rel}\n{text}'
        if total + len(chunk) > max_chars:
            parts.append('\n# ... truncated ...\n')
            break
        parts.append(chunk)
        total += len(chunk)
    return ''.join(parts)


def _active_modules() -> list[str]:
    raw = os.environ.get('BENCHMARK_MODULES', '').strip()
    if raw:
        return [m.strip() for m in raw.split(',') if m.strip()]
    return list(MODULES)


def _use_responses_api(model: str) -> bool:
    flag = os.environ.get('OPENAI_USE_RESPONSES', '').strip().lower()
    if flag in ('0', 'false', 'no'):
        return False
    if flag in ('1', 'true', 'yes'):
        return True
    return model.startswith('gpt-5') or model.startswith('o')


def _estimate_cost(
    tokens_in: int,
    tokens_out: int,
    *,
    tokens_cached_in: int = 0,
) -> float:
    cost_in = float(
        os.environ.get(
            'LLM_INPUT_COST_PER_1M',
            str(DEFAULT_LLM_INPUT_COST_PER_1M),
        ),
    )
    cost_cached = float(
        os.environ.get(
            'LLM_CACHED_INPUT_COST_PER_1M',
            str(DEFAULT_LLM_CACHED_INPUT_COST_PER_1M),
        ),
    )
    cost_out = float(
        os.environ.get(
            'LLM_OUTPUT_COST_PER_1M',
            str(DEFAULT_LLM_OUTPUT_COST_PER_1M),
        ),
    )
    cached = min(max(tokens_cached_in, 0), tokens_in)
    billable_in = tokens_in - cached
    return (
        billable_in / 1_000_000 * cost_in
        + cached / 1_000_000 * cost_cached
        + tokens_out / 1_000_000 * cost_out
    )


def _cached_input_tokens(usage: Any) -> int:
    details = getattr(usage, 'input_tokens_details', None)
    if details is not None:
        return int(getattr(details, 'cached_tokens', 0) or 0)
    return int(getattr(usage, 'cached_tokens', 0) or 0)


def _call_openai(
    client: Any,
    *,
    model: str,
    system: str,
    user: str,
) -> tuple[str, int, int, int, str]:
    """Return (raw_json, tokens_in, tokens_out, tokens_cached_in, api_mode)."""
    if _use_responses_api(model):
        effort = os.environ.get(
            'OPENAI_REASONING_EFFORT',
            DEFAULT_REASONING_EFFORT,
        ).strip()
        kwargs: dict[str, Any] = {
            'model': model,
            'input': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            'text': {
                'format': {
                    'type': 'json_schema',
                    'name': 'rde_report',
                    'strict': True,
                    'schema': LLM_RESPONSE_SCHEMA,
                },
            },
        }
        if effort and (model.startswith('gpt-5') or model.startswith('o')):
            kwargs['reasoning'] = {'effort': effort}

        response = client.responses.create(**kwargs)
        raw = response.output_text or '{}'
        usage = response.usage
        tokens_in = int(getattr(usage, 'input_tokens', 0) or 0)
        tokens_out = int(getattr(usage, 'output_tokens', 0) or 0)
        tokens_cached = _cached_input_tokens(usage) if usage else 0
        return raw, tokens_in, tokens_out, tokens_cached, 'responses'

    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
        response_format={
            'type': 'json_schema',
            'json_schema': {
                'name': 'rde_report',
                'strict': True,
                'schema': LLM_RESPONSE_SCHEMA,
            },
        },
    )
    usage = response.usage
    tokens_in = int(usage.prompt_tokens if usage else 0)
    tokens_out = int(usage.completion_tokens if usage else 0)
    tokens_cached = _cached_input_tokens(usage) if usage else 0
    raw = response.choices[0].message.content or '{}'
    return raw, tokens_in, tokens_out, tokens_cached, 'chat_completions'


def main() -> int:
    _load_dotenv()
    api_key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not api_key:
        print(
            'ERROR: set OPENAI_API_KEY in experiment/.env (see .env.example)',
            file=sys.stderr,
        )
        return 1

    try:
        from openai import OpenAI
    except ImportError:
        print('ERROR: pip install -r experiment/requirements.txt', file=sys.stderr)
        return 1

    model = os.environ.get('OPENAI_MODEL', DEFAULT_OPENAI_MODEL)
    api_mode = 'responses' if _use_responses_api(model) else 'chat_completions'
    reasoning = os.environ.get(
        'OPENAI_REASONING_EFFORT',
        DEFAULT_REASONING_EFFORT,
    )
    client = OpenAI(api_key=api_key)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f'Model: {model}  API: {api_mode}  reasoning.effort: {reasoning}')

    modules = _active_modules()
    runs: list[dict] = []
    all_issues: list[dict] = []
    total_cost_usd = 0.0
    t0 = time.perf_counter()

    for module in modules:
        spec_path = MUTATED_SPECS_DIR / f'{module}.md'
        if not spec_path.is_file():
            print(f'SKIP {module}: no spec', file=sys.stderr)
            continue

        spec_text = spec_path.read_text(encoding='utf-8')
        code_text = _read_module_sources(module)
        user_prompt = (
            f'MODULE: {module}\n\nSPECIFICATION:\n{spec_text}\n\nCODE:\n{code_text}'
        )

        print(f'LLM {module}...', flush=True)
        t_mod = time.perf_counter()
        try:
            raw, tokens_in, tokens_out, tokens_cached, mode = _call_openai(
                client,
                model=model,
                system=SYSTEM_PROMPT,
                user=user_prompt,
            )
            elapsed = time.perf_counter() - t_mod
            cost_usd = _estimate_cost(
                tokens_in,
                tokens_out,
                tokens_cached_in=tokens_cached,
            )
            total_cost_usd += cost_usd

            parsed = json.loads(raw)
            issues = parsed.get('issues', [])
            if not isinstance(issues, list):
                issues = []

            runs.append({
                'module': module,
                'api_mode': mode,
                'seconds': round(elapsed, 4),
                'tokens_in': tokens_in,
                'tokens_cached_in': tokens_cached,
                'tokens_out': tokens_out,
                'cost_usd': round(cost_usd, 6),
                'issue_count': len(issues),
                'issues': issues,
            })
            for issue in issues:
                if isinstance(issue, dict):
                    issue = {**issue, 'module': module}
                    all_issues.append(issue)
            print(
                f'  {len(issues)} issues, {tokens_in}+{tokens_out} tok, '
                f'${cost_usd:.4f}, {elapsed:.1f}s',
            )
        except Exception as exc:
            runs.append({
                'module': module,
                'seconds': round(time.perf_counter() - t_mod, 4),
                'fatal': str(exc),
                'issues': [],
            })
            print(f'  FATAL: {exc}', file=sys.stderr)

    total_sec = time.perf_counter() - t0
    fatal_count = sum(1 for run in runs if run.get('fatal'))
    success_count = len(runs) - fatal_count
    out = {
        'tool': 'openai_llm',
        'model': model,
        'api_mode': api_mode,
        'reasoning_effort': reasoning,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'modules': modules,
        'total_issues': len(all_issues),
        'total_seconds': round(total_sec, 4),
        'total_cost_usd': round(total_cost_usd, 6),
        'successful_runs': success_count,
        'fatal_runs': fatal_count,
        'runs': runs,
        'all_issues': all_issues,
    }
    path = RESULTS_DIR / 'llm_results.json'
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {path} (${total_cost_usd:.4f} total)')
    if runs and success_count == 0:
        print(
            'ERROR: all LLM requests failed; benchmark results are not valid.',
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
