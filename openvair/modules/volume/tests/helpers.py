"""Helper functions for volume integration tests.

Includes:
- `generate_volume_name`: Generates a unique name for testing.
- `wait_for_status`: Waits until a volume reaches the expected status.
"""

import time
import uuid

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.modules.volume.domain.model import VolumeFactory
from openvair.modules.volume.adapters.serializer import DataSerializer
from openvair.modules.volume.service_layer.unit_of_work import (
    SqlAlchemyUnitOfWork,
)

LOG = get_logger(__name__)


def generate_volume_name(prefix: str = 'test-volume') -> str:
    """Generates a unique volume name using UUID suffix."""
    return f'{prefix}-{uuid.uuid4().hex[:6]}'


def wait_for_status(
    client: TestClient,
    volume_id: str,
    expected_status: str,
    timeout: int = 30,
    interval: float = 0.5,
) -> None:
    """Waits until a volume reaches a specific status via polling.

    Raises:
        TimeoutError: If expected status is not reached within timeout.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = client.get(f'/volumes/{volume_id}/')
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            if data.get('status') == expected_status:
                return
        time.sleep(interval)
    message = (
        f"Volume {volume_id} did not reach status '{expected_status}'"
        f'within {timeout} seconds.'
    )
    raise TimeoutError(message)


def cleanup_all_volumes() -> None:
    """Removes all volumes from DB and filesystem (used after storage tests)."""
    unit_of_work = SqlAlchemyUnitOfWork()
    try:
        with unit_of_work as uow:
            s = uow.volumes.get_all()
            for volume_data in s:
                volume_instance = VolumeFactory().get_volume(
                    DataSerializer.to_domain(volume_data)
                )
                uow.volumes.delete(volume_data.id)
                volume_instance.delete()
                uow.commit()
    except Exception as err:  # noqa: BLE001
        LOG.warning(f'Error while cleaning up volumes: {err}')
