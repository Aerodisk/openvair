#!/usr/bin/env python3
"""Generate BENCHMARK_REPORT.md with tables and chart references."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import GROUND_TRUTH_PATH, RESULTS_DIR  # noqa: E402
from experiment.scripts.benchmark_analysis import (  # noqa: E402
    build_analysis_payload,
    load_evaluation,
    load_ground_truth,
    load_llm_results,
    load_linter_results,
)

FIGURES_DIR = RESULTS_DIR / 'figures'
REPORT_PATH = RESULTS_DIR / 'BENCHMARK_REPORT.md'

# Подписи типов мутаций из ground_truth.json (внутренние коды → текст для отчёта)
_KIND_LABELS: dict[str, str] = {
    'phantom_class': 'фантомный класс в спецификации',
    'wrong_method': 'неверное имя метода в спецификации',
    'wrong_http_path': 'неверный путь HTTP в спецификации',
    'wrong_callable': 'неверное имя функции в спецификации',
}

# Категории ложных срабатываний (внутренний код → русская подпись)
_FP_CATEGORY_LABELS: dict[str, str] = {
    'class_shape_mismatch': 'класс объявлен не так, как в коде',
    'http_param_kind_mismatch': 'тип параметра HTTP не совпадает',
    'http_param_contract_detail': 'лишний или неверный параметр API',
    'other_spec_code_gap': 'прочее расхождение контракта и кода',
    'unexpected_phantom': 'неожиданное совпадение с фантомом',
}


def _pct(x: float) -> str:
    return f'{100.0 * x:.1f}%'


def _kind_list_ru(kinds: set[str]) -> str:
    if not kinds:
        return '—'
    return ', '.join(_KIND_LABELS.get(k, k) for k in sorted(kinds))


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        '| ' + ' | '.join(headers) + ' |',
        '| ' + ' | '.join(['---'] * len(headers)) + ' |',
    ]
    for row in rows:
        lines.append('| ' + ' | '.join(row) + ' |')
    return '\n'.join(lines)


def _gt_kinds_by_module(mutations: list[dict]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for m in mutations:
        mod = str(m.get('module', ''))
        out.setdefault(mod, set()).add(str(m.get('kind', '')))
    return out


def _classify_false_positive(issue: dict, gt_kinds: dict[str, set[str]]) -> tuple[str, str]:
    """Вернуть (код категории, пояснение на русском)."""
    mod = str(issue.get('module', ''))
    entity = str(issue.get('entity_name', ''))
    desc = str(issue.get('description', ''))
    kinds_ru = _kind_list_ru(gt_kinds.get(mod, set()))

    if entity.startswith('PhantomRde_'):
        return (
            'unexpected_phantom',
            'Похоже на фантомный класс из эксперимента, но не совпало ни с одной '
            'из 43 эталонных записей (такое маловероятно).',
        )

    if 'query parameter' in desc.lower() and 'path parameter' in desc.lower():
        return (
            'http_param_kind_mismatch',
            f'В изменённой спецификации модуля «{mod}» мы намеренно вносили только: '
            f'{kinds_ru}. '
            'Замечание про то, что в контракте параметр указан как query, а в коде '
            'он берётся из пути URL (path), **экспериментом не добавлялось** — '
            'так было уже в исходной спецификации. '
            'Линтер в этом прогоне проверял только внесённые нами 43 дефекта; '
            'языковая модель просмотрела весь контракт целиком.',
        )

    if 'nested class' in desc.lower() or 'top-level' in desc.lower():
        return (
            'class_shape_mismatch',
            f'В контракте класс указан на одном уровне, в коде — вложенным в другой '
            f'класс. Среди 43 эталонных дефектов для «{mod}» такой записи не было '
            f'(были только: {kinds_ru}).',
        )

    if 'dependency parameter' in desc.lower() or 'route-level dependency' in desc.lower():
        return (
            'http_param_contract_detail',
            'Расхождение в описании параметров HTTP-обработчика (зависимости FastAPI, '
            'тело запроса, параметры маршрута). В список из 43 внесённых дефектов '
            f'для «{mod}» это не входило (там только: {kinds_ru}).',
        )

    return (
        'other_spec_code_gap',
        'Есть расхождение между контрактом и кодом, но оно не совпало ни с одной '
        'из 43 эталонных записей в файле ground_truth.json.',
    )


def _false_positive_section(
    fp_issues: list[dict],
    mutations: list[dict],
    llm_metrics: dict,
) -> list[str]:
    if not fp_issues:
        return [
            '## 7. Ложные срабатывания языковой модели',
            '',
            'Ложных срабатываний нет: каждое замечание модели совпало с одним из '
            '43 внесённых дефектов.',
            '',
        ]

    gt_kinds = _gt_kinds_by_module(mutations)
    tp = int(llm_metrics.get('tp', 0))
    fp = int(llm_metrics.get('fp', 0))
    lines = [
        '## 7. Ложные срабатывания языковой модели',
        '',
        '**Как считаем в этом эксперименте.** Замечание модели — **ложное срабатывание**, '
        'если оно **не совпало** ни с одной из 43 записей в эталоне (`ground_truth.json`), '
        'даже если по смыслу контракт и код действительно расходятся.',
        '',
        f'Всего замечаний модели: **{tp + fp}**. '
        f'**Верно по эталону:** {tp}. **Лишние:** {fp}. '
        f'**Точность** (доля верных среди всех замечаний): {tp} / ({tp} + {fp}) '
        f'= {_pct(float(llm_metrics["precision"]))}.',
        '',
        '### Почему линтер таких ложных срабатываний не дал',
        '',
        'RDE-линтер сравнивает изменённую спецификацию с кодом по жёстким правилам '
        '(разбор дерева синтаксиса) и в метриках учитывает только **те 43 дефекта, '
        'которые мы сами внесли**. Он не «штрафует» старые расхождения, уже жившие '
        'в спецификации до эксперимента — например, когда в контракте параметр '
        'описан как query, а в FastAPI он в path.',
        '',
        'Языковая модель получила **весь** архитектурный контракт (блок `rde`) и '
        '**весь** исходный код модуля и сообщила о **любом** заметном несоответствии. '
        'Часть таких замечаний может быть полезной на практике, но для **этого** '
        'сравнения с эталоном они считаются лишними.',
        '',
        '### Сводная таблица ложных срабатываний',
        '',
    ]

    summary_rows: list[list[str]] = []
    detail_blocks: list[str] = []

    for n, issue in enumerate(fp_issues, 1):
        cat_code, why = _classify_false_positive(issue, gt_kinds)
        cat_ru = _FP_CATEGORY_LABELS.get(cat_code, cat_code)
        mod = str(issue.get('module', ''))
        entity = str(issue.get('entity_name', ''))
        desc = str(issue.get('description', ''))
        summary_rows.append([str(n), mod, entity, cat_ru, why])
        detail_blocks += [
            f'#### Ложное срабатывание {n}: модуль «{mod}» — {entity}',
            '',
            f'- **Категория:** {cat_ru}',
            f'- **Тип в ответе модели:** «отсутствует в коде» (`missing_in_code`)',
            f'- **Почему считаем ложным:** {why}',
            f'- **Текст модели (как вернула API):** {desc}',
            '',
        ]

    lines.append(
        _md_table(
            ['№', 'Модуль', 'Сущность', 'Категория', 'Почему ложное'],
            summary_rows,
        ),
    )
    lines += ['', '### Подробный разбор каждого ложного срабатывания', ''] + detail_blocks

    by_mod: dict[str, int] = {}
    for issue in fp_issues:
        m = str(issue.get('module', ''))
        by_mod[m] = by_mod.get(m, 0) + 1
    lines += [
        '### Сколько ложных срабатываний по модулям',
        '',
        _md_table(
            ['Модуль', 'Ложных', 'Эталонных дефектов', 'Что вносили в эталон'],
            [
                [
                    mod,
                    str(cnt),
                    str(sum(1 for m in mutations if m.get('module') == mod)),
                    _kind_list_ru(gt_kinds.get(mod, set())),
                ]
                for mod, cnt in sorted(by_mod.items())
            ],
        ),
        '',
    ]

    return lines


def _metrics_row(label: str, tool: dict) -> list[str]:
    m = tool.get('metrics', tool)
    if 'precision' not in m:
        return [label, '—', '—', '—', '—', '—', '—', '—']
    return [
        label,
        str(m.get('tp', '')),
        str(m.get('fn', '')),
        str(m.get('fp', '')),
        _pct(float(m['precision'])),
        _pct(float(m['recall'])),
        f'{float(m["f1"]):.3f}',
        str(tool.get('total_seconds', '—')),
    ]


def main() -> int:
    if not (RESULTS_DIR / 'evaluation_report.json').is_file():
        print('Run evaluate.py first.', file=sys.stderr)
        return 1

    gt, mutations = load_ground_truth()
    ev = load_evaluation()
    analysis = build_analysis_payload()
    llm_data = load_llm_results()

    (FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    fig_rel = 'figures'

    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    llm_ran = 'precision' in ev.get('llm', {})
    model_name = analysis['llm'].get('model', '—') if llm_ran else '—'

    lines: list[str] = [
        '# Бенчмарк: RDE-линтер и языковая модель (Open vAIR)',
        '',
        f'**Дата отчёта:** {now}  ',
        f'**Эталонных дефектов (внесено намеренно):** {len(mutations)}  ',
        f'**Модулей Open vAIR:** {len(gt.get("modules", []))}  ',
        '',
        '## Протокол',
        '',
        '```mermaid',
        'flowchart LR',
        '  GT[эталон 43 дефекта] --> L[RDE-линтер]',
        '  GT --> M[языковая модель GPT]',
        '  SP[изменённые спецификации] --> L',
        '  SP --> M',
        '  CODE[исходный код модулей] --> L',
        '  CODE --> M',
        '  L --> EV[подсчёт метрик]',
        '  M --> EV',
        '  EV --> R[отчёт и графики]',
        '```',
        '',
        '## 1. Сводные метрики',
        '',
        'Пояснение к столбцам: **верно найдено** — дефект из эталона обнаружен; '
        '**пропущено** — дефект из эталона не найден; **ложные** — лишние замечания; '
        '**точность** — доля верных среди всех срабатываний; **полнота** — доля '
        'найденных среди всех дефектов эталона.',
        '',
        _md_table(
            [
                'Инструмент',
                'Верно',
                'Пропущ.',
                'Ложные',
                'Точность',
                'Полнота',
                'F1',
                'Время, с',
            ],
            [
                _metrics_row('RDE-линтер', analysis['linter']),
                _metrics_row(
                    f'Языковая модель ({model_name})' if llm_ran else 'Языковая модель',
                    analysis['llm'] if llm_ran else {},
                ),
            ],
        ),
        '',
    ]

    if llm_ran:
        lines += [
            f'**Стоимость запросов к API:** ${analysis["llm"].get("total_cost_usd", 0):.4f}  ',
            '*(оценка по тарифу gpt-5.5 Standard: вход $5/1M, кэшированный вход $0.5/1M, выход $30/1M)*  ',
            f'**Всего замечаний модели:** {analysis["llm"].get("total_issues_reported", 0)}  ',
            '',
        ]
    else:
        lines += ['*Прогон языковой модели не выполнялся — соответствующие разделы пустые.*', '']

    lin_tp = float(analysis['linter']['metrics'].get('tp', 0))
    lin_sec = float(analysis['linter'].get('total_seconds') or 1)
    lines += [
        f'**Скорость линтера:** около {analysis["linter"].get("throughput_defs_per_sec", lin_tp / lin_sec):.0f} эталонных дефектов в секунду.  ',
        '',
        f'![Сравнение точности и полноты]({fig_rel}/01_metrics_comparison.png)',
        '',
        f'![Верно / пропущено / ложные]({fig_rel}/02_tp_fn_fp.png)',
        '',
        '## 2. Полнота по типу внесённого дефекта',
        '',
    ]

    kinds = sorted(analysis['linter']['by_kind'].keys())
    kind_rows = []
    for k in kinds:
        lk = analysis['linter']['by_kind'][k]
        kind_ru = _KIND_LABELS.get(k, k)
        if llm_ran:
            rk = analysis['llm']['by_kind'].get(k, {})
            kind_rows.append([
                kind_ru,
                str(lk['total']),
                f'{lk["detected"]}/{lk["total"]}',
                _pct(lk['recall']),
                f'{rk.get("detected", "—")}/{rk.get("total", "—")}',
                _pct(rk['recall']) if rk.get('total') else '—',
            ])
        else:
            kind_rows.append([
                kind_ru,
                str(lk['total']),
                f'{lk["detected"]}/{lk["total"]}',
                _pct(lk['recall']),
                '—',
                '—',
            ])

    lines.append(
        _md_table(
            ['Тип дефекта', 'Штук', 'Линтер', 'Полнота L', 'Модель', 'Полнота M'],
            kind_rows,
        ),
    )
    lines += [
        '',
        f'![Полнота по типу]({fig_rel}/03_recall_by_kind.png)',
        '',
        '## 3. Полнота по модулю',
        '',
    ]

    mod_rows = []
    for mod in sorted(analysis['linter']['by_module'].keys()):
        lm = analysis['linter']['by_module'][mod]
        if llm_ran:
            rm = analysis['llm']['by_module'].get(mod, {})
            mod_rows.append([
                mod,
                str(lm['total']),
                _pct(lm['recall']),
                _pct(rm['recall']) if rm.get('total') else '—',
            ])
        else:
            mod_rows.append([mod, str(lm['total']), _pct(lm['recall']), '—'])

    lines.append(
        _md_table(['Модуль', 'Дефектов в эталоне', 'Полнота линтера', 'Полнота модели'], mod_rows),
    )
    lines += [
        '',
        f'![Полнота по модулю]({fig_rel}/04_recall_by_module.png)',
        '',
        '## 4. Скорость обработки',
        '',
        _md_table(
            ['Модуль', 'Линтер, с', 'Модель, с' if llm_ran else 'Модель'],
            [
                [
                    mod,
                    f'{analysis["linter"]["timing_by_module"].get(mod, 0):.3f}',
                    f'{analysis["llm"]["timing_by_module"].get(mod, 0):.1f}' if llm_ran else '—',
                ]
                for mod in sorted(analysis['linter']['timing_by_module'].keys())
            ],
        ),
        '',
        f'![Время по модулю]({fig_rel}/05_time_per_module.png)',
        '',
        f'![Пропускная способность]({fig_rel}/06_throughput.png)',
        '',
    ]

    if llm_ran:
        usage = analysis['llm'].get('usage_by_module', {})
        lines += [
            '## 5. Токены и стоимость запросов к модели',
            '',
            'Тариф OpenAI для модели gpt-5.5 (Standard): 5,00 $ за 1M токенов входа, 0,50 $ за 1M кэшированного входа, 30,00 $ за 1M токенов выхода.',
            '',
            _md_table(
                ['Модуль', 'Токенов на вход', 'Токенов на выход', 'USD', 'Замечаний'],
                [
                    [
                        mod,
                        str(int(u.get('tokens_in', 0))),
                        str(int(u.get('tokens_out', 0))),
                        f'{u.get("cost_usd", 0):.4f}',
                        str(int(u.get('issues', 0))),
                    ]
                    for mod, u in sorted(usage.items())
                ],
            ),
            '',
            f'![Токены и стоимость]({fig_rel}/07_llm_tokens_cost.png)',
            '',
        ]

    lines += [
        '## 6. Распределение дефектов по типам',
        '',
        f'![Распределение по типам]({fig_rel}/08_defect_distribution.png)',
        '',
    ]

    if llm_ran:
        lines += [
            f'![Матрица обнаружения]({fig_rel}/09_detection_heatmap.png)',
            '',
        ]

    if llm_ran:
        fp_issues = ev.get('llm', {}).get('false_positives', [])
        if not fp_issues and llm_data:
            from experiment.scripts.evaluate import _evaluate_llm  # noqa: E402

            issues = llm_data.get('all_issues', [])
            _m, _d, fp_issues = _evaluate_llm(mutations, issues)
        lines += _false_positive_section(fp_issues, mutations, ev.get('llm', {}))

    lines += ['## 8. Пропущенные дефекты (не найдены)', '']
    for tool_name, key in (('Линтер', 'linter'), ('Языковая модель', 'llm')):
        if key == 'llm' and not llm_ran:
            continue
        pm = ev[key].get('per_mutation', [])
        missed = [r for r in pm if not r.get('detected')]
        lines.append(f'### {tool_name} — пропущено: {len(missed)}')
        if not missed:
            lines.append('Ни одного эталонного дефекта не пропущено.')
        else:
            rows = []
            mut_by_id = {m['id']: m for m in mutations}
            for r in missed[:20]:
                m = mut_by_id.get(r['id'], {})
                kind_ru = _KIND_LABELS.get(str(r.get('kind', '')), r.get('kind', ''))
                rows.append([
                    str(r['id']),
                    r.get('module', ''),
                    kind_ru,
                    m.get('description', '')[:60],
                ])
            lines.append(_md_table(['№', 'Модуль', 'Тип', 'Описание'], rows))
            if len(missed) > 20:
                lines.append(f'*… и ещё {len(missed) - 20}*')
        lines.append('')

    lines += [
        '## 9. Файлы результатов',
        '',
        '| Файл | Содержание |',
        '|------|------------|',
        '| `ground_truth.json` | Список 43 внесённых дефектов (эталон) |',
        '| `linter_results.json` | Полный вывод линтера |',
        '| `llm_results.json` | Полный ответ языковой модели |',
        '| `evaluation_report.json` | Метрики и разбор по каждому дефекту |',
        '| `benchmark_analysis.json` | Сводные числа для графиков |',
        '',
    ]

    REPORT_PATH.write_text('\n'.join(lines), encoding='utf-8')
    analysis_path = RESULTS_DIR / 'benchmark_analysis.json'
    analysis_path.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'Wrote {REPORT_PATH}')
    print(f'Wrote {analysis_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
