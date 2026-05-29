"""Static FastAPI route extraction for the ``entrypoints`` layer."""

from __future__ import annotations

import ast

from requirements_linter.naming import is_contract_public_name

_HTTP_VERBS = frozenset({
    'get',
    'post',
    'put',
    'patch',
    'delete',
    'head',
    'options',
})


def join_fastapi_route_path(prefix: str | None, route_path: str) -> str:
    """Join ``APIRouter(prefix=...)`` with a literal route path.

    MVP: string literals only. Non-empty prefix strips slashes and prepends;
    otherwise the route path is returned (leading ``/`` kept). Trailing
    ``/`` on the decorator path is preserved (e.g. ``'/create/'``).

    Unsupported: ``include_router``, dynamic paths, non-literal prefix, or
    decorator wrappers besides ``<router>.<method>(path, ...)``.
    """
    seg = route_path if route_path.startswith('/') else f'/{route_path}'
    if not prefix or not prefix.strip('/'):
        return seg if seg else '/'
    base = '/' + prefix.strip('/')
    return base.rstrip('/') + seg


def _is_api_router_call(call: ast.Call) -> bool:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id == 'APIRouter'
    if isinstance(func, ast.Attribute):
        return func.attr == 'APIRouter'
    return False


def _prefix_constant_from_keywords(keywords: list[ast.keyword]) -> str | None:
    for kw in keywords:
        if kw.arg != 'prefix':
            continue
        if not isinstance(kw.value, ast.Constant):
            continue
        val = kw.value.value
        return val if isinstance(val, str) else None
    return None


def _api_router_prefix_from_call(call: ast.Call) -> str | None:
    return _prefix_constant_from_keywords(call.keywords)


def _try_register_router_assignment(
    node: ast.Assign,
    out: dict[str, str],
) -> None:
    val = node.value
    if not isinstance(val, ast.Call) or not _is_api_router_call(val):
        return
    prefix = _api_router_prefix_from_call(val)
    if prefix is None:
        return
    for t in node.targets:
        if isinstance(t, ast.Name):
            out[t.id] = prefix


def _collect_router_vars(module: ast.Module) -> dict[str, str]:
    out: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.Assign):
            _try_register_router_assignment(node, out)
    return out


def _call_name_like(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _is_fastapi_injection_call(call: ast.Call, name: str) -> bool:
    return _call_name_like(call) == name


def _default_classifies(default: ast.expr | None) -> str | None:
    if default is None or not isinstance(default, ast.Call):
        return None
    cn = _call_name_like(default)
    mapping = {
        'Path': 'path',
        'Query': 'query',
        'Depends': 'depends',
        'Body': 'body',
        'File': 'body',
        'Form': 'body',
    }
    return mapping.get(cn) if cn else None


def _annotation_str(ann: ast.expr | None) -> str:
    if ann is None:
        return ''
    return ast.unparse(ann)


def _is_optional_annotation(ann: ast.expr | None) -> bool:
    if ann is None:
        return False
    if isinstance(ann, ast.Subscript):
        if isinstance(ann.value, ast.Name) and ann.value.id == 'Optional':
            return True
        v_attr = ann.value
        if isinstance(v_attr, ast.Attribute) and v_attr.attr == 'Optional':
            return True
    return bool(
        isinstance(ann, ast.BinOp)
        and isinstance(ann.op, ast.BitOr)
    )


def _schema_recursive(ann: ast.expr) -> bool:
    if isinstance(ann, ast.Subscript):
        return _looks_like_schema_body_annotation(ann.slice)
    if isinstance(ann, ast.Attribute):
        parent = ann.value
        if isinstance(parent, ast.Name) and parent.id == 'schemas':
            return True
        return _looks_like_schema_body_annotation(parent)
    return False


def _looks_like_schema_body_annotation(ann: ast.expr | None) -> bool:
    if ann is None:
        return False
    if isinstance(ann, ast.Name) and ann.id in {'Dict', 'dict', 'List', 'list'}:
        return False
    if isinstance(ann, (ast.Subscript, ast.Attribute)):
        return _schema_recursive(ann)
    return False


def _infer_param_kind(arg: ast.arg, default: ast.expr | None) -> str:
    explicit = _default_classifies(default)
    if explicit:
        return explicit
    ann = arg.annotation
    if _looks_like_schema_body_annotation(ann):
        return 'body'
    is_dict_ann = _annotation_str(ann) in {'Dict', 'dict'}
    is_dep = (
        isinstance(default, ast.Call)
        and _is_fastapi_injection_call(default, 'Depends')
    )
    if is_dict_ann and default is not None and is_dep:
        return 'depends'
    return 'query'


def _query_call_required(call: ast.Call) -> bool:
    for kw in call.keywords:
        if kw.arg == 'default':
            val = kw.value
            return bool(
                isinstance(val, ast.Constant)
                and val.value is Ellipsis
            )
    if call.args:
        val0 = call.args[0]
        if isinstance(val0, ast.Constant):
            return val0.value is Ellipsis
        return False
    return True


def _required_from_default(default: ast.expr) -> bool:
    if isinstance(default, ast.Call):
        fname = _call_name_like(default)
        if fname == 'Query':
            return _query_call_required(default)
        return True
    return True


def _param_required(
    kind: str,
    default: ast.expr | None,
    ann: ast.expr | None,
) -> bool:
    if kind in ('depends', 'path'):
        return True
    if default is None:
        return not _is_optional_annotation(ann)
    if isinstance(default, ast.Constant) and default.value is None:
        return False
    return _required_from_default(default)


def _literal_route_path_arg(dec: ast.Call) -> str | None:
    if not dec.args:
        return None
    path_arg = dec.args[0]
    if not isinstance(path_arg, ast.Constant):
        return None
    return path_arg.value if isinstance(path_arg.value, str) else None


def _router_route_parts(dec: ast.Call) -> tuple[str, str, str] | None:
    func = dec.func
    if not isinstance(func, ast.Attribute):
        return None
    if func.attr not in _HTTP_VERBS:
        return None
    if not isinstance(func.value, ast.Name):
        return None
    router_var = func.value.id
    path_lit = _literal_route_path_arg(dec)
    if path_lit is None:
        return None
    return func.attr.upper(), router_var, path_lit


def _extract_route_from_decorator(
    dec: ast.expr,
    router_prefixes: dict[str, str],
) -> tuple[str, str] | None:
    if not isinstance(dec, ast.Call):
        return None
    parts = _router_route_parts(dec)
    if parts is None:
        return None
    verb, router_var, path_lit = parts
    prefix = router_prefixes.get(router_var, '')
    full_path = join_fastapi_route_path(prefix or None, path_lit)
    return verb, full_path


def _append_positional_params(
    func: ast.AsyncFunctionDef | ast.FunctionDef,
    params: list[dict[str, object]],
) -> None:
    args = func.args
    all_args: list[ast.arg] = list(args.posonlyargs) + list(args.args)
    num_no_default = len(all_args) - len(args.defaults)
    filler = [None] * num_no_default
    defaults: list[ast.expr | None] = filler + list(args.defaults)

    for arg, default in zip(all_args, defaults):
        if not is_contract_public_name(arg.arg):
            continue
        kind = _infer_param_kind(arg, default)
        params.append(
            {
                'name': arg.arg,
                'kind': kind,
                'required': _param_required(kind, default, arg.annotation),
                'type_hint': _annotation_str(arg.annotation),
            }
        )


def _append_kwonly_params(
    func: ast.AsyncFunctionDef | ast.FunctionDef,
    params: list[dict[str, object]],
) -> None:
    args = func.args
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        if not is_contract_public_name(arg.arg):
            continue
        kind = _infer_param_kind(arg, default)
        params.append(
            {
                'name': arg.arg,
                'kind': kind,
                'required': _param_required(kind, default, arg.annotation),
                'type_hint': _annotation_str(arg.annotation),
            }
        )


def _handler_parameters(
    func: ast.AsyncFunctionDef | ast.FunctionDef,
) -> list[dict[str, object]]:
    params: list[dict[str, object]] = []
    _append_positional_params(func, params)
    _append_kwonly_params(func, params)
    return params


def _first_route_decorator(
    func: ast.AsyncFunctionDef | ast.FunctionDef,
    router_prefixes: dict[str, str],
) -> tuple[str, str] | None:
    for dec in func.decorator_list:
        parsed = _extract_route_from_decorator(dec, router_prefixes)
        if parsed is not None:
            return parsed
    return None


def extract_http_endpoints_from_module(
    module: ast.Module,
    source_file: str,
) -> list[dict[str, object]]:
    """Describe FastAPI routes using static string literals only.

    Returns dicts with method, path, handler, parameters, source_file.
    """
    router_prefixes = _collect_router_vars(module)
    out: list[dict[str, object]] = []

    for node in module.body:
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        if not is_contract_public_name(node.name):
            continue
        route_info = _first_route_decorator(node, router_prefixes)
        if route_info is None:
            continue
        method, path = route_info
        out.append(
            {
                'method': method,
                'path': path,
                'handler': node.name,
                'parameters': _handler_parameters(node),
                'source_file': source_file,
            }
        )
    return out
