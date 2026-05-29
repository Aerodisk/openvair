"""Compare layered YAML contracts with ``build_code_artifacts`` output."""

from __future__ import annotations

from typing import NamedTuple, cast

from requirements_linter.ast_specs import (
    HTTP_ENDPOINTS_BUCKET,
    MODULE_FUNCTIONS_BUCKET,
    normalize_rel_path,
)

_SENTINEL_CLASS_NAMES = frozenset({
    MODULE_FUNCTIONS_BUCKET,
    HTTP_ENDPOINTS_BUCKET,
})


class CompareResult(NamedTuple):
    """Linter outcome: blocking errors and optional non-blocking warnings."""

    errors: list[str]
    warnings: list[str]


def _freeze_http_parameter_rows(
    params_raw: object,
) -> tuple[tuple[str, str, bool, str], ...]:
    """Comparable (name, kind, required, type_hint) rows for an endpoint."""
    if not isinstance(params_raw, list):
        return ()
    rows: list[tuple[str, str, bool, str]] = []
    for p in params_raw:
        if not isinstance(p, dict):
            continue
        name = str(p.get('name', ''))
        kind = str(p.get('kind', ''))
        req_raw = p.get('required')
        required_b = True if req_raw is None else bool(req_raw)
        th = str(p.get('type_hint') or '')
        rows.append((name, kind, required_b, th))
    rows.sort(key=lambda t: t[0])
    return tuple(rows)


def _http_endpoint_triple(ep: dict) -> tuple[str, str, str]:
    return (
        str(ep.get('method', '')).upper(),
        str(ep.get('path', '')),
        str(ep.get('handler', '')),
    )


def _mf_actual_map(layer_bucket: dict[str, object]) -> dict[str, list[str]]:
    mf_actual_raw = layer_bucket.get(MODULE_FUNCTIONS_BUCKET, {})
    if isinstance(mf_actual_raw, dict):
        return cast('dict[str, list[str]]', mf_actual_raw)
    return {}


def _known_methods_for_class(
    errors: list[str],
    layer_name: str,
    layer_bucket: dict[str, object],
    expected_name: str,
) -> list[str] | None:
    if expected_name not in layer_bucket:
        errors.append(
            f'Layer: {layer_name}\n'
            f' class {expected_name} not found in code artifacts'
        )
        return None
    current_methods_raw = layer_bucket[expected_name]
    if not isinstance(current_methods_raw, list):
        msg = (
            f'Internal error: expected list of methods for class '
            f'{expected_name}, got {type(current_methods_raw).__name__}.'
        )
        errors.append(msg)
        return None
    return [str(m) for m in current_methods_raw]


def _compare_one_required_class(
    errors: list[str],
    layer_name: str,
    layer_bucket: dict[str, object],
    req_class: dict,
) -> None:
    expected_name = req_class['name']
    expected_methods = req_class['methods']

    if expected_name in _SENTINEL_CLASS_NAMES:
        msg = (
            f'Spec layer={layer_name!r} uses disallowed class name '
            f'{expected_name!r}: reserved linter sentinel key.'
        )
        errors.append(msg)
        return

    known_methods_list = _known_methods_for_class(
        errors,
        layer_name,
        layer_bucket,
        expected_name,
    )
    if known_methods_list is None:
        return

    for expected_method in expected_methods:
        if expected_method not in known_methods_list:
            errors.append(
                f'Layer: {layer_name}\n'
                f' Class {expected_name} does not contain'
                f' expected method {expected_method}'
            )


def _compare_required_classes(
    errors: list[str],
    layer_name: str,
    layer_data: dict,
    layer_bucket: dict[str, object],
) -> None:
    for req_class in layer_data.get('required_classes', []):
        _compare_one_required_class(
            errors,
            layer_name,
            layer_bucket,
            req_class,
        )


def _compare_required_module_functions(
    errors: list[str],
    layer_name: str,
    layer_data: dict,
    mf_actual: dict[str, list[str]],
) -> None:
    for mf in layer_data.get('required_module_functions', []):
        rel_path_yaml = mf.get('relative_path', '')
        rel_key = normalize_rel_path(str(rel_path_yaml))
        expected_fns_callables = mf.get('functions', [])

        actual_fns_scan = mf_actual.get(rel_key)
        if actual_fns_scan is None:
            msg = (
                f'Layer: {layer_name}\n'
                f' Module file {rel_key!r} was not scanned for functions '
                '(file missing after filtering or path outside '
                'KNOWN_LAYER_NAMES — see infer_layer()).'
            )
            errors.append(msg)
            continue

        for expected_fn in expected_fns_callables:
            if expected_fn not in actual_fns_scan:
                errors.append(
                    f'Layer: {layer_name}\n File {rel_key!r} does not expose '
                    f'expected top-level callable {expected_fn!r}'
                )


def _index_code_endpoints(
    code_eps_list: list,
) -> dict[tuple[str, str, str], dict]:
    code_by_triple: dict[tuple[str, str, str], dict] = {}
    for ep in code_eps_list:
        if not isinstance(ep, dict):
            continue
        code_by_triple[_http_endpoint_triple(ep)] = ep
    return code_by_triple


def _compare_one_spec_http_endpoint(
    errors: list[str],
    layer_name: str,
    code_by_triple: dict[tuple[str, str, str], dict],
    spec_ep: object,
) -> None:
    if not isinstance(spec_ep, dict):
        errors.append(
            f'Layer: {layer_name}\n required_http_endpoints entry must be '
            f'a mapping, got {type(spec_ep).__name__}.'
        )
        return
    trip = _http_endpoint_triple(spec_ep)
    if trip[0] == '' or trip[1] == '' or trip[2] == '':
        errors.append(
            f'Layer: {layer_name}\n HTTP endpoint spec must include '
            f'non-empty method, path, handler: {spec_ep!r}'
        )
        return
    code_ep = code_by_triple.get(trip)
    if code_ep is None:
        errors.append(
            f'Layer: {layer_name}\n No matching HTTP route in code for '
            f'{trip[0]} {trip[1]!r} handler={trip[2]!r}'
        )
        return
    spec_sig = _freeze_http_parameter_rows(spec_ep.get('parameters'))
    code_sig = _freeze_http_parameter_rows(code_ep.get('parameters'))
    if spec_sig != code_sig:
        errors.append(
            f'Layer: {layer_name}\n HTTP route {trip[0]} {trip[1]!r} '
            f'handler={trip[2]!r} parameter contract mismatch:\n'
            f'  spec:  {list(spec_sig)}\n'
            f'  code:  {list(code_sig)}'
        )


def _compare_required_http_endpoints(
    errors: list[str],
    layer_name: str,
    layer_bucket: dict[str, object],
    yaml_eps: object,
) -> None:
    if not isinstance(yaml_eps, list):
        errors.append(
            f'Layer: {layer_name}\n required_http_endpoints must be a list, '
            f'got {type(yaml_eps).__name__}.'
        )
        return

    http_actual_raw = layer_bucket.get(HTTP_ENDPOINTS_BUCKET, [])
    code_eps_list = http_actual_raw if isinstance(http_actual_raw, list) else []
    code_by_triple = _index_code_endpoints(code_eps_list)

    for spec_ep in yaml_eps:
        _compare_one_spec_http_endpoint(
            errors,
            layer_name,
            code_by_triple,
            spec_ep,
        )


def _spec_class_methods_map(layer_data: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for req_class in layer_data.get('required_classes', []) or []:
        if not isinstance(req_class, dict):
            continue
        name = str(req_class.get('name', ''))
        if not name:
            continue
        methods_raw = req_class.get('methods', [])
        methods = (
            {str(m) for m in methods_raw}
            if isinstance(methods_raw, list)
            else set()
        )
        out[name] = methods
    return out


def _spec_module_functions_map(layer_data: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for mf in layer_data.get('required_module_functions', []) or []:
        if not isinstance(mf, dict):
            continue
        rel_key = normalize_rel_path(str(mf.get('relative_path', '')))
        fns_raw = mf.get('functions', [])
        fns = {str(f) for f in fns_raw} if isinstance(fns_raw, list) else set()
        out[rel_key] = fns
    return out


def _spec_http_triples(layer_data: dict) -> set[tuple[str, str, str]]:
    eps_raw = layer_data.get('required_http_endpoints', [])
    if not isinstance(eps_raw, list):
        return set()
    trips: set[tuple[str, str, str]] = set()
    for spec_ep in eps_raw:
        if isinstance(spec_ep, dict):
            trips.add(_http_endpoint_triple(spec_ep))
    return trips


def _code_class_names(layer_bucket: dict[str, object]) -> set[str]:
    return {
        str(k)
        for k in layer_bucket
        if k not in _SENTINEL_CLASS_NAMES
    }


def _code_methods_for_class(
    layer_bucket: dict[str, object],
    class_name: str,
) -> set[str]:
    raw = layer_bucket.get(class_name)
    if not isinstance(raw, list):
        return set()
    return {str(m) for m in raw}


def collect_extras_warnings(
    requirements: dict,
    code_artifacts: dict,
) -> list[str]:
    """Report public code symbols absent from the contract (non-blocking)."""
    warnings: list[str] = []
    layers_req_raw = requirements.get('layers', {})
    layers_req = layers_req_raw if isinstance(layers_req_raw, dict) else {}

    for layer_name in sorted(code_artifacts.keys()):
        layer_bucket = code_artifacts[layer_name]
        layer_req = layers_req.get(layer_name)
        if not isinstance(layer_req, dict):
            layer_req = {}

        spec_classes = _spec_class_methods_map(layer_req)
        code_classes = _code_class_names(layer_bucket)

        if layer_name not in layers_req:
            for class_name in sorted(code_classes):
                warnings.append(
                    f'Layer: {layer_name}\n'
                    f' Class {class_name!r} is present in code but the layer '
                    f'is not listed in the contract.'
                )
            spec_mf: dict[str, set[str]] = {}
            spec_triples: set[tuple[str, str, str]] = set()
        else:
            for class_name in sorted(code_classes - set(spec_classes.keys())):
                warnings.append(
                    f'Layer: {layer_name}\n'
                    f' Class {class_name!r} is present in code but not listed '
                    f'in required_classes.'
                )
            spec_mf = _spec_module_functions_map(layer_req)
            spec_triples = _spec_http_triples(layer_req)

        for class_name in sorted(code_classes & set(spec_classes.keys())):
            extra_methods = _code_methods_for_class(
                layer_bucket,
                class_name,
            ) - spec_classes[class_name]
            for method_name in sorted(extra_methods):
                warnings.append(
                    f'Layer: {layer_name}\n'
                    f' Class {class_name} exposes method {method_name!r} in '
                    f'code but it is not listed in the contract.'
                )

        code_mf = _mf_actual_map(layer_bucket)
        for rel_path in sorted(set(code_mf.keys()) - set(spec_mf.keys())):
            warnings.append(
                f'Layer: {layer_name}\n'
                f' File {rel_path!r} exposes top-level callables in code '
                f'but is not listed in required_module_functions.'
            )
        for rel_path in sorted(set(code_mf.keys()) & set(spec_mf.keys())):
            extra_fns = set(code_mf[rel_path]) - spec_mf[rel_path]
            for fn_name in sorted(extra_fns):
                warnings.append(
                    f'Layer: {layer_name}\n'
                    f' File {rel_path!r} exposes callable {fn_name!r} in code '
                    f'but it is not listed in the contract.'
                )

        http_actual_raw = layer_bucket.get(HTTP_ENDPOINTS_BUCKET, [])
        code_eps_list = (
            http_actual_raw if isinstance(http_actual_raw, list) else []
        )
        for code_ep in code_eps_list:
            if not isinstance(code_ep, dict):
                continue
            trip = _http_endpoint_triple(code_ep)
            if trip[0] == '' or trip[1] == '' or trip[2] == '':
                continue
            if trip not in spec_triples:
                warnings.append(
                    f'Layer: {layer_name}\n'
                    f' HTTP route {trip[0]} {trip[1]!r} handler={trip[2]!r} '
                    f'is present in code but not listed in '
                    f'required_http_endpoints.'
                )

    return warnings


class Comparator:
    """Compare a YAML layered contract with scanned artifacts."""

    def __init__(self, requirements: dict, code_artifacts: dict) -> None:
        """Attach requirements and analyzer output."""
        self.requirements = requirements
        self.code_artifacts = code_artifacts
        self.errors: list[str] = []

    def compare(self, *, report_extras: bool = True) -> CompareResult:
        """Return blocking mismatches and optional code-not-in-spec warnings."""
        layers_req = self.requirements.get('layers', {})
        for layer_name, layer_data in layers_req.items():
            if layer_name not in self.code_artifacts:
                self.errors.append(
                    f"Layer '{layer_name}' not found under scanned sources "
                    '(no .py files under that layer in the bounded context '
                    'after filtering).'
                )
                continue
            layer_bucket = self.code_artifacts[layer_name]
            _compare_required_classes(
                self.errors,
                layer_name,
                layer_data,
                layer_bucket,
            )
            mf_actual = _mf_actual_map(layer_bucket)
            _compare_required_module_functions(
                self.errors,
                layer_name,
                layer_data,
                mf_actual,
            )
            yaml_eps = layer_data.get('required_http_endpoints')
            if yaml_eps is not None:
                _compare_required_http_endpoints(
                    self.errors,
                    layer_name,
                    layer_bucket,
                    yaml_eps,
                )

        warnings: list[str] = []
        if report_extras:
            warnings = collect_extras_warnings(
                self.requirements,
                self.code_artifacts,
            )
        return CompareResult(errors=self.errors, warnings=warnings)
