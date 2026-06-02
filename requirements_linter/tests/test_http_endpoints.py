"""FastAPI route extraction and ``required_http_endpoints`` checks."""

from __future__ import annotations

import ast

from requirements_linter.entrypoints.cli import run_demo_pipeline
from requirements_linter.core.ast_specs import (
    HTTP_ENDPOINTS_BUCKET,
    build_code_artifacts,
)
from requirements_linter.core.comparator import Comparator
from requirements_linter.http.http_routes import (
    join_fastapi_route_path,
    extract_http_endpoints_from_module,
)

_EXPECTED_ROUTES_MINI_API = 2

MINI_API = '''
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Path, Depends

router = APIRouter(prefix="/widgets", tags=[])


def get_uid():
    return {}


@router.get("/")
async def list_widgets():
    return []


@router.get("/{wid}/")
async def get_widget(
    wid: UUID = Path(),
    cx: Optional[str] = None,
    user=Depends(get_uid),
):
    return {}
'''


def test_join_fastapi_route_path() -> None:
    """Check prefix + path joining for sample templates."""
    base = '/virtual-machines'
    assert join_fastapi_route_path(base, '/') == '/virtual-machines/'
    vm = '/{vm_id}/'
    assert join_fastapi_route_path(base, vm) == '/virtual-machines/{vm_id}/'
    assert join_fastapi_route_path('', '/bare/') == '/bare/'


def test_extract_http_endpoints_from_module() -> None:
    """Exercise static parsing of a miniature FastAPI module."""
    tree = ast.parse(MINI_API)
    eps = extract_http_endpoints_from_module(tree, 'entrypoints/api.py')
    by_handler = {e['handler']: e for e in eps}
    assert set(by_handler) == {'list_widgets', 'get_widget'}
    assert by_handler['list_widgets']['method'] == 'GET'
    assert by_handler['list_widgets']['path'] == '/widgets/'
    gw = by_handler['get_widget']
    assert gw['method'] == 'GET'
    assert gw['path'] == '/widgets/{wid}/'
    params_raw = gw.get('parameters')
    assert isinstance(params_raw, list)
    kinds = {
        str(p['name']): str(p['kind'])
        for p in params_raw
        if isinstance(p, dict)
    }
    assert kinds == {'wid': 'path', 'cx': 'query', 'user': 'depends'}


def test_comparator_http_contract_ok() -> None:
    """Comparator accepts code when YAML matches extracted routes."""
    files = {'entrypoints/api.py': MINI_API}
    arts = build_code_artifacts(files)
    spec = {
        'layers': {
            'entrypoints': {
                'required_classes': [],
                'required_http_endpoints': [
                    {
                        'method': 'GET',
                        'path': '/widgets/',
                        'handler': 'list_widgets',
                        'parameters': [],
                    },
                    {
                        'method': 'GET',
                        'path': '/widgets/{wid}/',
                        'handler': 'get_widget',
                        'parameters': [
                            {
                                'name': 'cx',
                                'kind': 'query',
                                'required': False,
                                'type_hint': 'Optional[str]',
                            },
                            {
                                'name': 'user',
                                'kind': 'depends',
                                'required': True,
                                'type_hint': '',
                            },
                            {
                                'name': 'wid',
                                'kind': 'path',
                                'required': True,
                                'type_hint': 'UUID',
                            },
                        ],
                    },
                ],
            },
        },
    }
    assert Comparator(spec, arts).compare().errors == []


def test_comparator_http_contract_param_mismatch() -> None:
    """Mismatching parameter rows surface a single Comparator error."""
    files = {'entrypoints/api.py': MINI_API}
    arts = build_code_artifacts(files)
    spec = {
        'layers': {
            'entrypoints': {
                'required_classes': [],
                'required_http_endpoints': [
                    {
                        'method': 'GET',
                        'path': '/widgets/{wid}/',
                        'handler': 'get_widget',
                        'parameters': [
                            {
                                'name': 'wid',
                                'kind': 'path',
                                'required': True,
                                'type_hint': 'str',
                            },
                        ],
                    },
                ],
            },
        },
    }
    result = Comparator(spec, arts).compare()
    assert len(result.errors) == 1
    assert 'parameter contract mismatch' in result.errors[0]


def test_demo_pipeline_regression() -> None:
    """Synthetic demo YAML and sources remain aligned."""
    assert run_demo_pipeline().errors == []


def test_build_code_artifacts_has_http_bucket() -> None:
    """Entrypoints artifacts include merged HTTP endpoints list."""
    arts = build_code_artifacts({'entrypoints/api.py': MINI_API})
    ep = arts['entrypoints'][HTTP_ENDPOINTS_BUCKET]
    assert isinstance(ep, list)
    assert len(ep) == _EXPECTED_ROUTES_MINI_API
