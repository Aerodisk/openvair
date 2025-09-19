"""Module defining data models for block device interfaces.

This module provides Pydantic data models for representing different types of
block device interfaces, including general interface information, login
status, and IQN data.

Classes:
    Interface: Represents general information about a block device interface.
    InterfaceLogin: Represents a block device interface with login status.
    InterfaceDeleted: Represents a block device interface that has been deleted.
    IQN: Represents an IQN (iSCSI Qualified Name).
"""


from pydantic import BaseModel


class Interface(BaseModel):
    """Represents general information about a block device interface.

    Attributes:
        inf_type (str): The type of the block device interface.
        ip (str): The IP address of the block device interface.
        port (Optional[str]): The port number of the block device interface.
    """

    inf_type: str
    ip: str
    port: str | None = None


class InterfaceLogin(Interface):
    """Represents a block device interface with login status.

    Attributes:
        id (str): The ID of the block device interface.
        status (str): The login status of the block device interface.
    """

    id: str
    status: str


class InterfaceDeleted(BaseModel):
    """Represents a block device interface that has been deleted.

    Attributes:
        inf_type (str): The type of the block device interface.
        ip (str): The IP address of the block device interface.
    """

    inf_type: str
    ip: str


class IQN(BaseModel):
    """Represents an IQN (iSCSI Qualified Name).

    Attributes:
        iqn (str): The IQN.
    """

    iqn: str


class Session(BaseModel):
    """Represents an session associated with block device.

    Attributes:
        ip (str): REMOTE_SERVER_IP. The IP address of the block device target.
        status (str): SOME_STATUS. The status of the block device session.
        id (str): SESSION_ID. The ID of the block device session.
        inf_type (str): SESSION_TYPE. The type of the block device interface.
        port (str): REMOTE_SERVER_PORT. The port number of the block device
            target.
    """

    ip: str
    status: str
    id: str
    inf_type: str
    port: str | None = None
