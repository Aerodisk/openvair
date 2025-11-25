"""Module defining data models for dashboard metrics.

This module provides Pydantic data models for representing various metrics
related to node performance and resource usage, including CPU, memory,
storage, IOPS, IO latency, bandwidth, and disk information.

Classes:
    CpuData: Represents CPU usage data.
    MemoryData: Represents memory usage data.
    StoragesData: Represents storage usage data.
    IopsData: Represents IOPS (Input/Output Operations Per Second) data.
    IOLatency: Represents IO latency data.
    BandWithData: Represents bandwidth usage data.
    DiskInfo: Represents disk read/write data.
    NodeInfo: Aggregates all the above data models into a comprehensive
        representation of node metrics.
"""

from pydantic import BaseModel


class CpuData(BaseModel):
    """Represents CPU usage data.

    Attributes:
        count (int): The number of CPU cores.
        percentage (float): The percentage of CPU usage.
    """

    count: int
    percentage: float


class MemoryData(BaseModel):
    """Represents memory usage data.

    Attributes:
        value (int): The total memory value.
        used (int): The amount of used memory.
        available (int): The amount of available memory.
        percentage (float): The percentage of memory usage.
    """

    value: int
    used: int
    available: int
    percentage: float


class StoragesData(BaseModel):
    """Represents storage usage data.

    Attributes:
        size (int): The total storage size.
        used (int): The amount of used storage.
        free (int): The amount of free storage.
        percentage (float): The percentage of storage usage.
        cls (str): The class of the storage.
    """

    size: int
    used: int
    free: int
    percentage: float
    cls: str


class IopsData(BaseModel):
    """Represents IOPS (Input/Output Operations Per Second) data.

    Attributes:
        input (int): The number of input operations.
        output (int): The number of output operations.
        date (int): The timestamp of the IOPS data.
    """

    input: int
    output: int
    date: int


class IOLatency(BaseModel):
    """Represents IO latency data.

    Attributes:
        wait (float): The wait time for IO operations.
        date (int): The timestamp of the IO latency data.
    """

    wait: float
    date: int


class BandWithData(BaseModel):
    """Represents bandwidth usage data.

    Attributes:
        read (float): The amount of data read in bandwidth usage.
        write (float): The amount of data written in bandwidth usage.
        date (int): The timestamp of the bandwidth usage data.
    """

    read: float
    write: float
    date: int


class DiskInfo(BaseModel):
    """Represents disk read/write data.

    Attributes:
        read (float): The amount of data read from the disk.
        write (float): The amount of data written to the disk.
        date (int): The timestamp of the disk data.
    """

    read: float
    write: float
    date: int


class NodeInfo(BaseModel):
    """Aggregates node metrics into a comprehensive representation.

    Attributes:
        cpu (CpuData): CPU usage data.
        memory (MemoryData): Memory usage data.
        storage (StoragesData): Storage usage data.
        iops (IopsData): IOPS data.
        io_latency (IOLatency): IO latency data.
        bandwith_data (BandWithData): Bandwidth usage data.
        disk_data (DiskInfo): Disk read/write data.
    """

    cpu: CpuData
    memory: MemoryData
    storage: StoragesData
    iops: IopsData
    io_latency: IOLatency
    bandwith_data: BandWithData
    disk_data: DiskInfo
