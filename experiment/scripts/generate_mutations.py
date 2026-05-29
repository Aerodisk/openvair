#!/usr/bin/env python3
"""Build mutated specs + ground_truth.json for the benchmark (43 defects)."""

from __future__ import annotations

import copy
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve().parents[2]
if str(_BOOT) not in sys.path:
    sys.path.insert(0, str(_BOOT))

from experiment.config import (  # noqa: E402
    GROUND_TRUTH_PATH,
    MODULES,
    MUTATED_SPECS_DIR,
    SPECS_SOURCE_DIR,
    TARGET_MUTATION_COUNT,
)
from requirements_linter.spec_document import (  # noqa: E402
    contract_to_markdown,
    load_spec,
)


@dataclass
class MutationPlan:
    module: str
    kind: str
    layer: str
    description: str
    linter_needles: tuple[str, ...]
    llm_needles: tuple[str, ...]

    def to_ground_truth_row(self, mutation_id: int) -> dict[str, Any]:
        return {
            'id': mutation_id,
            'module': self.module,
            'kind': self.kind,
            'layer': self.layer,
            'description': self.description,
            'linter_needles': list(self.linter_needles),
            'llm_needles': list(self.llm_needles),
        }


def _wrong_name(name: str, suffix: str = '_rde_mut') -> str:
    if name.endswith(suffix):
        return name + '_x'
    return name + suffix


def _apply_next_mutation(
    module: str,
    doc: dict[str, Any],
    state: dict[str, int],
) -> MutationPlan | None:
    layers = doc.get('layers', {})
    if not isinstance(layers, dict):
        return None

    for layer_name, layer_data in layers.items():
        if not isinstance(layer_data, dict):
            continue

        for req_cls in layer_data.get('required_classes', []):
            if not isinstance(req_cls, dict):
                continue
            cls_name = str(req_cls.get('name', ''))
            methods = req_cls.get('methods', [])
            if isinstance(methods, list) and methods:
                for method in list(methods):
                    method_str = str(method)
                    if '_rde_mut' in method_str:
                        continue
                    wrong = _wrong_name(method_str)
                    methods[methods.index(method)] = wrong
                    return MutationPlan(
                        module=module,
                        kind='wrong_method',
                        layer=layer_name,
                        description=f'{cls_name}.{method} -> {wrong} in spec',
                        linter_needles=(
                            f'Class {cls_name} does not contain',
                            f'expected method {wrong}',
                        ),
                        llm_needles=(wrong, cls_name, str(method)),
                    )
            elif cls_name and not str(cls_name).startswith('PhantomRde_'):
                state['phantom'] += 1
                phantom = f'PhantomRde_{module}_{layer_name}_{state["phantom"]}'
                layer_data.setdefault('required_classes', []).append(
                    {'name': phantom, 'methods': ['run']},
                )
                return MutationPlan(
                    module=module,
                    kind='phantom_class',
                    layer=layer_name,
                    description=f'Phantom class {phantom} added',
                    linter_needles=(f'class {phantom} not found',),
                    llm_needles=(phantom,),
                )

        for mf in layer_data.get('required_module_functions', []):
            if not isinstance(mf, dict):
                continue
            rel = str(mf.get('relative_path', ''))
            fns = mf.get('functions', [])
            if isinstance(fns, list):
                for fn in list(fns):
                    wrong = _wrong_name(str(fn))
                    fns[fns.index(fn)] = wrong
                    return MutationPlan(
                        module=module,
                        kind='wrong_callable',
                        layer=layer_name,
                        description=f'{rel}: {fn} -> {wrong}',
                        linter_needles=(
                            f"expected top-level callable '{wrong}'",
                            wrong,
                        ),
                        llm_needles=(wrong, str(fn), rel),
                    )

        http_eps = layer_data.get('required_http_endpoints', [])
        if isinstance(http_eps, list):
            for ep in http_eps:
                if not isinstance(ep, dict):
                    continue
                path = str(ep.get('path', ''))
                if path.endswith('/__rde_mut__'):
                    continue
                method = str(ep.get('method', 'GET')).upper()
                handler = str(ep.get('handler', ''))
                wrong_path = path.rstrip('/') + '/__rde_mut__'
                ep['path'] = wrong_path
                return MutationPlan(
                    module=module,
                    kind='wrong_http_path',
                    layer=layer_name,
                    description=f'HTTP {method} {path!r} -> {wrong_path!r}',
                    linter_needles=(
                        'No matching HTTP route in code for',
                        wrong_path,
                        handler,
                    ),
                    llm_needles=(wrong_path, handler, method),
                )

    return None


def _build_module_mutations(
    module: str,
    base_doc: dict[str, Any],
    max_count: int,
) -> tuple[list[MutationPlan], dict[str, Any]]:
    doc = copy.deepcopy(base_doc)
    state = {'phantom': 0}
    plans: list[MutationPlan] = []
    while len(plans) < max_count:
        plan = _apply_next_mutation(module, doc, state)
        if plan is None:
            break
        plans.append(plan)
    return plans, doc


def main() -> int:
    MUTATED_SPECS_DIR.mkdir(parents=True, exist_ok=True)
    selected: list[MutationPlan] = []
    mutated_docs: dict[str, dict[str, Any]] = {}
    remaining = TARGET_MUTATION_COUNT
    per_module_cap = max(1, (TARGET_MUTATION_COUNT + len(MODULES) - 1) // len(MODULES))

    for module in MODULES:
        if remaining <= 0:
            break
        src = SPECS_SOURCE_DIR / f'{module}.md'
        if not src.is_file():
            print(f'SKIP {module}: missing {src}', file=sys.stderr)
            continue
        base = load_spec(src)
        batch = min(remaining, per_module_cap)
        plans, doc = _build_module_mutations(module, base, batch)
        if plans:
            selected.extend(plans)
            remaining -= len(plans)
            mutated_docs[module] = doc
            print(f'{module}: {len(plans)} mutations')

    # Modules without mutations still need baseline mutated file = copy of original
    for module in MODULES:
        src = SPECS_SOURCE_DIR / f'{module}.md'
        if module not in mutated_docs and src.is_file():
            mutated_docs[module] = copy.deepcopy(load_spec(src))

    if len(selected) < TARGET_MUTATION_COUNT:
        print(
            f'WARNING: {len(selected)} mutations (target {TARGET_MUTATION_COUNT})',
            file=sys.stderr,
        )

    for module in MODULES:
        if module not in mutated_docs:
            continue
        out = MUTATED_SPECS_DIR / f'{module}.md'
        out.write_text(
            contract_to_markdown(
                mutated_docs[module],
                title=f'Open vAIR contract (mutated benchmark): {module}',
            ),
            encoding='utf-8',
        )

    payload = {
        'version': 1,
        'target_count': TARGET_MUTATION_COUNT,
        'actual_count': len(selected),
        'modules': list(MODULES),
        'mutations': [p.to_ground_truth_row(i) for i, p in enumerate(selected, 1)],
    }
    GROUND_TRUTH_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'Wrote {GROUND_TRUTH_PATH} ({len(selected)} mutations)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
