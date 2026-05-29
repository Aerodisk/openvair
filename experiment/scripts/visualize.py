#!/usr/bin/env python3
"""Generate PNG charts for the linter vs LLM benchmark."""

from __future__ import annotations

import sys
from pathlib import Path

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import RESULTS_DIR  # noqa: E402
from experiment.scripts.benchmark_analysis import (  # noqa: E402
    build_analysis_payload,
    load_evaluation,
    load_ground_truth,
)

FIGURES_DIR = RESULTS_DIR / 'figures'


def _require_matplotlib():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt  # noqa: F401
        return plt
    except ImportError as exc:
        print('ERROR: pip install matplotlib', file=sys.stderr)
        raise SystemExit(1) from exc


def _save(fig, name: str) -> None:
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=150, bbox_inches='tight')
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(f'  {path.name}')


def chart_metrics_comparison(plt, analysis: dict) -> None:
    tools = ['RDE-линтер']
    metrics = ['precision', 'recall', 'f1']
    lin = analysis['linter']['metrics']
    data = [[lin[m] for m in metrics]]
    llm_ran = 'metrics' in analysis.get('llm', {})
    if llm_ran:
        tools.append('LLM')
        data.append([analysis['llm']['metrics'][m] for m in metrics])

    x = range(len(metrics))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (tool, vals) in enumerate(zip(tools, data)):
        offset = (i - (len(tools) - 1) / 2) * width
        bars = ax.bar([xi + offset for xi in x], vals, width, label=tool)
        for bar, v in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f'{v:.0%}',
                ha='center',
                va='bottom',
                fontsize=9,
            )
    ax.set_xticks(list(x))
    ax.set_xticklabels(['Precision', 'Recall', 'F1'])
    ax.set_ylim(0, 1.15)
    ax.set_ylabel('Доля')
    ax.set_title('Сравнение метрик: линтер vs LLM')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    _save(fig, '01_metrics_comparison.png')


def chart_tp_fn_fp(plt, analysis: dict) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    tools = ['Линтер']
    series = [analysis['linter']['metrics']]
    if 'metrics' in analysis.get('llm', {}):
        tools.append('LLM')
        series.append(analysis['llm']['metrics'])

    labels = ['TP', 'FN', 'FP']
    x = range(len(tools))
    width = 0.25
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    for j, lab in enumerate(labels):
        key = lab.lower()
        vals = [s[key] for s in series]
        ax.bar([xi + (j - 1) * width for xi in x], vals, width, label=lab, color=colors[j])
    ax.set_xticks(list(x))
    ax.set_xticklabels(tools)
    ax.set_ylabel('Количество')
    ax.set_title('TP / FN / FP')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    _save(fig, '02_tp_fn_fp.png')


def chart_recall_by_kind(plt, analysis: dict) -> None:
    kinds = sorted(analysis['linter']['by_kind'].keys())
    lin_r = [analysis['linter']['by_kind'][k]['recall'] for k in kinds]
    llm_r = []
    if 'by_kind' in analysis.get('llm', {}):
        llm_r = [analysis['llm']['by_kind'].get(k, {}).get('recall', 0) for k in kinds]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(kinds))
    w = 0.35
    ax.bar([i - w / 2 for i in x], lin_r, w, label='Линтер', color='#3498db')
    if llm_r:
        ax.bar([i + w / 2 for i in x], llm_r, w, label='LLM', color='#9b59b6')
    ax.set_xticks(list(x))
    ax.set_xticklabels(kinds, rotation=15, ha='right')
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('Recall')
    ax.set_title('Recall по типу дефекта')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    _save(fig, '03_recall_by_kind.png')


def chart_recall_by_module(plt, analysis: dict) -> None:
    mods = sorted(analysis['linter']['by_module'].keys())
    lin_r = [analysis['linter']['by_module'][m]['recall'] for m in mods]
    llm_r = []
    if 'by_module' in analysis.get('llm', {}):
        llm_r = [analysis['llm']['by_module'].get(m, {}).get('recall', 0) for m in mods]

    fig, ax = plt.subplots(figsize=(11, 5))
    x = range(len(mods))
    w = 0.35
    ax.bar([i - w / 2 for i in x], lin_r, w, label='Линтер', color='#1abc9c')
    if llm_r:
        ax.bar([i + w / 2 for i in x], llm_r, w, label='LLM', color='#e67e22')
    ax.set_xticks(list(x))
    ax.set_xticklabels(mods, rotation=35, ha='right')
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('Recall')
    ax.set_title('Recall по модулю')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    _save(fig, '04_recall_by_module.png')


def chart_time_per_module(plt, analysis: dict) -> None:
    mods = sorted(analysis['linter']['timing_by_module'].keys())
    lin_t = [analysis['linter']['timing_by_module'].get(m, 0) for m in mods]
    llm_t = []
    if analysis.get('llm', {}).get('timing_by_module'):
        llm_t = [analysis['llm']['timing_by_module'].get(m, 0) for m in mods]

    fig, ax = plt.subplots(figsize=(11, 5))
    x = range(len(mods))
    w = 0.35
    ax.bar([i - w / 2 for i in x], lin_t, w, label='Линтер (с)', color='#16a085')
    if llm_t:
        ax2 = ax.twinx()
        ax2.bar([i + w / 2 for i in x], llm_t, w, label='LLM (с)', color='#c0392b', alpha=0.85)
        ax2.set_ylabel('LLM, секунды', color='#c0392b')
        ax2.tick_params(axis='y', labelcolor='#c0392b')
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    else:
        ax.legend()
    ax.set_xticks(list(x))
    ax.set_xticklabels(mods, rotation=35, ha='right')
    ax.set_ylabel('Линтер, секунды')
    ax.set_title('Время обработки одного модуля')
    ax.grid(axis='y', alpha=0.3)
    _save(fig, '05_time_per_module.png')


def chart_throughput(plt, analysis: dict) -> None:
    labels = ['RDE-линтер']
    vals = [analysis['linter'].get('throughput_defs_per_sec', 0)]
    if analysis.get('llm', {}).get('throughput_defs_per_sec') is not None:
        labels.append('LLM')
        vals.append(analysis['llm']['throughput_defs_per_sec'])

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, vals, color=['#2980b9', '#8e44ad'][: len(labels)])
    for bar, v in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f'{v:.2f}/с',
            ha='center',
            va='bottom',
        )
    ax.set_ylabel('Дефектов в секунду')
    ax.set_title('Пропускная способность (43 дефекта / общее время)')
    ax.grid(axis='y', alpha=0.3)
    _save(fig, '06_throughput.png')


def chart_llm_tokens_cost(plt, analysis: dict) -> None:
    usage = analysis.get('llm', {}).get('usage_by_module', {})
    if not usage:
        return
    mods = sorted(usage.keys())
    tin = [usage[m]['tokens_in'] for m in mods]
    tout = [usage[m]['tokens_out'] for m in mods]
    cost = [usage[m]['cost_usd'] for m in mods]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8))
    x = range(len(mods))
    w = 0.35
    ax1.bar([i - w / 2 for i in x], tin, w, label='Input tokens', color='#5dade2')
    ax1.bar([i + w / 2 for i in x], tout, w, label='Output tokens', color='#af7ac5')
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(mods, rotation=35, ha='right')
    ax1.set_ylabel('Токены')
    ax1.set_title('Токены LLM по модулю')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    ax2.bar(mods, cost, color='#e74c3c')
    ax2.set_ylabel('USD')
    ax2.set_title('Стоимость LLM по модулю')
    ax2.tick_params(axis='x', rotation=35)
    ax2.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    _save(fig, '07_llm_tokens_cost.png')


def chart_defect_distribution(plt, gt_mutations: list) -> None:
    from collections import Counter
    counts = Counter(m.get('kind', '?') for m in gt_mutations)
    labels = list(counts.keys())
    sizes = list(counts.values())
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sizes,
        labels=[f'{l}\n({s})' for l, s in zip(labels, sizes)],
        autopct='%1.0f%%',
        startangle=90,
    )
    ax.set_title('Распределение 43 дефектов по типам')
    _save(fig, '08_defect_distribution.png')


def chart_detection_heatmap(plt, ev: dict, mutations: list) -> None:
    if 'precision' not in ev.get('llm', {}):
        return
    import numpy as np

    kinds = sorted({m['kind'] for m in mutations})
    modules = sorted({m['module'] for m in mutations})
    def _matrix(tool: str) -> list[list[float]]:
        pm = {r['id']: r['detected'] for r in ev[tool]['per_mutation']}
        grid = []
        for mod in modules:
            row = []
            for kind in kinds:
                ids = [m['id'] for m in mutations if m['module'] == mod and m['kind'] == kind]
                if not ids:
                    row.append(float('nan'))
                else:
                    row.append(sum(1 for i in ids if pm.get(i)) / len(ids))
            grid.append(row)
        return grid

    lin_m = np.array(_matrix('linter'))
    llm_m = np.array(_matrix('llm'))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, mat, title in zip(axes, [lin_m, llm_m], ['Линтер', 'LLM']):
        im = ax.imshow(mat, vmin=0, vmax=1, cmap='RdYlGn', aspect='auto')
        ax.set_xticks(range(len(kinds)))
        ax.set_xticklabels(kinds, rotation=20, ha='right')
        ax.set_yticks(range(len(modules)))
        ax.set_yticklabels(modules)
        ax.set_title(f'Доля найденных ({title})')
        for i in range(len(modules)):
            for j in range(len(kinds)):
                v = mat[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f'{v:.0%}', ha='center', va='center', fontsize=8)
    fig.colorbar(im, ax=axes.ravel().tolist(), label='Recall', shrink=0.8)
    fig.suptitle('Матрица обнаружения: модуль × тип дефекта')
    fig.tight_layout()
    _save(fig, '09_detection_heatmap.png')


def main() -> int:
    if not (RESULTS_DIR / 'evaluation_report.json').is_file():
        print('Run evaluate.py first.', file=sys.stderr)
        return 1

    plt = _require_matplotlib()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    _, mutations = load_ground_truth()
    ev = load_evaluation()
    analysis = build_analysis_payload()

    print('Writing charts:')
    chart_metrics_comparison(plt, analysis)
    chart_tp_fn_fp(plt, analysis)
    chart_recall_by_kind(plt, analysis)
    chart_recall_by_module(plt, analysis)
    chart_time_per_module(plt, analysis)
    chart_throughput(plt, analysis)
    chart_llm_tokens_cost(plt, analysis)
    chart_defect_distribution(plt, mutations)
    chart_detection_heatmap(plt, ev, mutations)
    print(f'Done -> {FIGURES_DIR}/')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
