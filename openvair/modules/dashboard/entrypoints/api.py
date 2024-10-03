"""API endpoint for retrieving node resource data.

This module defines a FastAPI router for the '/dashboard' endpoint, which
provides a single GET endpoint to retrieve node resource data.

The `get_node_data` function is the handler for the GET '/dashboard' endpoint.
It takes a `DashboardCrud` object as a dependency and returns a `NodeInfo`
object containing the node resource data.

The `DashboardCrud` object is responsible for fetching the node resource data
from the `PrometheusRepository` class, which is defined in another module.

The `get_node_data` function is protected by a dependency on the
`get_current_user` function, which ensures that only authenticated users can
access the endpoint.

Functions:
    get_node_data: Retrieves node resource data and returns it as a `NodeInfo`
        object.
"""

from fastapi import Depends, APIRouter, status

from openvair.libs.log import get_logger
from openvair.modules.tools.utils import get_current_user
from openvair.modules.dashboard.entrypoints.crud import DashboardCrud
from openvair.modules.dashboard.entrypoints.schemas import NodeInfo

LOG = get_logger(__name__)

router = APIRouter(
    prefix='/dashboard',
    tags=['dashboard'],
    responses={404: {'description': 'Not found!'}},
)


@router.get(
    '/',
    response_model=NodeInfo,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_user),
    ],
)
def get_node_data(crud: DashboardCrud = Depends(DashboardCrud)) -> NodeInfo:
    """Retrieve node resource data.

    This function takes a `DashboardCrud` object as a dependency and returns a
    `NodeInfo` object containing the node resource data. The `DashboardCrud`
    object is responsible for fetching the data from the `PrometheusRepository`
    class.

    Args:
        crud (DashboardCrud): The `DashboardCrud` object used to fetch the node
            resource data.

    Returns:
        NodeInfo: A pydantic model containing the node resource data.
    """
    LOG.info('Api start getting dashboard info.')
    node_data = crud.get_data()
    LOG.info('Api request was successfully processed.')
    return node_data
