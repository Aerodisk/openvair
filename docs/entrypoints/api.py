from pathlib import Path
from typing import List

from starlette.routing import Mount, BaseRoute
from starlette.staticfiles import StaticFiles

PROJECT_DIR = Path(__file__).parent.parent.parent


def docs_routes() -> List[BaseRoute]:
    """ Provide a list of static routes to add when initializing app

    return:
        list of routes

    """
    docs = Mount(
        path="/docs",
        app=StaticFiles(directory=PROJECT_DIR / 'docs/build', html=True),
        name="docs"
    )
    return [docs]

