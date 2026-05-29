#!/usr/bin/env python3
"""Quick OpenAI API reachability check (no benchmark, minimal cost)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import DEFAULT_OPENAI_MODEL  # noqa: E402


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


def main() -> int:
    _load_dotenv()
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key:
        print('FAIL: OPENAI_API_KEY not set in experiment/.env', file=sys.stderr)
        return 1

    model = os.environ.get('OPENAI_MODEL', DEFAULT_OPENAI_MODEL)
    print(f'Key: ...{key[-4:]}  model: {model}')

    try:
        from openai import OpenAI
    except ImportError:
        print('FAIL: pip install openai', file=sys.stderr)
        return 1

    client = OpenAI(api_key=key)

    # 1) Cheap: list models (no generation)
    print('\n[1] GET /v1/models ...')
    try:
        page = client.models.list()
        first = next(iter(page.data), None)
        print(f'OK — API reachable. Example model id: {first.id if first else "?"}')
    except Exception as exc:
        print(f'FAIL — {exc}', file=sys.stderr)
        if 'unsupported_country_region_territory' in str(exc):
            print(
                '\nRegion/network blocked for OpenAI API. Use VPN or run from '
                'another network. Full benchmark will fail the same way.',
                file=sys.stderr,
            )
        return 1

    # 2) Optional: tiny generation (may cost a fraction of a cent)
    if os.environ.get('PING_OPENAI_GENERATE', '').strip() in ('1', 'true', 'yes'):
        print(f'\n[2] Tiny completion ({model}) ...')
        try:
            if model.startswith('gpt-5') or model.startswith('o'):
                r = client.responses.create(
                    model=model,
                    input='Reply with exactly: pong',
                    reasoning={'effort': 'none'},
                    max_output_tokens=16,
                )
                text = (r.output_text or '').strip()
            else:
                r = client.chat.completions.create(
                    model=model,
                    messages=[{'role': 'user', 'content': 'Reply with exactly: pong'}],
                    max_tokens=16,
                )
                text = (r.choices[0].message.content or '').strip()
            print(f'OK — model answered: {text!r}')
        except Exception as exc:
            print(f'FAIL — {exc}', file=sys.stderr)
            return 1
    else:
        print(
            '\n[2] Skipped (set PING_OPENAI_GENERATE=1 in .env to test model slug)',
        )

    print('\nAll checks passed. You can run: python experiment/scripts/run_llm.py')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
