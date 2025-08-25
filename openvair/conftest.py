# noqa: D100
from uuid import uuid4
from typing import Dict, Optional, Generator, cast
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from openvair.main import app
from openvair.libs.log import get_logger
from openvair.libs.testing.utils import (
    create_resource,
    delete_resource,
    wait_full_deleting,
    cleanup_all_volumes,
    cleanup_test_bridges,
    wait_for_field_value,
    cleanup_all_templates,
    cleanup_all_notifications,
    generate_test_entity_name,
)
from openvair.libs.auth.jwt_utils import oauth2schema, get_current_user
from openvair.libs.testing.config import (
    network_settings,
    storage_settings,
    notification_settings,
)
from openvair.modules.volume.entrypoints.schemas import CreateVolume
from openvair.modules.storage.entrypoints.schemas import (
    CreateStorage,
    LocalFSStorageExtraSpecsCreate,
)
from openvair.modules.virtual_machines.entrypoints.schemas import (
    QOS,
    RAM,
    Os,
    Cpu,
    AttachVolume,
    CreateVmDisks,
    VirtualInterface,
    CreateVirtualMachine,
    GraphicInterfaceBase,
)
from openvair.modules.template.entrypoints.schemas.requests import (
    RequestCreateTemplate,
)

LOG = get_logger(__name__)


@pytest.fixture(scope='session')
def client() -> Generator[TestClient, None, None]:
    """Creates FastAPI TestClient with app instance for API testing."""
    with TestClient(app=app) as client:
        LOG.info('CLIENT WAS STARTS')
        yield client
        LOG.info('CLIENT WAS CLOSED')


@pytest.fixture
def unauthorized_client() -> Generator[TestClient, None, None]:
    """TestClient without auth overrides (temporarily)."""
    from openvair.main import app

    # Сохраняем текущие overrides
    original_overrides = app.dependency_overrides.copy()

    # Удаляем mock авторизацию
    app.dependency_overrides = {}

    client = TestClient(app)
    yield client

    # Восстанавливаем mock авторизацию
    app.dependency_overrides = original_overrides


@pytest.fixture(autouse=True, scope='session')
def mock_auth_dependency() -> None:
    """Overrides real JWT authentication with a mocked test user."""
    LOG.info('Mocking authentication dependencies')
    app.dependency_overrides[oauth2schema] = lambda: 'mocked_token'
    app.dependency_overrides[get_current_user] = lambda token='mocked_token': {
        'id': str(uuid4()),
        'username': 'test_user',
        'role': 'admin',
        'token': token,
    }


@pytest.fixture(scope='session', autouse=True)
def configure_pagination() -> None:
    """Registers pagination support in the test app (FastAPI-pagination)."""
    add_pagination(app)


# def delete_storage_from_fs() -> None:
#     devices = get_block_devices_info()
#     for device in devices:
#         mount_point = device.get('mountpoint') or ''
#         if '/opt/aero/openvair/data/mnt' in mount_point:
#             try:
#                 execute(
#                     'umount',
#                     mount_point,
#                     params=ExecuteParams(
#                         shell=True, run_as_root=True, raise_on_error=True
#                     ),
#                 )
#                 execute(
#                     'rm',
#                     '-rf',
#                     mount_point,
#                     params=ExecuteParams(
#                         shell=True,
#                         run_as_root=True,
#                         raise_on_error=True,
#                     ),
#                 )
#             except (ExecuteError, OSError) as e:
#                 LOG.error(f'Error during unmounting storage - {e}')
#                 raise


# @pytest.fixture(autouse=True, scope='session')
# def delete_storages_from_db() -> None:
#     unit_of_work = SqlAlchemyUnitOfWork()
#     with unit_of_work as uow:
#         orm_storages = uow.storages.get_all()
#         for orm_storage in orm_storages:
#             uow.storages.delete(orm_storage.id)
#             uow.commit()
#


@pytest.fixture(scope='module')
def storage(client: TestClient) -> Generator[Dict, None, None]:
    """Creates a test storage and deletes it after session ends."""
    headers = {'Authorization': 'Bearer mocked_token'}

    storage_disk = Path(storage_settings.storage_path)

    storage_data = CreateStorage(
        name=generate_test_entity_name('storage'),
        description='Test storage for integration tests',
        storage_type='localfs',
        specs=LocalFSStorageExtraSpecsCreate(path=storage_disk, fs_type='ext4'),
    )
    response = client.post(
        '/storages/create/',
        json=storage_data.model_dump(mode='json'),
        headers=headers,
    )
    if response.status_code != status.HTTP_201_CREATED:
        message = (
            f'Failed to create storage: {response.status_code}, {response.text}'
        )
        raise RuntimeError(message)

    storage = response.json()
    yield storage
    cleanup_all_volumes()
    cleanup_all_templates()

    delete_response = client.delete(f"/storages/{storage['id']}/delete")
    if delete_response.status_code != status.HTTP_202_ACCEPTED:
        LOG.warning(
            (
                f'Failed to delete test storage: {delete_response.status_code},'
                f' {delete_response.text}'
            )
        )
    LOG.info('FINISH DELETE STORAGE')


@pytest.fixture(scope='function')
def volume(client: TestClient, storage: Dict) -> Generator[Dict, None, None]:
    """Creates a test volume and deletes it after each test."""
    volume_data = CreateVolume(
        name=generate_test_entity_name('volume'),
        description='Volume for integration tests',
        storage_id=storage['id'],
        format='qcow2',
        size=1024,
        read_only=False,
    ).model_dump(mode='json')
    volume = create_resource(client, '/volumes/create/', volume_data, 'volume')

    yield volume

    delete_resource(client, '/volumes', volume['id'], 'volume')


@pytest.fixture(scope='function')
def template(
    client: TestClient, storage: Dict, volume: Dict
) -> Generator[Dict, None, None]:
    """Creates a test volume and deletes it after each test."""
    template_data = RequestCreateTemplate(
        base_volume_id=volume['id'],
        name=generate_test_entity_name(entity_type='template'),
        description='Template for integration tests',
        storage_id=storage['id'],
        is_backing=False,
    ).model_dump(mode='json')
    template = create_resource(
        client, '/templates/', template_data, 'template'
    )['data']

    yield template

    delete_resource(client, '/templates', template['id'], 'volume')


@pytest.fixture(scope='function')
def virtual_machine(
    client: TestClient,
    volume: Dict,
) -> Generator[Dict, None, None]:
    """Creates a test virtual machine and deletes it after each test."""
    vm_data = CreateVirtualMachine(
        name=generate_test_entity_name('virtual_machine'),
        description='Virtual machine for integration tests',
        cpu=Cpu(cores=1, threads=1, sockets=1, model='host', type='static'),
        ram=RAM(size=1000000000),
        os=Os(boot_device='hd', bios='LEGACY', graphic_driver='virtio'),
        graphic_interface=GraphicInterfaceBase(connect_type='vnc'),
        disks=CreateVmDisks(
            attach_disks=[
                AttachVolume(
                    volume_id=volume['id'],
                    qos=QOS(
                        iops_read=500,
                        iops_write=500,
                        mb_read=150,
                        mb_write=100,
                    ),
                    boot_order=1,
                    order=1,
                )
            ]
        ),
        virtual_interfaces=[
            VirtualInterface(
                mode='bridge',
                model='virtio',
                mac='6C:4A:74:EC:CC:D9',
                interface='virbr0',
                order=0,
            )
        ],
    ).model_dump(mode='json')
    vm = create_resource(client, '/virtual-machines/create/', vm_data, 'vm')
    wait_for_field_value(
        client, f'/virtual-machines/{vm["id"]}/', 'status', 'available'
    )
    created_vm = client.get(f'/virtual-machines/{vm["id"]}/').json()

    yield created_vm

    delete_resource(client, '/virtual-machines', created_vm['id'], 'vm')
    wait_full_deleting(client, '/virtual-machines/', created_vm['id'])


@pytest.fixture(scope='function')
def deactivated_virtual_machine(
    client: TestClient, virtual_machine: Dict
) -> Generator[Dict, None, None]:
    """Creates a test deactivated virtual machine."""
    if virtual_machine['power_state'] != 'shut_off':
        response = client.post(
            f'/virtual-machines/{virtual_machine["id"]}/shut-off/'
        ).json()
        wait_for_field_value(
            client,
            f'/virtual-machines/{response["id"]}/',
            'power_state',
            'shut_off',
        )

    deactivated_vm = client.get(
        f'/virtual-machines/{virtual_machine["id"]}/'
    ).json()

    yield deactivated_vm


@pytest.fixture(scope='function')
def activated_virtual_machine(
    client: TestClient, virtual_machine: Dict
) -> Generator[Dict, None, None]:
    """Creates a test activated virtual machine."""
    response = client.post(
        f'/virtual-machines/{virtual_machine["id"]}/start/'
    ).json()
    wait_for_field_value(
        client,
        f'/virtual-machines/{response["id"]}/',
        'power_state',
        'running',
    )

    activated = client.get(f'/virtual-machines/{virtual_machine["id"]}/').json()

    yield activated

    response = client.post(
        f'/virtual-machines/{virtual_machine["id"]}/shut-off/'
    ).json()
    wait_for_field_value(
        client,
        f'/virtual-machines/{response["id"]}/',
        'power_state',
        'shut_off',
    )


@pytest.fixture
def notification() -> Generator[Dict, None, None]:
    """Generates test notification data and cleans up after test."""
    test_data = {
        'msg_type': notification_settings.notification_type,
        'recipients': notification_settings.target_emails,
        'subject': '[TEST - Open vAIR]',
        'message': 'This is a test message from Open vAIR',
    }

    yield test_data

    cleanup_all_notifications()


@pytest.fixture
def physical_interface(client: TestClient) -> Optional[Dict]:
    """Get physical interface by name from environment variable."""
    response = client.get('/interfaces/')
    interfaces_data = response.json()
    interfaces = interfaces_data.get('items', [])

    for interface in interfaces:
        if interface['name'] == network_settings.network_interface:
            return cast(Dict, interface)

    return None


@pytest.fixture
def non_default_interface(client: TestClient) -> Optional[Dict]:
    """Get a non-default physical interface (without IP)."""
    response = client.get('/interfaces/')
    interfaces_data = response.json()
    interfaces = interfaces_data.get('items', [])

    for interface in interfaces:
        if (
            interface['name'] != network_settings.network_interface
            and not interface['ip']
        ):
            return cast(Dict, interface)

    return None


@pytest.fixture
def bridge(
    client: TestClient, physical_interface: Dict
) -> Generator[Dict, None, None]:
    """Create a test bridge and delete it after test."""
    bridge_data = {
        'name': generate_test_entity_name('br'),
        'type': 'bridge',
        'interfaces': [physical_interface],
        'ip': '',
    }

    response = client.post('/interfaces/create/', json=bridge_data)
    bridge_data = response.json()
    wait_for_field_value(
        client, f'/interfaces/{bridge_data["id"]}', 'status', 'available'
    )

    yield bridge_data

    cleanup_test_bridges()
