"""Utilities for block device operations.

This module provides helper functions to manage and interact with block devices:

- lip_scan: Initiates a Loop Initialization Protocol (LIP) scan on all Fibre
    Channel host adapters.
"""

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.libs.cli.exceptions import ExecuteError

LOG = get_logger(__name__)


def lip_scan() -> None:
    """Performs an LIP scan on Fibre Channel host adapters.

    This function initiates a Loop Initialization Protocol (LIP) scan by writing
    '1' to the 'issue_lip' file for all Fibre Channel host adapters, thereby
    forcing a re-initialization of the Fibre Channel fabric.

    Raises:
        OSError: If there is an error accessing or writing to the 'issue_lip'
            file.
        ExecuteError: If executing the LIP scan command fails for any reason.
    """
    try:
        # Execute the command to issue LIP scan for all Fibre Channel
        # host adapters.
        execute(
            'for i in /sys/class/fc_host/*; do sudo sh -c "echo 1 > $i/issue_lip"; done',  # noqa: E501
            params=ExecuteParams(  # noqa: S604
                shell=True,
                run_as_root=True,
            ),
        )
    except (ExecuteError, OSError) as e:
        msg = (
            f'Error accessing or writing to /sys/class/fc_host/*/issue_lip: {e}'
        )
        LOG.error(msg)
        raise
