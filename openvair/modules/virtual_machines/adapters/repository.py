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

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import update

from openvair.common.repositories.base_sqlalchemy import (
    BaseSqlAlchemyRepository,
)
from openvair.modules.virtual_machines.adapters.orm import (
    Disk,
    Snapshots,
    VirtualMachines,
    VirtualInterface,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class VMSqlAlchemyRepository(BaseSqlAlchemyRepository[VirtualMachines]):
    """SQLAlchemy-based implementation of the virtual machine repository.

    This repository implementation uses SQLAlchemy ORM to perform database
    operations for virtual machines, disks, and virtual interfaces.
    """

    def __init__(self, session: 'Session'):
        """Initialize the repository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session used for database
                operations.
        """
        super().__init__(session, VirtualMachines)

    def get_disk_by_id(self, disk_id: int) -> Disk:
        """Retrieve a disk by its ID.

        Args:
            disk_id (int): The ID of the disk to retrieve.

        Returns:
            Disk: The retrieved disk entity.
        """
        return self.session.query(Disk).filter_by(id=disk_id).one()

    def bulk_update_disks(self, disks: List) -> None:
        """Bulk update disk entities in the repository.

        Args:
            disks (List): A list of disk entities to update.
        """
        self.session.execute(update(Disk), disks)

    def bulk_update_virtual_interfaces(self, virt_interfaces: List) -> None:
        """Bulk update virtual interface entities in the repository.

        Args:
            virt_interfaces (List): A list of virtual interface entities to
                update.
        """
        self.session.execute(update(VirtualInterface), virt_interfaces)

    def delete_disk(self, disk: Disk) -> None:
        """Delete a disk entity from the repository.

        Args:
            disk (Disk): The disk entity to delete.
        """
        self.session.delete(disk)

    def delete_virtual_interfaces(self, virt_interfaces: List) -> None:
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

    def add_snapshot(self, snapshot: 'Snapshots') -> None:
        """Add a new snapshot to the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to add.
        """
        self.session.add(snapshot)

    def get_snapshot(
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
            .filter_by(vm_id=vm_id, id=snapshot_id)
            .one()
        )

    def get_snapshot_by_name(
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
            .filter_by(vm_id=vm_id, name=name)
            .first()
        )

    def get_snapshots_by_vm(self, vm_id: str) -> List[Snapshots]:
        """Retrieve all snapshots for a virtual machine.

        Args:
            vm_id (str): The ID of the virtual machine.

        Returns:
            List[Snapshots]: A list of snapshot entities.
        """
        return (
            self.session.query(Snapshots)
            .filter_by(vm_id=vm_id)
            .order_by(Snapshots.created_at)
            .all()
        )

    def delete_snapshot(self, snapshot: 'Snapshots') -> None:
        """Delete a snapshot from the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to delete.
        """
        self.session.delete(snapshot)

    def update_snapshot(self, snapshot: 'Snapshots') -> None:
        """Update a snapshot in the repository.

        Args:
            snapshot (Snapshots): The snapshot entity to update.
        """
        self.session.merge(snapshot)

    def get_current_snapshot(self, vm_id: str) -> Optional[Snapshots]:
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

    def set_current_snapshot(self, snapshot: 'Snapshots') -> None:
        """Mark snapshot as current (and unmark others for this VM).

        Args:
            snapshot: Snapshot to mark as current
        """
        self.session.execute(
            update(Snapshots)
            .where(Snapshots.vm_id == snapshot.vm_id)
            .values(is_current=(Snapshots.id == snapshot.id))
        )

        snapshot.is_current = True

    def unset_current_snapshot(self, vm_id: str) -> None:
        """Unset current snapshot flag for all snapshots of a VM.

        Args:
            vm_id: ID of the virtual machine.
        """
        self.session.execute(
            update(Snapshots)
            .where(Snapshots.vm_id == vm_id)
            .values(is_current=False)
        )

    def get_child_snapshots(self, snapshot: 'Snapshots') -> List[Snapshots]:
        """Get all child snapshots for given snapshot.

        Args:
            snapshot (Snapshots): The parent snapshot entity.

        Returns:
            List[Snapshots]: A list of children snapshot entities.
        """
        return (
            self.session.query(Snapshots)
            .filter_by(parent_id=snapshot.id)
            .all()
        )
