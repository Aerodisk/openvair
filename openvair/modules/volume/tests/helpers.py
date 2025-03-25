  # noqa: D100
import time
import uuid

from fastapi import status
from fastapi.testclient import TestClient


def generate_volume_name(prefix: str = 'test-volume') -> str:
    """Генерирует уникальное имя тома с указанным префиксом."""  # noqa: RUF002
    return f'{prefix}-{uuid.uuid4().hex[:6]}'


def wait_for_status(
    client: TestClient,
    volume_id: str,
    expected_status: str,
    timeout: int = 30,
    interval: float = 0.5,
) -> None:
    """Ожидает, пока статус тома не станет равным expected_status.

    Если за timeout секунд статус не изменится, выбрасывается TimeoutError.
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
