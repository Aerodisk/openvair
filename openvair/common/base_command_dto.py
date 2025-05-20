from typing import Dict, Generic, TypeVar  # noqa: D100

from pydantic import BaseModel

Manager = TypeVar('Manager', bound=BaseModel)
Method = TypeVar('Method', bound=BaseModel)


class BaseCommandDTO(BaseModel, Generic[Manager, Method]):
    """Base class for CommandDTOs with manager/method separation."""

    manager: Manager
    method: Method

    def for_manager_dict(self) -> Dict:
        """Return manager data as dict (for RPC constructor)."""
        return self.manager.model_dump(mode='json')

    def for_method_dict(self) -> Dict:
        """Return method data as dict (for RPC method call)."""
        return self.method.model_dump(mode='json')
