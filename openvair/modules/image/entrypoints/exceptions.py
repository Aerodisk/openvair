# noqa: D100
from typing import Any

from openvair.abstracts.base_exception import BaseCustomException


class NotSupportedExtensionError(BaseCustomException):  # noqa: D101
    def __init__(self, message: str, *args: Any) -> None:  # noqa: D107 ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        super().__init__(message, *args)


class FilenameLengthError(BaseCustomException):  # noqa: D101
    def __init__(self, message: str, *args: Any) -> None:  # noqa: D107 ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        super().__init__(message, *args)


class CreateImagePageException(BaseCustomException):
    """Raised if ImagesPage get incorrect args."""

    def __init__(self, message: str, *args: Any) -> None:  # noqa: ANN401 # TODO need to parameterize the arguments correctly, in accordance with static typing
        """Initialize CreateImagePageException with the given arguments."""
        super().__init__(message, *args)
