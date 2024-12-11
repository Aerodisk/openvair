from enum import Enum
from typing import Optional

from typing_extensions import Self


class ReturnCode(Enum):
    """Represents exit codes for commands and their descriptions.

    This Enum maps numerical exit codes to their corresponding textual
    descriptions. These exit codes are used to determine the result of
    executed commands and to provide meaningful error messages.
    """

    SUCCESS = 0, 'Command was successful'
    COMMAND_FAILED = 1, 'Command failed, see command help for more details'
    GO_RUNTIME_ERROR = 2, 'Go runtime error'
    PARTIAL_BACKUP = 3, 'Backup command could not read some source data'
    REPO_NOT_EXIST = 10, 'Repository does not exist (since restic 0.17.0)'
    REPO_LOCK_FAILED = 11, 'Failed to lock repository (since restic 0.17.0)'
    WRONG_PASSWORD = 12, 'Wrong password (since restic 0.17.1)'
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
