# Отчёт: архитектурный анализ модуля Scheduler (внешние контрибьюторы)

**Дата:** 16.05.2026  
**Источник кода:** ветка [`feature/scheduler-final-branch`](https://github.com/miem-project-2259/openvair/tree/feature/scheduler-final-branch), каталог `openvair/modules/scheduler`  
**Эталон требований:** GitHub issues [#283](https://github.com/miem-project-2259/openvair/issues/283) (domain), [#284](https://github.com/miem-project-2259/openvair/issues/284) (service + adapters), [#285](https://github.com/miem-project-2259/openvair/issues/285) (entrypoints)  
**Контракт для линтера:** `specs/scheduler.md` (блок `` ```rde `` ``, согласован с issues и целевой архитектурой Open vAIR)  
**Инструмент проверки:** RDE-линтер (`requirements_linter/rde_linter.py`), статический разбор AST без запуска кода

---

## 1. Резюме

Модуль scheduler внешних контрибьюторов **в целом повторяет слоистую структуру** Open vAIR (domain → service_layer → adapters → entrypoints), но **систематически расходится** с формулировками issues по именованию, HTTP-контракту, границам слоёв и части бизнес-правил.

| Показатель | Значение |
|------------|----------|
| **Ошибки линтера** (блокирующие, `SPECS MISMATCH`) | **21** |
| **Предупреждения линтера** (`WARNINGS`, лишнее в коде) | **31** |
| Код выхода линтера для форка | `1` (контракт не выполнен) |
| Локальная копия `openvair/modules/scheduler` в этом репозитории | **0 ошибок** по тому же контракту |

Ручной разбор issues и прогон линтера **дополняют друг друга**: issues описывают задумку и критерии приёмки; линтер **механически** сверяет контракт `specs/scheduler.md` с фактическим AST кода (классы, методы, HTTP-маршруты, параметры хендлеров). Сводное сравнение «должно / сделано» — **§3** (одна таблица, построчно).

---

## 2. Методика

1. Shallow-клон ветки `feature/scheduler-final-branch` в `_vendor_scheduler_fork/`.
2. Сопоставление структуры и ключевых файлов с текстом issues #283–#285.
3. Запуск RDE-линтера:

```bash
python requirements_linter/rde_linter.py specs/scheduler.md _vendor_scheduler_fork/openvair/modules/scheduler
```

Контракт в `specs/scheduler.md` отражает **целевое** состояние модуля (имена из issues: `SchedulerCRUD`, `CreateJobRequest`, `SchedulerService`, маршруты `/scheduler/jobs/{job_id}` и т.д.). Форк проверялся **как есть**, без подгонки спеки под реализацию.

---

## 3. Сводная таблица: как должно было быть и как сделано

В одной строке — требование по issues / `specs/scheduler.md` и фактическая реализация в форке `feature/scheduler-final-branch`.  
Колонка **Линтер** — зафиксировал ли RDE-линтер расхождение (`ошибка` / `warn` / `—`).

| Issue | Область | Как должно было быть | Как сделано (форк) | Линтер |
|-------|---------|----------------------|--------------------|--------|
| #285 | Router | Префикс `/scheduler`, CRUD по задачам | Префикс `/scheduler`, глобальная авторизация | — |
| #285 | GET/POST jobs | `GET/POST /scheduler/jobs`, `GET /scheduler/jobs/{job_id}` | Те же пути | — |
| #285 | PATCH/DELETE | `PATCH/DELETE /scheduler/jobs/{job_id}`, handler `update_job` | **`PATCH/DELETE /scheduler/{job_id}`**, handler `edit_job` | ошибка №11, 15–16; warn |
| #285 | CRUD-класс | `SchedulerCRUD`, маппинг исключений RPC → HTTP | `SchedulerCrud`, **без** `HTTPException` в crud; docstring из Template | ошибка №4, 12–14 |
| #285 | Схемы запросов | `CreateJobRequest`, `UpdateJobRequest`, `DeleteJobRequest` | `RequestCreateJob`, `RequestUpdateJob`, `RequestDeleteJob` | ошибка №5–7 |
| #285 | Схемы ответов | `JobResponse`, `JobListResponse`, `JobStatusResponse`, `CreateJobResponse`, `ErrorResponse`, `DeleteResponse` | `JobResponse`, `JobCreateResponse`, `JobDeleteResponse`; **нет** `JobStatusResponse`; список — `Page[JobResponse]` | ошибка №8–10 |
| #285 | OpenAPI / HTTP-статусы | 200, 201, 400, 404, 409, 422, 500 в документации | Только `404` в `responses`; `ErrorResponse` не на роутере | — |
| #285 | DELETE status | **200 OK** после удаления | **202 Accepted** | — |
| #285 | DeleteJobRequest | Body/query по контракту | Схема есть, DELETE только `job_id` в path | — |
| #285 | Опасные команды | Запрет `rm -rf`, `dd`, `mkfs`, `curl`, `wget` | `FORBIDDEN_COMMAND_PATTERNS` + `validate_command` | — |
| #285 | Символы `&`, `;`, `\|` | Запрет без валидации | Regex **разрешает** | — |
| #284 | Сервисный класс | `SchedulerService` | `SchedulerServiceLayerManager` (+ `monitoring`, `get_job`) | ошибка №17; warn |
| #284 | Методы CRUD SL | `get_all_jobs`, `create_job`, `edit_job`, `delete_job` | Те же + `get_job` | — |
| #284 | UoW | `SchedulerSqlAlchemyUnitOfWork` | Реализован | — |
| #284 | RPC service | `service_layer/manager.py`, очередь API↔SL | Есть, очереди через `RPC_QUEUES.Scheduler.*` | — |
| #284 | Исключения SL | `SchedulerServiceException`, `JobNotFoundError`, `JobAlreadyExistsError`, `InvalidJobDataError`, `JobExecutionError` | `JobNameAlreadyExists`, `JobInvalidNameError`, `JobFieldIsNotEditable` и др.; **нет** трёх классов из issue | ошибка №18–21; warn |
| #284 | ORM `scheduler_jobs` | Полный набор полей + timestamps | Реализован | — |
| #284 | Repository | `SqlAlchemySchedulerRepository`: get, get_all, update, delete, get_by_name | `SchedulerSqlAlchemyRepository`: get_by_id, add, delete; update через session | ошибка №1; warn |
| #284 | Serializer | `SchedulerJobSerializer`: to_web, to_domain, to_db | Реализован | — |
| #284 | Миграция Alembic | Таблица `scheduler_jobs` | `99d3c25dbacc_add_scheduler_jobs.py` | — |
| #284 | Уникальное имя / cron | Валидация в SL | Проверяется | — |
| #284 | Макс. 10 задач | Проверка при создании | `MAX_CONCURRENT_JOBS=10` в config, **не используется** | — |
| #284 | Интервал ≥ 1 мин | Валидация cron | `_enforce_minute_granularity` в requests | — |
| #284 | Таймаут / логи | `JOB_TIMEOUT`, `LOG_RETENTION_DAYS` в логике | Только константы в config | — |
| #284 | Удаление с зависимостями | `JobExecutionError` / проверка | **Нет** | — |
| #284 | CRON_USER в RPC | `openvair` | Вызовы domain с **`user: 'root'`** | — |
| #283 | BaseScheduler / CronJob | `python-crontab`, create/edit/delete | Есть + `get`, `list_all` | warn |
| #283 | Factory | `SchedulerFactory`, `CronJobScheduler` | Реализован | — |
| #283 | Domain RPC manager | `SchedulerDomainManager` в `domain/manager.py` | **`manager=SchedulerFactory()`** (вызов create/edit/delete на экземпляре cron) | ошибка №3 |
| #283 | Файл исключений | `domain/exceptions.py`, `SchedulerDomainException` | `domain/exception.py`, база в `shared/` | ошибка №2 |
| #283 | Доменные исключения | `CronJobNotFound`, `InvalidCronExpression`, системные cron | Есть + `CronTabRead/Write`, `CronDaemonException` | warn |
| #283 | Изоляция слоёв | Domain не зависит от entrypoints | **`cron_job.py` импортирует entrypoints.schemas** | — |
| #283 | DomainSchedulerModelDTO | Валидная DTO | Docstring «Заглушка» | warn |
| #283 | Cron user | `openvair` | config `openvair`, runtime **root** (см. строку CRON_USER выше) | — |

**Примечание к domain RPC:** Open vAIR инициализирует `manager(data_for_manager)` и вызывает метод на экземпляре планировщика. С `SchedulerFactory` цепочка **может работать**, но это не соответствует issue (отдельный `SchedulerDomainManager`).

Линтер **не проверяет** семантику безопасности, лимиты задач и выбор пользователя cron — только структурный контракт (классы, методы, HTTP).

---

## 4. Роль RDE-линтера в поиске несостыковок

### 4.1. Что линтер проверяет

- Наличие **классов и публичных методов** по слоям (`domain`, `service_layer`, `adapters`, `entrypoints`).
- Топ-уровневые функции в `entrypoints/api.py`.
- **HTTP-маршруты** FastAPI: метод, полный path, имя handler, параметры (Depends, body, path).

Сравнение **одностороннее по ошибкам**: всё, что заявлено в `specs/scheduler.md`, обязано быть в коде. Предупреждения показывают «лишнее» в коде, не описанное в контракте.

### 4.2. Сводка результатов прогона

**Объект:** `_vendor_scheduler_fork/openvair/modules/scheduler`  
**Контракт:** `specs/scheduler.md`

| Тип | Количество |
|-----|------------|
| **Ошибки (`errors`)** | **21** |
| **Предупреждения (`warnings`)** | **31** |
| Exit code | `1` |

**Справочно:** локальный `openvair/modules/scheduler` в этом репозитории по тому же контракту даёт **0 ошибок** — контракт отражает исправленную/целевую реализацию после доработок.

### 4.3. Полный список ошибок линтера (21)

| № | Слой | Сообщение линтера |
|---|------|-------------------|
| 1 | adapters | class `SqlAlchemySchedulerRepository` not found (в коде: `SchedulerSqlAlchemyRepository`) |
| 2 | domain | class `SchedulerDomainException` not found |
| 3 | domain | class `SchedulerDomainManager` not found |
| 4 | entrypoints | class `SchedulerCRUD` not found (в коде: `SchedulerCrud`) |
| 5 | entrypoints | class `CreateJobRequest` not found |
| 6 | entrypoints | class `UpdateJobRequest` not found |
| 7 | entrypoints | class `DeleteJobRequest` not found |
| 8 | entrypoints | class `JobStatusResponse` not found |
| 9 | entrypoints | class `CreateJobResponse` not found |
| 10 | entrypoints | class `DeleteResponse` not found |
| 11 | entrypoints | нет callable `update_job` в `api.py` (есть `edit_job`) |
| 12 | entrypoints | GET `/scheduler/jobs`: mismatch параметров (`SchedulerCrud` vs `SchedulerCRUD`) |
| 13 | entrypoints | GET `/scheduler/jobs/{job_id}`: mismatch параметров |
| 14 | entrypoints | POST `/scheduler/jobs`: mismatch (`RequestCreateJob` / query vs body / `CreateJobRequest`) |
| 15 | entrypoints | нет PATCH `/scheduler/jobs/{job_id}` handler `update_job` |
| 16 | entrypoints | нет DELETE `/scheduler/jobs/{job_id}` handler `delete_job` |
| 17 | service_layer | class `SchedulerService` not found |
| 18 | service_layer | class `SchedulerServiceException` not found |
| 19 | service_layer | class `JobAlreadyExistsError` not found |
| 20 | service_layer | class `InvalidJobDataError` not found |
| 21 | service_layer | class `JobExecutionError` not found |

### 4.4. Категории предупреждений (31, кратко)

Линтер дополнительно сообщил о символах **в коде, но не в контракте**, в том числе:

- **Entrypoints:** `SchedulerCrud`, `RequestCreateJob`, `JobCreateResponse`, `edit_job`, маршруты `PATCH/DELETE /scheduler/{job_id}`.
- **Domain:** вспомогательные исключения cron, `JobMetadata`, методы `get`/`list_all`.
- **Service layer:** `JobNameAlreadyExists`, `monitoring`, `get_job`.
- **Adapters:** DTO команд, `SchedulerSqlAlchemyRepository`.

Предупреждения полезны при **ревью**: показывают, что реализация разошлась с контрактом не только «не хватает», но и «лишнее/другое имя».

### 4.5. Вывод по линтеру

Из **32 строк** сводной таблицы (§3) линтер помечает колонкой «ошибка» или «warn» **15 строк** (структура: имена классов, HTTP, параметры). Строки с «—» в колонке линтера (безопасность `&;|`, лимит 10 задач, `CRON_USER` vs `root`, DELETE 202, copy-paste Template) выявлены только ручным разбором.

**Итого:** **21 ошибка** и **31 предупреждение** при прогоне; линтер закрывает примерно **половину** явных расхождений из таблицы, остальное — семантика и поведение вне AST-контракта.

---

## 5. Рекомендации (для приёмки PR)

1. Исправить маршруты: `PATCH`/`DELETE` → `/scheduler/jobs/{job_id}`, handler `update_job`, статус DELETE → 200.
2. Ввести алиасы или переименование под контракт: `SchedulerCRUD`, `CreateJobRequest`, …
3. Добавить `SchedulerDomainManager` (или обновить spec, если сознательно оставляют factory).
4. Убрать импорты entrypoints из domain; использовать domain/DTO.
5. Использовать `CRON_USER` из config в RPC; реализовать `MAX_CONCURRENT_JOBS` и проверку зависимостей при delete.
6. Подключить `ErrorResponse` к роутеру и маппинг исключений в `crud.py`.
7. В CI: `python requirements_linter/rde_linter.py specs/scheduler.md openvair/modules/scheduler` — exit code 0 как критерий приёмки.

---

## 6. Команда воспроизведения

```bash
# Форк контрибьюторов (ожидается 21 ошибка, 31 предупреждение)
python requirements_linter/rde_linter.py specs/scheduler.md _vendor_scheduler_fork/openvair/modules/scheduler

# Только ошибки, без предупреждений
python requirements_linter/rde_linter.py specs/scheduler.md _vendor_scheduler_fork/openvair/modules/scheduler --no-warn-extras

# Локальная целевая реализация в репозитории (0 ошибок)
python requirements_linter/rde_linter.py specs/scheduler.md openvair/modules/scheduler
```

---

*Отчёт подготовлен в рамках работы над ВКР по инструменту RDE-линтинга архитектурных контрактов Open vAIR.*
