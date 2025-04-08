from typing import Dict  # noqa: D100

from openvair.modules.template.domain.base import BaseTemplate


class Qcow2Template(BaseTemplate):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        super().__init__()

    def create(self) -> Dict:  # noqa: D102
        raise NotImplementedError

    def edit(self) -> Dict:  # noqa: D102
        raise NotImplementedError

    def delete(self) -> Dict:  # noqa: D102
        raise NotImplementedError
