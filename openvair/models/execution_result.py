"""This module defines the `ExecutionResult` model used across the project.

The `ExecutionResult` model represents the outcome of a command execution,
providing details about the return code, standard output, and standard error.

Classes:
    ExecutionResult: A Pydantic model encapsulating the result of a command
        execution, including the return code, stdout, and stderr.
"""

from pydantic import BaseModel


class ExecutionResult(BaseModel):
    """A model representing the result of a command execution.

    Attributes:
        returncode (int): The exit code of the executed command.
        stdout (str): The standard output produced by the command.
        stderr (str): The standard error output produced by the command.
    """

    returncode: int
    stdout: str
    stderr: str
