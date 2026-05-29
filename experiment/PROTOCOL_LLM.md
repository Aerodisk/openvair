# Пошаговый протокол: полный бенчмарк RDE-линтер vs LLM

Выполняйте команды из **корня репозитория** (`d:\study\openvair_rde_linter`).

---

## Шаг 0. Зависимости (один раз)

```powershell
cd d:\study\openvair_rde_linter
pip install -r experiment/requirements.txt
pip install pyyaml
```

---

## Шаг 1. Бесплатная проверка пайплайна (без LLM)

Убедиться, что линтер и отчёты работают **до** траты денег:

```powershell
python experiment/scripts/run_benchmark.py --skip-llm
```

**Ожидается:**

| Проверка | Значение |
|----------|----------|
| `experiment/ground_truth.json` → `actual_count` | **43** |
| `experiment/results/linter_results.json` → `total_errors` | **43** |
| Консоль `evaluate.py` | Linter **R=100%**, F1=100% |
| `experiment/results/BENCHMARK_REPORT.md` | создан |
| `experiment/results/figures/` | **9 PNG** (графики без блока LLM) |

Если Recall линтера &lt; 100% — **не запускайте LLM**, напишите в issue / почините `generate_mutations.py`.

---

## Шаг 2. API-ключ OpenAI

1. [platform.openai.com](https://platform.openai.com) → Billing → пополнить баланс (**рекомендуется $10–15** на полный прогон 9 модулей).
2. [API keys](https://platform.openai.com/api-keys) → Create key.
3. Создать файл окружения:

```powershell
copy experiment\.env.example experiment\.env
notepad experiment\.env
```

Минимум в `.env`:

```env
OPENAI_API_KEY=sk-ваш-ключ
OPENAI_MODEL=gpt-5.5
OPENAI_REASONING_EFFORT=low
```

Для **gpt-5.5** скрипт использует **Responses API** + Structured Outputs (рекомендация OpenAI).  
Сравнение с прошлым поколением: `OPENAI_MODEL=gpt-4o-2024-08-06` и `OPENAI_USE_RESPONSES=0`.

Тарифы для оценки `$` в отчёте (gpt-5.5 Standard, [pricing](https://openai.com/api/pricing/)):

```env
LLM_INPUT_COST_PER_1M=5.0
LLM_CACHED_INPUT_COST_PER_1M=0.5
LLM_OUTPUT_COST_PER_1M=30.0
```

---

## Шаг 3 (рекомендуется). Пробный прогон LLM на 2 модулях (~$0.3–1)

В `experiment/.env` добавьте:

```env
BENCHMARK_MODULES=user,storage
```

```powershell
python experiment/scripts/run_llm.py
python experiment/scripts/evaluate.py
python experiment/scripts/report_markdown.py
python experiment/scripts/visualize.py
```

Проверьте `results/llm_results.json` (есть `cost_usd`, `tokens_in`). Если всё ок — переходите к шагу 4.

**Удалите или закомментируйте** `BENCHMARK_MODULES` для полного бенчмарка.

---

## Шаг 4. Полный бенчмарк (9 модулей, платно)

```powershell
python experiment/scripts/run_benchmark.py
```

Одна команда выполняет:

1. `generate_mutations.py` — 43 дефекта  
2. `run_linter.py` — AST, замер времени по модулю  
3. `run_llm.py` — OpenAI, JSON, токены, USD  
4. `evaluate.py` — Precision, Recall, F1  
5. `report_markdown.py` — `BENCHMARK_REPORT.md`  
6. `visualize.py` — графики в `results/figures/`

**Ориентир:** 5–20 минут, **$3–15** (зависит от размера модулей).

Повторный прогон без пересоздания мутаций:

```powershell
python experiment/scripts/run_benchmark.py --skip-mutations
```

Только пересобрать отчёт из JSON:

```powershell
python experiment/scripts/run_benchmark.py --only-report
```

---

## Шаг 5. Что открыть после прогона

| Артефакт | Назначение |
|----------|------------|
| `experiment/results/BENCHMARK_REPORT.md` | **Главный отчёт** для ВКР: таблицы + ссылки на графики |
| `experiment/results/figures/*.png` | 9 диаграмм (метрики, recall, время, токены, heatmap) |
| `experiment/results/evaluation_report.json` | P/R/F1, TP/FN/FP |
| `experiment/results/benchmark_analysis.json` | Агрегаты для графиков |
| `experiment/results/benchmark_run_meta.json` | Wall-time каждого шага |
| `experiment/results/linter_results.json` | Сырой вывод линтера |
| `experiment/results/llm_results.json` | Сырой вывод LLM |

Для ВКР: вставьте таблицы из `BENCHMARK_REPORT.md` и рисунки из `figures/`.

---

## Шаг 6. Копия отчёта в `vkr/` (опционально)

```powershell
copy experiment\results\BENCHMARK_REPORT.md vkr\BENCHMARK_LINTER_VS_LLM.md
xcopy experiment\results\figures vkr\figures_benchmark\ /E /I
```

---

## Визуализация (что будет на графиках)

| Файл | Содержание |
|------|------------|
| `01_metrics_comparison.png` | Precision, Recall, F1 — линтер vs LLM |
| `02_tp_fn_fp.png` | TP / FN / FP |
| `03_recall_by_kind.png` | Recall по типу дефекта |
| `04_recall_by_module.png` | Recall по модулю |
| `05_time_per_module.png` | Время линтера и LLM на модуль |
| `06_throughput.png` | Дефектов в секунду |
| `07_llm_tokens_cost.png` | Токены и USD по модулю (после LLM) |
| `08_defect_distribution.png` | Pie: распределение 43 дефектов |
| `09_detection_heatmap.png` | Heatmap модуль × тип (после LLM) |

---

## Устранение проблем

| Симптом | Действие |
|---------|----------|
| `OPENAI_API_KEY` не задан | `experiment/.env` |
| `ModuleNotFoundError: matplotlib` | `pip install matplotlib` |
| Обрезан контекст | `BENCHMARK_MODULES` — меньше модулей |
| LLM R=0% | Проверьте `llm_needles` / промпт; смотрите `llm_results.json` |
| Линтер R&lt;100% | `python experiment/scripts/generate_mutations.py` заново |

---

## Экономия токенов

1. Сначала шаг 1 (`--skip-llm`) — бесплатно.  
2. Потом шаг 3 — 2 модуля.  
3. Полный прогон — только если шаг 3 успешен.  
4. Не гоняйте LLM повторно: `--only-report` пересоберёт графики из JSON.
