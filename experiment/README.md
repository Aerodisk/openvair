# Эксперимент: RDE-линтер vs LLM

Сравнение детерминированного линтера и OpenAI API на **43 искусственных дефектах** в контрактах (9 модулей Open vAIR).

## Что уже в папке

| Путь | Назначение |
|------|------------|
| `scripts/generate_mutations.py` | Создаёт `mutated_specs/*.md` и `ground_truth.json` |
| `scripts/run_linter.py` | Прогон линтера → `results/linter_results.json` |
| `scripts/run_llm.py` | Прогон OpenAI API → `results/llm_results.json` |
| `scripts/evaluate.py` | Precision / Recall / F1 → `results/evaluation_report.json` |
| `scripts/report_markdown.py` | Отчёт `results/BENCHMARK_REPORT.md` |
| `scripts/visualize.py` | 9 PNG в `results/figures/` |
| `scripts/run_benchmark.py` | **Весь пайплайн одной командой** |
| `PROTOCOL_LLM.md` | **Пошаговый протокол** (ключ, LLM, отчёт) |
| `.env.example` | Шаблон API-ключа |
| `requirements.txt` | Зависимости (openai, matplotlib, …) |

---

## Что сделать вам (один раз)

### 1. Python-зависимости

Из **корня репозитория**:

```powershell
pip install -r experiment/requirements.txt
pip install pyyaml
```

### 2. Сгенерировать мутированные спеки

```powershell
python experiment/scripts/generate_mutations.py
```

Появятся:

- `experiment/mutated_specs/<module>.md` — контракты с ошибками
- `experiment/ground_truth.json` — эталон из 43 дефектов

### 3. Оплатить OpenAI и получить API-ключ

1. Зарегистрируйтесь на [https://platform.openai.com](https://platform.openai.com)
2. Пополните баланс (Billing) — для 9 модулей обычно **~$1–15**, зависит от размера кода
3. Создайте API key: [API keys](https://platform.openai.com/api-keys)
4. Скопируйте ключ:

```powershell
copy experiment\.env.example experiment\.env
# Отредактируйте experiment\.env — вставьте OPENAI_API_KEY=sk-...
```

**Токен** — это именно **API key** (`sk-...`), не подписка ChatGPT Plus (она для браузера, не для скрипта).

Опционально в `.env`:

```env
OPENAI_MODEL=gpt-4o-2024-08-06
# Дешёвый тест только на 2 модулях:
BENCHMARK_MODULES=user,storage
```

---

## Прогон (после оплаты)

**Рекомендуется — одна команда (полный бенчмарк + графики):**

```powershell
python experiment/scripts/run_benchmark.py
```

Пошагово и с экономией токенов: см. **[PROTOCOL_LLM.md](PROTOCOL_LLM.md)**.

Бесплатно (без LLM):

```powershell
python experiment/scripts/run_benchmark.py --skip-llm
```

Результаты: `experiment/results/BENCHMARK_REPORT.md`, `experiment/results/figures/`

---

## Проверка перед оплатой LLM (обязательно)

Из **корня репозитория**:

```powershell
pip install -r experiment/requirements.txt
pip install pyyaml
python experiment/scripts/generate_mutations.py
python experiment/scripts/run_linter.py
python experiment/scripts/evaluate.py
```

Ожидается:

- `ground_truth.json` → `"actual_count": 43`
- `linter_results.json` → `"total_errors": 43` (по одной ошибке на дефект)
- `evaluate.py` → **Linter R=100%**, F1=100% (иначе не запускайте LLM — сначала чините пайплайн)

Дешёвый тест LLM на 2 модулях (~$0.2–1):

```env
BENCHMARK_MODULES=user,storage
```

в `experiment/.env`.

## Ожидаемые ориентиры

| Инструмент | Ожидание |
|------------|----------|
| Линтер | 43 ошибки, &lt; 2 с на все 9 модулей, Recall → **100%** на внедрённых дефектах |
| LLM (gpt-4o) | Recall **ниже** линтера, возможны FP; ~5–15 мин; ориентир **$3–15** на все 9 модулей |

Откройте `results/evaluation_report.json` для таблицы P/R/F1.

---

## Модули эксперимента

`template`, `storage`, `backup`, `event_store`, `image`, `network`, `user`, `virtual_machines`, `volume`

## Суть эксперимента (кратко)

1. В **мутированные** спеки (`mutated_specs/*.md`) вносятся **43 контролируемых дефекта** (фантомные классы, неверные методы, неверные HTTP-пути).
2. **Код Open vAIR не меняется** — эталон `openvair/modules/<module>/`.
3. **Линтер** сравнивает мутированный контракт с кодом (AST, детерминированно).
4. **LLM** получает тот же мутированный spec + исходники модуля и возвращает JSON `issues[]`.
5. **evaluate.py** считает Precision / Recall / F1 относительно `ground_truth.json`.

Линтер проверяет только то, что **явно заявлено в spec** (как в CI). LLM может «догадаться» о других проблемах — это даст **ложные срабатывания** (FP) и снизит Precision.

---


## Устранение проблем

| Проблема | Решение |
|---------|---------|
| `OPENAI_API_KEY` не задан | Файл `experiment/.env` |
| `only N mutations` (&lt; 43) | В спеках мало сущностей — нормально, метрики по фактическому N |
| LLM обрезает контекст | Уменьшите модули через `BENCHMARK_MODULES` |
| Линтер 0 ошибок | Сначала `generate_mutations.py`, проверьте пути к `mutated_specs/` |
