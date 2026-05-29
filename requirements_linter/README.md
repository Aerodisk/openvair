# RDE: линтер YAML-спецификаций (OpenVAir)

Инструмент **детерминированной** проверки: контракт в `specs/<feature>.md` (блок `` ```rde `` с YAML внутри) сопоставляется с исходниками Python в `openvair/modules/<feature>/` только через разбор AST (рантайм и тесты не выполняются).

## Что именно проверяется

В каждом bounded context (`openvair/modules/<имя>/`):

1. **`required_classes`** (по архитектурным каталогам: `domain/`, `service_layer/`, `adapters/`, `entrypoints/`)
   - Классы с указанным именем реально есть на этом слое (объединяются несколько файлов).
   - Каждый перечисленный **метод** существует у класса как **публичный** метод (имена, начинающиеся с `_`, и дандеры учитываются как «непубличные»).

2. **`required_module_functions`**
   - Топ-уровневые `def` / `async def` в файле с заданным **относительным путём** от корня модуля (частый случай — `entrypoints/api.py`).

3. **`required_http_endpoints`** (опционально, обычно на слое `entrypoints`)
   - Маршруты FastAPI извлекаются статически: `@router.get|post|put|patch|delete(...)` при литеральном `APIRouter(prefix=...)`.
   - Сверяются **метод HTTP**, **полный путь**, **имя хендлера** и набор параметров `(name, kind, required, type_hint)`.

**Направление соответствия (ошибки, блокируют коммит):** всё, что **заявлено в контракте**, **обязано** быть в коде в том же виде.

**Предупреждения (по умолчанию включены):** публичные классы, методы, функции и HTTP-маршруты в коде, которых **нет** в контракте, выводятся как `WARNINGS`, но **не** меняют код выхода. Отключить: `--no-warn-extras`.

Имена классов **не должны** совпадать со служебными ключами: `'$module_functions$'`, `'$http_endpoints$'`.

## Зависимости

- Python 3.10+ (используется `ast.unparse`).
- `PyYAML`.

## Структура пакета

| Путь | Назначение |
|------|------------|
| `ast_specs.py` | Слои, `build_code_artifacts`, `load_module_sources` |
| `http_routes.py` | Извлечение маршрутов и параметров FastAPI |
| `comparator.py` | `Comparator` — сравнение YAML с `code_artifacts` |
| `analyzer.py` | `AstAnalyzer` — диск или строки в памяти |
| `cli.py` | Реализация CLI одного модуля (`main`, argparse, `--demo`) |
| `rde_linter.py` | Точка входа: `python requirements_linter/rde_linter.py …` |
| `spec_document.py` | Извлечение блока ``rde`` из Markdown, нормализация контракта |
| `lint_repo_specs.py` | Прогон **всех** `specs/*.md` |
| `generate_openvair_specs.py` | Перегенерация `specs/<feature>.md` из кода |
| `specs/*.md` | Контракты (человекочитаемая обёртка + `` ```rde ``); `feature` = папка в `openvair/modules/` |

## Генерация или обновление спецификации

Из **корня репозитория**:

```bash
python requirements_linter/generate_openvair_specs.py --feature storage
python requirements_linter/generate_openvair_specs.py --feature virtual_machines --out-dir specs
```

- Читает все `*.py` под `openvair/modules/<feature>/`, кроме `tests/` и `__pycache__/`.
- Пишет `specs/<feature>.yaml` (или каталог из `--out-dir`).

Автоген — это **черновик**: после генерации обычно оставляют только публичный контракт модуля.

## Запуск линтера (один bounded context)

**Важно про умолчания:** если выполнить `python requirements_linter/rde_linter.py` **без аргументов**, сравниваются только `specs/storage.yaml` и `openvair/modules/storage/`. Правка `specs/user.yaml` при таком запуске **не проверится**.

Явно указать спеку и каталог модуля (из корня репозитория):

```bash
python requirements_linter/rde_linter.py specs/user.yaml openvair/modules/user
```

Демо без чтения с диска:

```bash
python requirements_linter/rde_linter.py --demo
```

Код выхода: `0` — нет расхождений, `1` — есть ошибки (печать в stdout).

## Запуск линтера (все спеки)

```bash
python requirements_linter/lint_repo_specs.py
```

Для каждого `specs/*.yaml`:

- Берётся поле `feature`; если его нет — используется имя файла без `.yaml` (`user.yaml` → модуль `user`).
- Ожидается каталог `openvair/modules/<feature>/`; если его нет — сообщение в stderr, код выхода `1`.
- Дальше — та же логика, что и при проверке одного модуля.

Этот скрипт вызывается хуком **pre-commit** `rde-spec-linter` в `.pre-commit-config.yaml`.

## Pre-commit

Хук выполняет:

```text
python requirements_linter/lint_repo_specs.py
```

Установка (из корня репозитория):

```bash
pre-commit install
pre-commit run rde-spec-linter --all-files
```

## Минимальная структура YAML

Обычно используются ключи верхнего уровня:

```yaml
meta:
  source: openvair/modules/my_feature
  maintainer_notes: "..."
feature: my_feature
layers:
  domain:
    required_classes:
      - name: SomeClass
        methods:
          - public_method
  entrypoints:
    required_classes: []
    required_module_functions:
      - relative_path: entrypoints/api.py
        functions:
          - list_things
    required_http_endpoints:
      - method: GET
        path: /things/
        handler: list_things
        parameters:
          - name: crud
            kind: depends
            required: true
            type_hint: ThingCrud
```

Имена слоёв должны входить во множество `KNOWN_LAYER_NAMES` в `ast_specs.py`.

## Ограничения извлечения HTTP (MVP)

Поддерживается: присваивания `router = APIRouter(prefix="...", ...)`, декораторы `@router.<метод>("<литеральный путь>", ...)` у топ-уровневых хендлеров, литеральные строки пути и prefix.

Не поддерживается без доработки кода: динамические пути, неконстантный `prefix`, условные декораторы, `include_router(...)`.

Тела запросов классифицируются эвристикой (например, типы вида `schemas.Model` считаются `body`). Схемы без префикса `schemas.` могут быть ошибочно отнесены к query.

## Тесты

```bash
python -m pytest requirements_linter/tests -v --override-ini addopts=
```

Если в `pytest.ini` задано `addopts = --order-scope=module`, а плагин `pytest-order` не установлен, передавайте `--override-ini addopts=`, как выше.

## Типичные проблемы

| Симптом | Причина |
|---------|---------|
| Линтер не демонистрирует проблем при их явном наличии | Запуск без аргументов проверяет только модуль **storage** по умолчанию. Нужно явно передать путь к YAML и к `openvair/modules/<feature>`. |
| «Layer not found under scanned sources» | В этом слое нет подходящих `.py` (первый сегмент пути файла должен быть одним из: `domain`, `service_layer`, `adapters`, `entrypoints`). |
| Расхождение по HTTP-парам после ручного редактирования | Ручная правка `required_http_endpoints` разошлась с кодом; перегенерируйте спеку или выровняйте строки параметров один в один. |

## Связь с корневым `README.md`

В корне репозитория может быть описан **другой** эксперимент (markdown-спеки и вызовы `openvair.requirements_linter.cli`). **Актуальный** рабочий цикл этого репозитория — YAML в `specs/` и скрипты из `requirements_linter/`, как в этом файле.

---

### English summary

The same workflow in short: YAML under `specs/` is checked against `openvair/modules/<feature>/` via AST. Single module: `python requirements_linter/rde_linter.py specs/<f>.yaml openvair/modules/<f>`. All specs: `python requirements_linter/lint_repo_specs.py`. Default CLI path pair is **storage** only.
