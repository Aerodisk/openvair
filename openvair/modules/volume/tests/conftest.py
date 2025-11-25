"""Shared fixtures for volume integration tests.

Provides:
- `client`: FastAPI test client.
- `mock_auth_dependency`: Replaces JWT auth with mock user.
- `configure_pagination`: Enables pagination globally in tests.
- `test_storage`: Creates and removes a test storage.
- `test_volume`: Creates and deletes a volume for each test.
- `attached_volume`: Mocks a volume-to-VM attachment in the DB.

Includes:
- `cleanup_all_volumes`: Utility to delete all volumes from DB + filesystem.
"""

from uuid import UUID, uuid4
from typing import Generator

import pytest

from openvair.libs.log import get_logger
from openvair.modules.volume.adapters.orm import VolumeAttachVM
from openvair.modules.volume.service_layer.unit_of_work import (
    VolumeSqlAlchemyUnitOfWork,
)

LOG = get_logger(__name__)


@pytest.fixture(scope='function')
def attached_volume(volume: dict) -> Generator[dict, None, None]:
    """Creates volume-to-VM attachment (directly in DB) and removes it after test."""  # noqa: E501
    volume_id = UUID(volume['id'])
    vm_id = uuid4()

    with VolumeSqlAlchemyUnitOfWork() as uow:
        db_volume = uow.volumes.get_or_fail(volume_id)
        attachment = VolumeAttachVM(vm_id=vm_id, volume_id=volume_id)
        db_volume.attachments.append(attachment)
        uow.session.add(attachment)
        uow.commit()

    yield {
        'volume_id': volume_id,
        'vm_id': vm_id,
    }

    with VolumeSqlAlchemyUnitOfWork() as uow:
        db_volume = uow.volumes.get_or_fail(volume_id)
        db_volume.attachments.clear()
        uow.session.query(VolumeAttachVM).filter_by(
            volume_id=volume_id
        ).delete()
        uow.commit()
