"""DTOs for external volume and storage service responses.

Defines strongly typed models representing volumes and storages as returned
by external services. These DTOs are used in service layer validation and logic.
"""

from uuid import UUID
from typing import Any, Dict, List, Literal, Optional
from pathlib import Path

from pydantic import model_validator

from openvair.common.base_pydantic_models import BaseDTOModel


class VolumeModelDTO(BaseDTOModel):
    """Schema representing a volume.

    Attributes:
        id (UUID): The ID of the volume.
        name (str): The name of the volume.
        description (Optional[str]): A description of the volume.
        storage_id (Optional[UUID]): The ID of the storage the volume belongs
            to.
        user_id (Optional[UUID]): The ID of the user who owns the volume.
        format (str): The format of the volume (e.g., qcow2, raw).
        size (int): The size of the volume in bytes.
        used (Optional[int]): The amount of space used in the volume.
        status (Optional[str]): The status of the volume.
        information (Optional[str]): Additional information about the volume.
        attachments (List[Optional[Attachment]]): A list of attachments for the
            volume.
        read_only (Optional[bool]): Whether the volume is read-only.
    """

    class VolumeAttachment(BaseDTOModel):
        """Schema representing a volume attachment to a virtual machine.

        This model defines the association between a volume and a virtual
        machine, including the target device path inside the VM.

        Attributes:
            vm_id (UUID): The unique identifier of the virtual machine to which
             the volume is attached.
            target (Path): The target path or device name inside the virtual
                machine where the volume is attached.
        """

        vm_id: UUID
        target: Optional[Path]

    id: UUID
    name: str
    description: Optional[str] = None
    storage_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    format: Literal['qcow2', 'raw']
    size: int
    used: Optional[int] = None
    status: Optional[str] = None
    information: Optional[str] = None
    read_only: Optional[bool] = False
    path: Path
    template_id: Optional[UUID]
    attachments: List[VolumeAttachment]


class StorageModelDTO(BaseDTOModel):
    """Schema representing a storage entity.

    Attributes:
        id (UUID): The unique identifier of the storage.
        name (str): The name of the storage.
        description (Optional[str]): A brief description of the storage.
        storage_type (str): The type of storage (e.g., 'nfs', 'localfs').
        status (str): The current status of the storage.
        size (int): The total size of the storage in bytes.
        available (int): The available size of the storage in bytes.
        user_id (Optional[UUID]): The ID of the user who owns the storage.
        information (Optional[str]): Additional information about the storage.
    """

    id: UUID
    name: str
    description: Optional[str] = None
    storage_type: str
    status: str
    size: int
    available: int
    user_id: Optional[UUID] = None
    information: Optional[str] = None
    mount_point: Path

    @model_validator(mode='before')
    @classmethod
    def extract_mount_point(cls, values: Dict[str, Any]) -> Dict[str, Any]:  # noqa: C901
        """Pre-validation:

        Extracts the 'mount_point' from the 'storage_extra_specs'
        field if present and sets it as the 'mount_point' field.

        Args:
            values (Dict[str, Any]): The input data dictionary.

        Returns:
            Dict[str, Any]: The modified data dictionary with 'mount_point' set.
        """
        specs = values.get('storage_extra_specs')
        if specs:
            mount = None
            if isinstance(specs, dict):
                mount = specs.get('mount_point')
            elif isinstance(specs, list):
                for spec in specs:
                    if isinstance(spec, dict) and spec.get('mount_point'):
                        mount = spec.get('mount_point')
                        break
            if mount is not None:
                values['mount_point'] = (
                    mount if isinstance(mount, Path) else Path(mount)
                )
        return values


class VMModelDTO(BaseDTOModel):
    """Schema representing a virtual machine entity.

    This model is used to validate and represent virtual machine data received
    from external services.

    Attributes:
        id (str): The unique identifier of the virtual machine.
        name (str): The name of the virtual machine.
        power_state (str): The current power state (e.g., 'running', 'stopped').
        status (str): The general status of the virtual machine.
    """

    id: str
    name: str
    power_state: str
    status: str
