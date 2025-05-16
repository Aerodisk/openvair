"""Helper functions for volume integration tests.

Includes:
- `wait_for_status`: Waits until a volume reaches the expected status.
"""

import time

from fastapi import status
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger

LOG = get_logger(__name__)


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
