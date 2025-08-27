from typing import Dict  # noqa: D100

from fastapi import APIRouter
from pydantic import BaseModel

from openvair.modules.control_plane.service_layer.services import (
    call_vm_on_node,
)

router = APIRouter(prefix='/_dev')


class RpcReq(BaseModel):  # noqa: D101
    module: str  # "vm"
    target_node: str  # "cmp-1"
    action: str  # "create_vm"
    data: dict


@router.post('/rpc')
def dev_rpc(req: RpcReq) -> Dict:  # noqa: D103
    if req.module != 'vm':
        return {'ok': False, 'error': 'only module=vm in dev stub'}
    return call_vm_on_node(req.target_node, req.action, req.data)
