# RDE Linter: complete practical guide (EN)

Practical guide for the `requirements_linter` architectural contract checker on Open vAIR.

**What it does:**

- reads the contract from `specs/<feature>.md` (YAML inside a fenced `rde` block);
- scans Python under `openvair/modules/<feature>/`;
- compares spec vs code **via AST only** (no app runtime, tests, or business-logic imports).

---

## 1. Purpose

The linter checks that the codebase **contains** everything declared in the contract:

| Kind | What is matched |
|------|-----------------|
| Classes | Class name and listed **public** methods |
| Module functions | Top-level `def` / `async def` in a given file |
| HTTP (FastAPI) | Method, full path, handler, parameters |

### Errors vs warnings

| Kind | Direction | Exit code | Disable |
|------|-----------|-----------|---------|
| **Error** | spec → code: declared in contract, missing in code | `1` | — |
| **WARNINGS** | code → spec: public symbol in code, not in contract | `0` | `--no-warn-extras` |

Class names **must not** equal reserved sentinels: `$module_functions$`, `$http_endpoints$`.

---

## 2. Contract format

### 2.1 `specs/<feature>.md`

Human-readable header and description, then a machine-readable block:

````markdown
# Open vAIR contract: my_feature

Module overview…

```rde
meta:
  source: openvair/modules/my_feature
feature: my_feature
layers:
  domain:
    required_classes: []
```
````

Loading: `spec_document.load_spec` → `extract_rde_block` → `yaml.safe_load` → `normalize_contract_document`.

Legacy standalone `specs/<feature>.yaml` / `.yml` files are still supported.

### 2.2 DDD layers

Layers: `domain`, `service_layer`, `adapters`, `entrypoints` (`KNOWN_LAYER_NAMES`).

### 2.3 Keys inside the `rde` YAML

| Key | Role |
|-----|------|
| `required_classes` | Class + public methods |
| `required_module_functions` | Path relative to module root + function names |
| `required_http_endpoints` | method, path, handler, parameters |

**Shorthand** (normalized on load): `classes`, `module_functions`, `http` with `router_prefix` / `endpoints`.

Public API: names starting with `_` and dunders `__…__` are not treated as public.

---

## 3. Minimal contract example (YAML inside `rde`)

```yaml
meta:
  source: openvair/modules/my_feature
  maintainer_notes: "RDE contract"

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

## 4. Writing specs that pass reliably

### 4.1 Exact names

- `SchedulerCRUD` ≠ `SchedulerCrud`
- `update_job` ≠ `edit_job`
- `schemas.CreateJobRequest` ≠ `CreateJobRequest`

### 4.2 Real `relative_path`

Function in `openvair/modules/user/entrypoints/api.py` → contract uses `entrypoints/api.py`.

### 4.3 HTTP: method + path + handler

Mismatch → `No matching HTTP route in code for ...`

Parameter mismatch → `parameter contract mismatch` with `spec:` / `code:` lists.

### 4.4 Parameter kind heuristics

| In code | `kind` in spec |
|---------|----------------|
| `Depends(...)` | `depends` |
| `Body` / `Form` / `File` | `body` |
| `schemas.*` annotation | often `body` |
| Otherwise | usually `query` |

Best practice: generate a draft first, then trim to the public contract.

---

## 5. How to run

### 5.1 Single module (recommended)

From repository root:

```bash
python requirements_linter/rde_linter.py specs/user.md openvair/modules/user
```

In-memory demo:

```bash
python requirements_linter/rde_linter.py --demo
```

Exit codes: `0` — no spec → code errors; `1` — errors found. WARNINGS do not change the exit code.

### 5.2 Default when run with no arguments

```bash
python requirements_linter/rde_linter.py
```

Only checks:

- `specs/storage.md`
- `openvair/modules/storage/`

Pass explicit paths to lint other modules.

### 5.3 All specs

```bash
python requirements_linter/lint_repo_specs.py
```

For each `specs/*.md` (legacy `*.yaml` only if no matching `.md`):

- `feature` from contract → `openvair/modules/<feature>/`;
- if `feature` is missing → file stem (`user.md` → `user`).

Pre-commit hook `rde-spec-linter` runs the same script.

```bash
pre-commit install
pre-commit run rde-spec-linter --all-files
```

Use `--no-warn-extras` to suppress code-not-in-contract warnings.

---

## 6. feature → module mapping

| Condition | Module directory |
|-----------|------------------|
| `feature: user` in contract | `openvair/modules/user` |
| No `feature`, file `user.md` | `openvair/modules/user` |

---

## 7. Package layout

| Path | Role |
|------|------|
| `spec_document.py` | `rde` block, `load_spec`, normalization |
| `ast_specs.py` | Layers, `build_code_artifacts`, `load_module_sources` |
| `http_routes.py` | FastAPI route extraction |
| `comparator.py` | `Comparator`, `CompareResult` |
| `analyzer.py` | `AstAnalyzer` |
| `cli.py` | `run_on_openvair_module`, `main` |
| `rde_linter.py` | Single-module CLI entry |
| `lint_repo_specs.py` | Lint all `specs/*.md` |
| `generate_openvair_specs.py` | Draft `specs/<feature>.md` from code |

---

## 8. Typical messages

### 8.1 `Layer '<name>' not found under scanned sources ...`

No `.py` files for the layer or wrong layer name.

### 8.2 `class <Name> not found in code artifacts`

Class missing or wrong layer in contract.

### 8.3 `Class <Name> does not contain expected method <method>`

Public method missing or renamed.

### 8.4 `File '...' does not expose expected top-level callable ...`

Not a top-level function, or wrong path/name.

### 8.5 `Module file '...' was not scanned for functions ...`

Missing file or path not under a known layer.

### 8.6 `No matching HTTP route in code for ...`

method/path/handler mismatch or route not statically extractable.

### 8.7 `parameter contract mismatch`

Mismatch in `(name, kind, required, type_hint)` — align spec with handler signature.

### 8.8 HTTP structure errors in spec

- `required_http_endpoints must be a list`
- `required_http_endpoints entry must be a mapping`
- `HTTP endpoint spec must include non-empty method, path, handler`

### 8.9 Reserved class name

`Spec layer=... uses disallowed class name '$module_functions$' ...`

### 8.10 Missing module directory

`skip — bounded context directory missing (openvair/modules/<feature>)`

### 8.11 WARNINGS (non-blocking)

e.g. `undocumented` — symbol in code not listed in contract. Extend the contract or narrow code API.

---

## 9. FastAPI extraction limits (MVP)

**Supported:**

- `router = APIRouter(prefix="...")` with literal prefix;
- `@router.get|post|put|patch|delete("...")` with literal path;
- top-level handlers.

**Not supported:**

- dynamic path/prefix;
- decorator wrappers;
- `include_router(...)` as contract source;
- metaprogrammed routes.

---

## 10. Recommended workflow

1. Generate draft:

```bash
python requirements_linter/generate_openvair_specs.py --feature my_feature
```

2. Trim `specs/my_feature.md` to the public contract.
3. Lint one module:

```bash
python requirements_linter/rde_linter.py specs/my_feature.md openvair/modules/my_feature
```

4. Fix spec → code errors; optionally address WARNINGS.
5. Lint all: `python requirements_linter/lint_repo_specs.py`.
6. Run pre-commit before push.

---

## 11. FAQ

**Route exists but linter fails?**

Handler name, `type_hint`, `kind` (query vs body), or prefix/path normalization.

**Empty layer?**

Check `.py` under the layer folder and public symbol names.

**Safest update after refactor?**

Regenerate → manual trim → single-module lint loop.

---

## 12. Command cheat sheet

```bash
# Single module
python requirements_linter/rde_linter.py specs/user.md openvair/modules/user

# Without extra-code warnings
python requirements_linter/rde_linter.py specs/user.md openvair/modules/user --no-warn-extras

# All specs
python requirements_linter/lint_repo_specs.py

# Generate draft .md
python requirements_linter/generate_openvair_specs.py --feature user

# Linter tests
python -m pytest requirements_linter/tests -v --override-ini addopts=
```

---

See also the short overview: [README.md](README.md).
