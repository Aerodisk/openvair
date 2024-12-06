"""Custom exceptions for the adapters of storage module.

This module defines custom exceptions used in the storage adapters
for handling errors related to storages  operations.

"""

from openvair.modules.tools.base_exception import BaseCustomException


class PartedError(BaseCustomException):  # noqa: D101
    def __init__(self, *args):  # noqa: D107
        super().__init__(*args)
