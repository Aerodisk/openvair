"""Module for defining and managing restic return codes.

This module provides an Enum class to represent the various exit codes
produced by restic commands. Each exit code is associated with a textual
description, allowing for better readability and error handling in
restic-based applications.

Typical usage example:
    result_code = ReturnCode.from_code(0)
    if result_code == ReturnCode.SUCCESS:
        print("Command executed successfully.")
"""

from enum import Enum
from typing import Optional

from typing_extensions import Self


class ReturnCode(Enum):
    """Represents exit codes for commands and their descriptions.

    This Enum maps numerical exit codes to their corresponding textual
    descriptions. These exit codes help interpret the results of restic
    commands and provide meaningful messages for debugging or error handling.

    Attributes:
        code (int): The numerical exit code associated with a command.
        description (str): A textual description explaining the exit code.
    """

    SUCCESS = 0, 'Command was successful'
    COMMAND_FAILED = 1, 'Command failed'
    GO_RUNTIME_ERROR = 2, 'Go runtime error'
    PARTIAL_BACKUP = 3, 'Backup command could not read some source data'
    REPO_NOT_EXIST = 10, 'Repository does not exist'
    REPO_LOCK_FAILED = 11, 'Failed to lock repository'
    WRONG_PASSWORD = 12, 'Wrong password'
    INTERRUPTED = 130, 'Restic was interrupted using SIGINT or SIGSTOP'

    def __init__(self, code: int, description: str) -> None:
        """Initializes a ReturnCode instance with a code and description.

        Args:
            code (int): The numerical exit code associated with the command.
            description (str): A textual description of the exit code.
        """
        self.code: int = code
        self.description: str = description

    @classmethod
    def from_code(cls, code: int) -> Optional[Self]:
        """Finds the corresponding ReturnCode by numerical exit code.

        Args:
            code (int): The numerical exit code to look up.

        Returns:
            Optional[Self]: The matching ReturnCode instance if found, or None
                if the code does not correspond to a defined ReturnCode.
        """
        return next((rc for rc in cls if rc.code == code), None)
