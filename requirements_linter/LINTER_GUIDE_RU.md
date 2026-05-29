# RDE Linter: полное руководство (RU)

Практическое руководство по линтеру архитектурных контрактов `requirements_linter` для Open vAIR.

**Что делает линтер:**

- читает контракт из `specs/<feature>.md` (YAML внутри fenced-блока `rde`);
- сканирует Python в `openvair/modules/<feature>/`;
- сравнивает spec и код **только через AST** (без запуска приложения, тестов и импорта бизнес-логики).

---

## 1. Функциональное назначение

Линтер проверяет, что в коде **присутствуют** все сущности, заявленные в контракте:

| Тип | Что сверяется |
|-----|----------------|
| Классы | Имя класса и перечисленные **публичные** методы |
| Функции модуля | Top-level `def` / `async def` в указанном файле |
| HTTP (FastAPI) | Метод, полный путь, handler, параметры |

### Ошибки и предупреждения

| Тип | Направление | Код выхода | Отключение |
|-----|-------------|------------|------------|
| **Ошибка** | spec → code: в контракте есть, в коде нет | `1` | — |
| **WARNINGS** | code → spec: в коде есть публичная сущность, в контракте нет | `0` | `--no-warn-extras` |

Имена классов **не должны** совпадать со служебными: `$module_functions$`, `$http_endpoints$`.

---

## 2. Формат контракта

### 2.1 Файл `specs/<feature>.md`

В начале — заголовок и пояснение для человека. Машиночитаемая часть — блок:

````markdown
# Open vAIR contract: my_feature

Описание модуля…

```rde
meta:
  source: openvair/modules/my_feature
feature: my_feature
layers:
  domain:
    required_classes: []
```
````

Загрузка: `spec_document.load_spec` → `extract_rde_block` → `yaml.safe_load` → `normalize_contract_document`.

Поддерживаются устаревшие отдельные файлы `specs/<feature>.yaml` / `.yml`.

### 2.2 Слои DDD

Проверка идёт по каталогам: `domain`, `service_layer`, `adapters`, `entrypoints` (константа `KNOWN_LAYER_NAMES`).

### 2.3 Ключи в YAML внутри `rde`

| Ключ | Назначение |
|------|------------|
| `required_classes` | Класс + список публичных методов |
| `required_module_functions` | `relative_path` от корня модуля + список функций |
| `required_http_endpoints` | method, path, handler, parameters |

**Сокращённая запись** (нормализуется при загрузке): `classes`, `module_functions`, `http` с `router_prefix` / `endpoints`.

Публичность: имена с `_` в начале и дандеры `__…__` не считаются публичным API.

---

## 3. Минимальный пример контракта (YAML в блоке `rde`)

```yaml
meta:
  source: openvair/modules/my_feature
  maintainer_notes: "Contract for RDE linter"

feature: my_feature

layers:
  domain:
    required_classes:
      - name: MyDomainService
        methods:
          - create
          - delete

  entrypoints:
    required_classes:
      - name: MyCrud
        methods:
          - get_items
    required_module_functions:
      - relative_path: entrypoints/api.py
        functions:
          - get_items
    required_http_endpoints:
      - method: GET
        path: /items
        handler: get_items
        parameters:
          - name: crud
            kind: depends
            required: true
            type_hint: MyCrud
```

---

## 4. Как писать спецификацию, чтобы проверка проходила

### 4.1 Имена — один в один

- `SchedulerCRUD` ≠ `SchedulerCrud`
- `update_job` ≠ `edit_job`
- `schemas.CreateJobRequest` ≠ `CreateJobRequest`

### 4.2 `relative_path` должен существовать

Функция в `openvair/modules/user/entrypoints/api.py` → в контракте `entrypoints/api.py`.

### 4.3 HTTP: тройка method + path + handler

При несовпадении: `No matching HTTP route in code for ...`

При расхождении параметров: `parameter contract mismatch` (списки `spec:` и `code:`).

### 4.4 Эвристики параметров HTTP

| В коде | `kind` в spec |
|--------|----------------|
| `Depends(...)` | `depends` |
| `Body` / `Form` / `File` | `body` |
| Аннотация `schemas.*` | часто `body` |
| Остальное | обычно `query` |

Рекомендация: сначала автогенерация, затем ручная чистка до публичного контракта.

---

## 5. Запуск

### 5.1 Один модуль (рекомендуется при разработке)

Из корня репозитория:

```bash
python requirements_linter/rde_linter.py specs/user.md openvair/modules/user
```

Демо без диска:

```bash
python requirements_linter/rde_linter.py --demo
```

Коды возврата: `0` — нет ошибок spec → code; `1` — есть ошибки. WARNINGS на код выхода не влияют.

### 5.2 Запуск без аргументов

```bash
python requirements_linter/rde_linter.py
```

По умолчанию проверяются только:

- `specs/storage.md`
- `openvair/modules/storage/`

Частая причина «мой модуль не проверился» — не переданы пути явно.

### 5.3 Все спецификации

```bash
python requirements_linter/lint_repo_specs.py
```

Для каждого `specs/*.md` (если нет `.md` — устаревшие `*.yaml` без пары `.md`):

- `feature` из контракта → `openvair/modules/<feature>/`;
- если `feature` нет — имя файла без расширения (`user.md` → `user`).

Pre-commit: хук `rde-spec-linter` вызывает этот же скрипт.

```bash
pre-commit install
pre-commit run rde-spec-linter --all-files
```

Флаг `--no-warn-extras` подавляет WARNINGS при массовом прогоне.

---

## 6. Сопоставление feature → module

В `lint_repo_specs.py`:

| Условие | Каталог модуля |
|---------|----------------|
| В контракте есть `feature: user` | `openvair/modules/user` |
| Поля `feature` нет, файл `user.md` | `openvair/modules/user` |

---

## 7. Структура пакета

| Путь | Назначение |
|------|------------|
| `spec_document.py` | Блок `rde`, `load_spec`, нормализация |
| `ast_specs.py` | Слои, `build_code_artifacts`, `load_module_sources` |
| `http_routes.py` | Извлечение маршрутов FastAPI |
| `comparator.py` | `Comparator`, `CompareResult` |
| `analyzer.py` | `AstAnalyzer` |
| `cli.py` | `run_on_openvair_module`, `main` |
| `rde_linter.py` | Точка входа CLI одного модуля |
| `lint_repo_specs.py` | Прогон всех `specs/*.md` |
| `generate_openvair_specs.py` | Черновик `specs/<feature>.md` из кода |

---

## 8. Типовые ошибки

### 8.1 `Layer '<name>' not found under scanned sources ...`

Нет подходящих `.py` в слое или неверное имя слоя. Проверьте каталоги и YAML.

### 8.2 `class <Name> not found in code artifacts`

Класс не найден в указанном слое — имя или слой в контракте.

### 8.3 `Class <Name> does not contain expected method <method>`

Нет публичного метода с таким именем.

### 8.4 `File '...' does not expose expected top-level callable ...`

Нет top-level функции; возможно, это метод класса.

### 8.5 `Module file '...' was not scanned for functions ...`

Файл отсутствует или путь не в распознанном слое.

### 8.6 `No matching HTTP route in code for ...`

Не совпали method/path/handler или роут не извлечён статически.

### 8.7 `parameter contract mismatch`

Расхождение `(name, kind, required, type_hint)` — выровняйте spec с сигнатурой handler.

### 8.8 Ошибки структуры HTTP в spec

- `required_http_endpoints must be a list`
- `required_http_endpoints entry must be a mapping`
- `HTTP endpoint spec must include non-empty method, path, handler`

### 8.9 Зарезервированное имя класса

`Spec layer=... uses disallowed class name '$module_functions$' ...`

### 8.10 Отсутствует каталог модуля

`skip — bounded context directory missing (openvair/modules/<feature>)`

### 8.11 WARNINGS (не блокируют)

Пример: `undocumented` — метод или сущность в коде не перечислены в контракте. Сузьте контракт или добавьте сущность в spec.

---

## 9. Ограничения извлечения HTTP (MVP)

**Поддерживается:**

- `router = APIRouter(prefix="...")` с литеральным prefix;
- `@router.get|post|put|patch|delete("...")` с литеральным path;
- top-level handlers.

**Не поддерживается:**

- динамические path/prefix;
- обёртки вокруг декораторов;
- `include_router(...)` как источник контракта;
- метапрограммная генерация маршрутов.

---

## 10. Рекомендуемый рабочий процесс

1. Сгенерировать черновик:

```bash
python requirements_linter/generate_openvair_specs.py --feature my_feature
```

2. Оставить в `specs/my_feature.md` только публичный контракт.
3. Проверить один модуль:

```bash
python requirements_linter/rde_linter.py specs/my_feature.md openvair/modules/my_feature
```

4. Исправить ошибки spec → code; при необходимости дополнить контракт по WARNINGS.
5. Прогнать все спеки: `python requirements_linter/lint_repo_specs.py`.
6. Перед коммитом — pre-commit.

---

## 11. FAQ

**Почему mismatch при видимом endpoint?**

Часто: другой handler, `type_hint`, `kind` (query vs body), нормализация prefix/path.

**Почему слой пустой?**

Проверьте `.py` в каталоге слоя, публичные имена, что первый сегмент пути — имя слоя.

**Как обновить spec после рефакторинга?**

Автогенерация → ручная чистка → точечная проверка модуля.

---

## 12. Команды — шпаргалка

```bash
# Один модуль
python requirements_linter/rde_linter.py specs/user.md openvair/modules/user

# Без предупреждений о «лишнем» коде
python requirements_linter/rde_linter.py specs/user.md openvair/modules/user --no-warn-extras

# Все спецификации
python requirements_linter/lint_repo_specs.py

# Генерация черновика .md
python requirements_linter/generate_openvair_specs.py --feature user

# Тесты линтера
python -m pytest requirements_linter/tests -v --override-ini addopts=
```

---

См. также краткий обзор: [README.md](README.md).
