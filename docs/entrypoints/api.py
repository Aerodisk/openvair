"""Entrypoint for serving documentation routes.

This module defines a function to generate routes for serving static
documentation files using Starlette. It is typically used during app
initialization to include the `/docs` endpoint.

Attributes:
    PROJECT_DIR (Path): Root directory of the project.
"""

from typing import List
from pathlib import Path

from starlette.routing import Mount, BaseRoute
from starlette.staticfiles import StaticFiles

PROJECT_DIR = Path(__file__).parent.parent.parent


def docs_routes() -> List[BaseRoute]:
    """Provide a list of routes for serving documentation.

    Returns:
        List[BaseRoute]: A list containing a single route for the `/docs`
            endpoint, which serves static files from the project's documentation
            build directory.
    """
    docs = Mount(
        path='/docs',
        app=StaticFiles(directory=PROJECT_DIR / 'docs/build', html=True),
        name='docs',
    )
    return [docs]
