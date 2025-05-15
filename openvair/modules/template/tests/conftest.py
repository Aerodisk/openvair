from typing import Dict, Generator  # noqa: D100

import pytest
from fastapi.testclient import TestClient

from openvair.libs.log import get_logger
from openvair.libs.testing_utils import (
    create_resource,
    delete_resource,
    generate_test_entity_name,
)
from openvair.modules.template.entrypoints.schemas.requests import (
    RequestCreateTemplate,
)

LOG = get_logger(__name__)


@pytest.fixture(scope='function')
def test_template(
    client: TestClient, test_storage: Dict, test_template: Dict
) -> Generator[Dict, None, None]:
    """Creates a test volume and deletes it after each test."""
    template_data = RequestCreateTemplate(
        base_volume_id=test_template['id'],
        name=generate_test_entity_name(entity_type='template'),
        description='Template for integration tests',
        storage_id=test_storage['id'],
        is_backing=False,
    ).model_dump(mode='json')
    template = create_resource(
        client, '/templates/', template_data, 'template'
    )['data']

    yield template

    delete_resource(client, '/templates', template['id'], 'volume')
