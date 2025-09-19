"""This module defines the models for command execution parameters and results.

Classes:
    ExecutionResult: Represents the outcome of a command execution.
    ExecuteParams: Encapsulates parameters for executing a shell command.
"""


from pydantic import Field, BaseModel


class ExecutionResult(BaseModel):
    """Represents the result of a command execution.

    Attributes:
        returncode (int): The exit code of the executed command.
        stdout (str): The standard output produced by the command.
        stderr (str): The standard error output produced by the command.
    """

    returncode: int
    stdout: str
    stderr: str


class ExecuteParams(BaseModel):
    """Encapsulates parameters for executing a shell command.

    Attributes:
        shell (bool): If True, the command will be executed through the shell.
        run_as_root (bool): If True, the command will be executed with root
            privileges.
        root_helper (str): Command used to elevate privileges, such as 'sudo'.
        timeout (Optional[float]): Maximum time in seconds to wait for the
            command to complete.
        env (Optional[Dict[str, str]]): Environment variables for the command.
        raise_on_error (bool): If True, raises an exception if the command
            fails.
    """

    shell: bool = Field(
        default=False,
        description='If True, the command will be executed through the shell.',
    )
    run_as_root: bool = Field(
        default=False,
        description=(
            'If True, the command will be executed with root privileges.'
        ),
    )
    root_helper: str = Field(
        default='sudo',
        description="Command used to elevate privileges, such as 'sudo'.",
    )
    timeout: float | None = Field(
        default=None,
        description=(
            'Maximum time in seconds to wait for the command to complete.'
        ),
    )
    env: dict[str, str] | None = Field(
        default=None, description='Environment variables for the command.'
    )
    raise_on_error: bool = Field(
        default=False,
        description='If True, raises an exception if the command fails.',
    )
