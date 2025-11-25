"""Main entry point for the OpenVair application.

This module sets up the FastAPI application, including routing, middleware,
and exception handling. It also configures the CORS settings and initializes
the web server with Uvicorn.

Routes:
    Includes routers for various modules such as user, image, volume, network,
    and more.

Middleware:
    Adds logging middleware to log each incoming request.

Exception Handlers:
    Defines custom exception handlers for handling RPC call errors,
    initialization errors, and validation errors.

Functions:
    log_middleware: Middleware to log HTTP requests.
    root: The root endpoint that serves the index.html template.
    rpc_call_exception_handler: Handles RpcCallException.
    rpc_call_timeout_exception_handler: Handles RpcCallTimeoutException.
    rpc_init_exception_handler: Handles RpcClientInitializedException.
    validate_exception_handler: Handles TypeError, ValueError, and
        AssertionError.
"""

from typing import Callable, Awaitable
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi_pagination import add_pagination
from fastapi.staticfiles import StaticFiles

from openvair.libs.log import get_logger
from openvair.libs.client.config import get_routes
from openvair.libs.messaging.exceptions import (
    RpcCallException,
    RpcCallTimeoutException,
    RpcClientInitializedException,
)

LOG = get_logger(__name__)

app = FastAPI(
    routes=get_routes(),
    docs_url='/swagger',
    redoc_url=None,
)
add_pagination(app)

from fastapi.middleware.cors import CORSMiddleware

# Configure CORS settings to allow specified origins
origins = [
    'https://localhost',
    'https://localhost:8080',
    'https://localhost:8081',
    'https://localhost:8082',
    'https://0.0.0.0:8000',
    'https://0.0.0.0:8000/dashboard/',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

from openvair.modules.user.entrypoints.api import router as user
from openvair.modules.image.entrypoints.api import router as image
from openvair.modules.user.entrypoints.auth import router as auth
from openvair.modules.backup.entrypoints.api import router as backup_router
from openvair.modules.volume.entrypoints.api import router as volume
from openvair.modules.network.entrypoints.api import router as network
from openvair.modules.storage.entrypoints.api import router as storage
from openvair.modules.template.entrypoints.api import router as tempalte_router
from openvair.modules.dashboard.entrypoints.api import router as dashboard
from openvair.modules.event_store.entrypoints.api import router as event_store
from openvair.modules.block_device.entrypoints.api import router as block_router
from openvair.modules.notification.entrypoints.api import (
    router as notification_router,
)
from openvair.modules.virtual_network.entrypoints.api import router as vn_router
from openvair.modules.virtual_machines.entrypoints.api import (
    router as vm_router,
)

# Include routers for different modules
app.include_router(network)
app.include_router(dashboard)
app.include_router(storage)
app.include_router(user)
app.include_router(auth)
app.include_router(volume)
app.include_router(image)
app.include_router(vm_router)
app.include_router(event_store)
app.include_router(notification_router)
app.include_router(block_router)
app.include_router(vn_router)
app.include_router(backup_router)
app.include_router(tempalte_router)

project_dir = Path(__file__).parent
templates = Jinja2Templates(directory=project_dir / 'dist')
app.mount('/assets', StaticFiles(directory=project_dir / 'dist/assets'))
app.mount(
    '/docs',
    StaticFiles(directory=project_dir.parent / 'docs', html=True),
    name='mkdocs_docs',
)


@app.middleware('http')
async def log_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Middleware to log each HTTP request.

    Logs the URL and method of each incoming request.

    Args:
        request (Request): The incoming HTTP request.
        call_next (function): The next middleware or route handler.

    Returns:
        Response: The response returned by the next handler.
    """
    log_dict = {'url': request.url.path, 'method': request.method}
    LOG.info(log_dict, extra=log_dict)
    return await call_next(request)


@app.get('/')
def root(request: Request) -> Response:
    """Serve the root endpoint.

    Returns the index.html template.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        TemplateResponse: The rendered index.html template.
    """
    return templates.TemplateResponse(
        'index.html', {'request': request, 'success': True}
    )


@app.exception_handler(RpcCallException)
async def rpc_call_exception_handler(
    _request: Request,
    exc: RpcCallException,
) -> JSONResponse:
    """Handle RpcCallException.

    Logs the exception and returns a JSON response with error details.

    Args:
        request (Request): The incoming HTTP request.
        exc (RpcCallException): The exception that was raised.

    Returns:
        JSONResponse: The response containing error details.
    """
    LOG.error('handle error: %s.' % str(exc))
    return JSONResponse(
        status_code=500,
        content={
            'timestamp': str(datetime.now()),
            'error': type(exc).__name__,
            'message': str(exc),
        },
    )


@app.exception_handler(RpcCallTimeoutException)
async def rpc_call_timeout_exception_handler(
    _request: Request,
    exc: RpcCallTimeoutException,
) -> JSONResponse:
    """Handle RpcCallTimeoutException.

    Logs the exception and returns a JSON response with error details.

    Args:
        request (Request): The incoming HTTP request.
        exc (RpcCallTimeoutException): The exception that was raised.

    Returns:
        JSONResponse: The response containing error details.
    """
    LOG.error('handle error: %s.' % str(exc))
    return JSONResponse(
        status_code=500,
        content={
            'timestamp': str(datetime.now()),
            'error': type(exc).__name__,
            'message': str(exc),
        },
    )


@app.exception_handler(RpcClientInitializedException)
async def rpc_init_exception_handler(
    _request: Request,
    exc: RpcClientInitializedException,
) -> JSONResponse:
    """Handle RpcClientInitializedException.

    Logs the exception and returns a JSON response with error details.

    Args:
        request (Request): The incoming HTTP request.
        exc (RpcClientInitializedException): The exception that was raised.

    Returns:
        JSONResponse: The response containing error details.
    """
    LOG.error('handle error: %s.' % str(exc))
    return JSONResponse(
        status_code=500,
        content={
            'timestamp': str(datetime.now()),
            'error': type(exc).__name__,
            'message': str(exc),
        },
    )


@app.exception_handler(TypeError)
async def type_error_exception_handler(
    _request: Request,
    exc: TypeError,
) -> JSONResponse:
    """Handle TypeError.

    Logs the exception and returns a JSON response with error details.

    Args:
        request (Request): The incoming HTTP request.
        exc (TypeError): The exception that was raised.

    Returns:
        JSONResponse: The response containing error details.
    """
    LOG.error('Validate request error: %s.' % str(exc))
    return JSONResponse(
        status_code=409,
        content={
            'timestamp': str(datetime.now()),
            'error': type(exc).__name__,
            'message': str(exc),
        },
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(
    _request: Request,
    exc: ValueError,
) -> JSONResponse:
    """Handle ValueError.

    Logs the exception and returns a JSON response with error details.

    Args:
        request (Request): The incoming HTTP request.
        exc (ValueError): The exception that was raised.

    Returns:
        JSONResponse: The response containing error details.
    """
    LOG.error('Validate request error: %s.' % str(exc))
    return JSONResponse(
        status_code=409,
        content={
            'timestamp': str(datetime.now()),
            'error': type(exc).__name__,
            'message': str(exc),
        },
    )


@app.exception_handler(AssertionError)
async def assertion_error_exception_handler(
    _request: Request,
    exc: AssertionError,
) -> JSONResponse:
    """Handle AssertionError.

    Logs the exception and returns a JSON response with error details.

    Args:
        request (Request): The incoming HTTP request.
        exc (AssertionError): The exception that was raised.

    Returns:
        JSONResponse: The response containing error details.
    """
    LOG.error('Validate request error: %s.' % str(exc))
    return JSONResponse(
        status_code=409,
        content={
            'timestamp': str(datetime.now()),
            'error': type(exc).__name__,
            'message': str(exc),
        },
    )


if __name__ == '__main__':
    import uvicorn

    from openvair import config

    HOST = config.data['web_app'].get('host')
    PORT = config.data['web_app'].get('port')

    uvicorn.run(
        'main:app',
        host=HOST,
        port=PORT,
        workers=4,
        backlog=65535,
        limit_concurrency=1000,
        limit_max_requests=10000,
        ssl_keyfile='/opt/aero/openvair/key.pem',
        ssl_certfile='/opt/aero/openvair/cert.pem',
    )
