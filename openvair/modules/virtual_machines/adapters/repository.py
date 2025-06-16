"""Module for repository pattern implementation for virtual machines.

This module defines abstract and concrete repository classes for managing
virtual machine data. It provides a way to abstract database operations,
making it easier to switch out the data access layer without affecting
the business logic. The concrete repository implementation uses SQLAlchemy
for database interactions.

Classes:
    AbstractRepository: Abstract base class defining the repository interface
        for virtual machine-related operations.
    SqlAlchemyRepository: Concrete implementation of the repository interface
        using SQLAlchemy for database operations.

Exceptions:
    DBCannotBeConnectedError: Raised when a database connection cannot be
        established.
"""

import abc
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import update
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from openvair.abstracts.exceptions import DBCannotBeConnectedError
from openvair.modules.virtual_machines.adapters.orm import (
    Disk,
    Snapshots,
    VirtualMachines,
    VirtualInterface,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AbstractRepository(metaclass=abc.ABCMeta):
    """Abstract base class for virtual machine repositories.

    This class defines the interface for a repository responsible for
    managing virtual machines, disks, and virtual interfaces. Concrete
    implementations must provide methods for adding, retrieving, and
    deleting virtual machines and related entities.
    """

    def _check_connection(self) -> None:
        """Check the connection to the database.

        This method must be implemented by subclasses to verify if the
        repository can connect to the database.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    # VirtualMachine

    def add(self, virtual_machine: VirtualMachines) -> None:
        """Add a new virtual machine to the repository.

        Args:
            virtual_machine (VirtualMachines): The virtual machine entity to
                add.
        """
        self._add(virtual_machine)

    def get(self, vm_id: str) -> VirtualMachines:
        """Retrieve a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to retrieve.

        Returns:
            VirtualMachines: The retrieved virtual machine entity.
        """
        return self._get(vm_id)

    def get_all(self) -> List:
        """Retrieve all virtual machines from the repository.

        Returns:
            List: A list of all virtual machine entities.
        """
        return self._get_all()

    def delete(self, vm: VirtualMachines) -> None:
        """Delete a virtual machine from the repository.

        Args:
            vm (VirtualMachines): The virtual machine entity to delete.
        """
        return self._delete(vm)

    def get_disk_by_id(self, disk_id: int) -> Disk:
        """Retrieve a disk by its ID.

        Args:
            disk_id (int): The ID of the disk to retrieve.

        Returns:
            Disk: The retrieved disk entity.
        """
        return self._get_disk_by_id(disk_id)

    def bulk_update_disks(self, disks: List) -> None:
        """Bulk update disk entities in the repository.

        Args:
            disks (List): A list of disk entities to update.
        """
        self._bulk_update_disks(disks)

    def bulk_update_virtual_interfaces(self, virt_interfaces: List) -> None:
        """Bulk update virtual interface entities in the repository.

        Args:
            virt_interfaces (List): A list of virtual interface entities to
                update.
        """
        self._bulk_update_virtual_interfaces(virt_interfaces)

    def delete_disk(self, disk: Disk) -> None:
        """Delete a disk entity from the repository.

        Args:
            disk (Disk): The disk entity to delete.
        """
        self._delete_disk(disk)

    def delete_virtual_interfaces(self, virt_interfaces: List) -> None:
        """Delete virtual interface entities from the repository.

        Args:
            virt_interfaces (List): A list of virtual interface entities to
                delete.
        """
        self._delete_virtual_interfaces(virt_interfaces)

    def add_snapshot(self, snapshot: 'Snapshots') -> None:
        """Add a new snapshot to the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to add.
        """
        self._add_snapshot(snapshot)

    def get_snapshot(
            self, vm_id: str, snapshot_id: str
    ) -> Snapshots:
        """Retrieve a snapshot by VM ID and snapshot ID.

        Args:
            vm_id (str): The ID of the virtual machine.
            snapshot_id (str): The ID of the snapshot to retrieve.

        Returns:
            Snapshots: The retrieved snapshot entity.
        """
        return self._get_snapshot(vm_id, snapshot_id)

    def get_snapshot_by_name(
            self, vm_id: str, name: str
    ) -> Optional[Snapshots]:
        """Retrieve a snapshot by VM ID and snapshot name.

        Args:
            vm_id (str): The ID of the virtual machine.
            name (str): The name of the snapshot to retrieve.

        Returns:
            Snapshots: The retrieved snapshot entity.
        """
        return self._get_snapshot_by_name(vm_id, name)

    def get_snapshots_by_vm(self, vm_id: str) -> List[Snapshots]:
        """Retrieve all snapshots for a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.

        Returns:
            List[Snapshots]: A list of snapshot entities.
        """
        return self._get_snapshots_by_vm(vm_id)

    def delete_snapshot(self, snapshot: 'Snapshots') -> None:
        """Delete a snapshot from the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to delete.
        """
        self._delete_snapshot(snapshot)

    def update_snapshot(self, snapshot: 'Snapshots') -> None:
        """Update a snapshot in the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to update.
        """
        self._update_snapshot(snapshot)

    def get_current_snapshot(self, vm_id: str) -> Optional[Snapshots]:
        """Get current snapshot for VM.

        Args:
            vm_id: ID of the virtual machine
        """
        return self._get_current_snapshot(vm_id)

    def set_current_snapshot(self, snapshot: 'Snapshots') -> None:
        """Mark snapshot as current (and unmark others for this VM).

        Args:
            snapshot: Snapshot to mark as current
        """
        return self._set_current_snapshot(snapshot)

    @abc.abstractmethod
    def _add(self, virtual_machine: VirtualMachines) -> None:
        """Add a new virtual machine to the repository.

        Args:
            virtual_machine (VirtualMachines): The virtual machine entity to
                add.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, vm_id: str) -> VirtualMachines:
        """Retrieve a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to retrieve.

        Returns:
            VirtualMachines: The retrieved virtual machine entity.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_all(self) -> List:
        """Retrieve all virtual machines from the repository.

        Returns:
            List: A list of all virtual machine entities.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, vm: VirtualMachines) -> None:
        """Delete a virtual machine from the repository.

        Args:
            vm (VirtualMachines): The virtual machine entity to delete.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_disk_by_id(self, disk_id: int) -> Disk:
        """Retrieve a disk by its ID.

        Args:
            disk_id (int): The ID of the disk to retrieve.

        Returns:
            Disk: The retrieved disk entity.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update_disks(self, disks: List) -> None:
        """Bulk update disk entities in the repository.

        Args:
            disks (List): A list of disk entities to update.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update_virtual_interfaces(self, virt_interfaces: List) -> None:
        """Bulk update virtual interface entities in the repository.

        Args:
            virt_interfaces (List): A list of virtual interface entities to
                update.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete_disk(self, disk: Disk) -> None:
        """Delete a disk entity from the repository.

        Args:
            disk (Disk): The disk entity to delete.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete_virtual_interfaces(self, virt_interfaces: List) -> None:
        """Delete virtual interface entities from the repository.

        Args:
            virt_interfaces (List): A list of virtual interface entities to
                delete.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _add_snapshot(self, snapshot: 'Snapshots') -> None:
        """Add a new snapshot to the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to add.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_snapshot(
            self, vm_id: str, snapshot_id: str
    ) -> Snapshots:
        """Retrieve a snapshot by VM ID and snapshot ID.

        Args:
            vm_id (str): The ID of the virtual machine.
            snapshot_id (str): The ID of the snapshot to retrieve.

        Returns:
            Snapshots: The retrieved snapshot entity.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_snapshot_by_name(
            self, vm_id: str, name: str
    ) -> Optional[Snapshots]:
        """Retrieve a snapshot by VM ID and snapshot ID.

        Args:
            vm_id (str): The ID of the virtual machine.
            name (str): The name of the snapshot to retrieve.

        Returns:
            Snapshots: The retrieved snapshot entity.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_snapshots_by_vm(self, vm_id: str) -> List[Snapshots]:
        """Retrieve all snapshots for a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.

        Returns:
            List[Snapshots]: A list of snapshot entities.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete_snapshot(self, snapshot: 'Snapshots') -> None:
        """Delete a snapshot from the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to delete.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _update_snapshot(self, snapshot: 'Snapshots') -> None:
        """Update a snapshot in the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to update.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_current_snapshot(self, vm_id: str) -> Optional[Snapshots]:
        """Get current snapshot for VM.

        Args:
            vm_id: ID of the virtual machine

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _set_current_snapshot(self, snapshot: 'Snapshots') -> None:
        """Mark snapshot as current.

        Args:
            snapshot: Snapshot to mark as current

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """SQLAlchemy-based implementation of the AbstractRepository.

    This repository implementation uses SQLAlchemy ORM to perform database
    operations for virtual machines, disks, and virtual interfaces.
    """

    def __init__(self, session: 'Session'):
        """Initialize the repository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session used for database
                operations.
        """
        super(SqlAlchemyRepository, self).__init__()
        self.session: Session = session
        self._check_connection()

    def _check_connection(self) -> None:
        """Check the connection to the database.

        This method attempts to connect to the database and raises an exception
        if the connection fails.

        Raises:
            DBCannotBeConnectedError: If the database connection cannot be
                established.
        """
        try:
            self.session.connection()
        except OperationalError:
            raise DBCannotBeConnectedError(message="Can't connect to Database")

    def _add(self, virtual_machine: VirtualMachines) -> None:
        """Add a new virtual machine to the repository.

        Args:
            virtual_machine (VirtualMachines): The virtual machine entity to
                add.
        """
        self.session.add(virtual_machine)

    def _get(self, vm_id: str) -> VirtualMachines:
        """Retrieve a virtual machine by its ID.

        Args:
            vm_id (str): The ID of the virtual machine to retrieve.

        Returns:
            VirtualMachines: The retrieved virtual machine entity.
        """
        return (
            self.session.query(VirtualMachines)
            .options(
                joinedload(VirtualMachines.cpu),
                joinedload(VirtualMachines.os),
                joinedload(VirtualMachines.disks),
                joinedload(VirtualMachines.virtual_interfaces),
                joinedload(VirtualMachines.graphic_interface),
                joinedload(VirtualMachines.ram),
            )
            .filter_by(id=vm_id)
            .one()
        )

    def _get_all(self) -> List:
        """Retrieve all virtual machines from the repository.

        Returns:
            List: A list of all virtual machine entities.
        """
        return (
            self.session.query(VirtualMachines)
            .options(
                joinedload(VirtualMachines.cpu),
                joinedload(VirtualMachines.os),
                joinedload(VirtualMachines.disks),
                joinedload(VirtualMachines.virtual_interfaces),
                joinedload(VirtualMachines.graphic_interface),
                joinedload(VirtualMachines.ram),
            )
            .all()
        )

    def _delete(self, vm: VirtualMachines) -> None:
        """Delete a virtual machine from the repository.

        Args:
            vm (VirtualMachines): The virtual machine entity to delete.
        """
        self.session.delete(vm)

    def _get_disk_by_id(self, disk_id: int) -> Disk:
        """Retrieve a disk by its ID.

        Args:
            disk_id (int): The ID of the disk to retrieve.

        Returns:
            Disk: The retrieved disk entity.
        """
        return self.session.query(Disk).filter_by(id=disk_id).one()

    def _bulk_update_disks(self, disks: List) -> None:
        """Bulk update disk entities in the repository.

        Args:
            disks (List): A list of disk entities to update.
        """
        self.session.execute(update(Disk), disks)

    def _bulk_update_virtual_interfaces(self, virt_interfaces: List) -> None:
        """Bulk update virtual interface entities in the repository.

        Args:
            virt_interfaces (List): A list of virtual interface entities to
                update.
        """
        self.session.execute(update(VirtualInterface), virt_interfaces)

    def _delete_disk(self, disk: Disk) -> None:
        """Delete a disk entity from the repository.

        Args:
            disk (Disk): The disk entity to delete.
        """
        self.session.delete(disk)

    def _delete_virtual_interfaces(self, virt_interfaces: List) -> None:
        """Delete virtual interface entities from the repository.

        Args:
            virt_interfaces (List): A list of virtual interface entities to
                delete.
        """
        (
            self.session.query(VirtualInterface)
            .filter(
                VirtualInterface.id.in_(
                    [v_inter.get('id') for v_inter in virt_interfaces]
                )
            )
            .delete()
        )

    def _add_snapshot(self, snapshot: 'Snapshots') -> None:
        """Add a new snapshot to the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to add.
        """
        self.session.add(snapshot)

    def _get_snapshot(
            self, vm_id: str, snapshot_id: str
    ) -> Snapshots:
        """Retrieve a snapshot by its ID.

        Args:
            vm_id (str): The ID of the virtual machine.
            snapshot_id (str): The ID of the snapshot to retrieve.

        Returns:
            Snapshots: The retrieved snapshot entity.
        """
        return (
            self.session.query(Snapshots)
            .options(joinedload(Snapshots.parent))
            .filter_by(vm_id=vm_id, id=snapshot_id)
            .one()
        )

    def _get_snapshot_by_name(
            self, vm_id: str, name: str
    ) -> Optional[Snapshots]:
        """Retrieve a snapshot by its ID.

        Args:
            vm_id (str): The ID of the virtual machine.
            name (str): The name of the snapshot to retrieve.

        Returns:
            Optional(Snapshots): The retrieved snapshot entity if existed.
        """
        return (
            self.session.query(Snapshots)
            .options(joinedload(Snapshots.parent))
            .filter_by(vm_id=vm_id, name=name)
            .first()
        )

    def _get_snapshots_by_vm(self, vm_id: str) -> List[Snapshots]:
        """Retrieve all snapshots for a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.

        Returns:
            List[Snapshots]: A list of snapshot entities.
        """
        return (
            self.session.query(Snapshots)
            .options(joinedload(Snapshots.parent))
            .filter_by(vm_id=vm_id)
            .order_by(Snapshots.created_at)
            .all()
        )

    def _delete_snapshot(self, snapshot: 'Snapshots') -> None:
        """Delete a snapshot from the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to delete.
        """
        self.session.delete(snapshot)

    def _update_snapshot(self, snapshot: 'Snapshots') -> None:
        """Update a snapshot in the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to update.
        """
        self.session.merge(snapshot)

    def _get_current_snapshot(self, vm_id: str) -> Optional[Snapshots]:
        """Get current snapshot for VM (marked as is_current=True).

        Args:
            vm_id: ID of the virtual machine

        Returns:
            Snapshots or None if no current snapshot exists
        """
        return (
            self.session.query(Snapshots)
            .filter_by(vm_id=vm_id, is_current=True)
            .first()
        )

    def _set_current_snapshot(self, snapshot: 'Snapshots') -> None:
        """Mark snapshot as current (and unmark others for this VM).

        Args:
            snapshot: Snapshot to mark as current
        """
        self.session.execute(
            update(Snapshots)
            .where(Snapshots.vm_id == snapshot.vm_id)
            .values(is_current=False)
        )

        snapshot.is_current = True
