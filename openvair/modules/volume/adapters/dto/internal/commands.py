from pathlib import Path  # noqa: D100

from pydantic import BaseModel


class CreateVolumeFromTemplateDomainCommandDTO(BaseModel):  # noqa: D101
    template_path: Path
    is_backing: bool
