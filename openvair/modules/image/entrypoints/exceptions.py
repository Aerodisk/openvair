# noqa: D100
from openvair.modules.tools.base_exception import BaseCustomException


class NotSupportedExtensionError(BaseCustomException):  # noqa: D101
    def __init__(self, *args):  # noqa: D107
        super(NotSupportedExtensionError, self).__init__(args)


class FilenameLengthError(BaseCustomException):  # noqa: D101
    def __init__(self, *args):  # noqa: D107
        super(FilenameLengthError, self).__init__(args)
