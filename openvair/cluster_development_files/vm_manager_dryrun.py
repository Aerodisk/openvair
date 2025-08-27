from openvair.libs.log import get_logger  # noqa: D100
from openvair.modules.base_manager import BackgroundTasks

LOG = get_logger(__name__)


class VmManagerDryRun(BackgroundTasks):  # noqa: D101
    @staticmethod
    def create_vm(data_for_method=None, **_):  # type: ignore  # noqa: ANN001, ANN201, ANN205, D102, RUF100
        payload = data_for_method or {}
        name = payload.get('name')
        cpu = payload.get('cpu')
        ram = payload.get('ram')
        LOG.info(name)
        LOG.info(cpu)
        LOG.info(ram)
        assert name, 'name is required'  # noqa: S101
        assert cpu is not None, 'cpu is required'  # noqa: S101
        assert ram is not None, 'ram is required'  # noqa: S101
        # Никакого libvirt — только подтверждение
        return {
            'ok': True,
            'result': {
                'message': f'DRY-RUN create_vm {name} cpu={cpu} ram={ram}'
            },
        }

    @staticmethod
    def delete_vm(*, data_for_method=None, **_):  # type: ignore  # noqa: ANN001, ANN201, ANN205, D102, RUF100
        name = (data_for_method or {}).get('name')
        assert name, 'name is required'  # noqa: S101
        return {'ok': True, 'result': {'message': f'DRY-RUN delete_vm {name}'}}
