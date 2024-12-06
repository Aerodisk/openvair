import pytest
import time
import random

from openvair.modules.network.domain.utils.exceptions import (
    OVSManagerException,
    InterfaceNotFoundException,
    BridgeNotFoundException,
)
from openvair.modules.network.domain.utils.ovs_manager import OVSManager

TEST_INTERFACE_PREFIX = 'tst_br'


def generate_unique_id():
    """
    Generate a unique identifier for testing purposes.

    Returns:
        str: A unique identifier.
    """
    timestamp = int(time.time() * 1000)
    random_part = random.randint(1, 1000)
    short_timestamp = str(timestamp)[-3:]  # Используем последние 5 символов
    return f'{short_timestamp}_{random_part}'


@pytest.fixture
def ovs_manager():
    """
    Fixture to create an instance of OVSManager for testing.
    """
    return OVSManager()


@pytest.fixture
def tmp_bridge(ovs_manager):
    """
    Fixture to create a test bridge for testing.
    """
    bridge_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.create_bridge(bridge_name)
    yield bridge_name
    try:
        ovs_manager.delete_bridge(bridge_name)
    except BridgeNotFoundException:
        pass


def test_create_bridge(ovs_manager, tmp_bridge):
    """
    Test for creating an OVS bridge.
    """
    assert ovs_manager.check_bridge_existence(tmp_bridge)


def test_delete_bridge(ovs_manager, tmp_bridge):
    """
    Test for deleting an OVS bridge.
    """
    assert ovs_manager.check_bridge_existence(tmp_bridge)
    ovs_manager.delete_bridge(tmp_bridge)
    assert not ovs_manager.check_bridge_existence(tmp_bridge)


def test_add_interface(ovs_manager, tmp_bridge):
    """
    Test for adding an interface to an OVS bridge.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)
    assert ovs_manager.check_interface_existence(tmp_bridge, interface_name)


def test_remove_interface(ovs_manager, tmp_bridge):
    """
    Test for removing an interface from an OVS bridge.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)
    assert ovs_manager.check_interface_existence(tmp_bridge, interface_name)
    ovs_manager.remove_interface(tmp_bridge, interface_name)
    assert not ovs_manager.check_interface_existence(tmp_bridge, interface_name)


def test_set_interface_address(ovs_manager, tmp_bridge):
    """
    Test for setting the IP address for an OVS interface.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)
    ip_address = '192.168.1.1/24'
    ip_address2 = '192.168.1.2/24'
    ovs_manager.set_interface_address(interface_name, ip_address)
    ovs_manager.set_interface_address(interface_name, ip_address2)
    if ovs_manager.check_interface_existence(tmp_bridge, interface_name):
        addresses = ovs_manager.get_interface_addresses(interface_name)
        assert ip_address in addresses


def test_edit_interface_address(ovs_manager, tmp_bridge):
    """
    Test for editing the IP address for an OVS interface.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)
    initial_ip_address = '192.168.1.1/24'
    ovs_manager.set_interface_address(interface_name, initial_ip_address)
    new_ip_address = '192.168.1.2/24'
    ovs_manager.turn_on_interface(interface_name)
    ovs_manager.edit_interface_address(
        interface_name, initial_ip_address, new_ip_address
    )

    # Check that the new IP address is set
    if ovs_manager.check_interface_existence(tmp_bridge, interface_name):
        addresses = ovs_manager.get_interface_addresses(interface_name)
        assert new_ip_address in addresses

        # Check that the old IP address no longer exists
        assert initial_ip_address not in addresses
    else:
        # The interface doesn't exist, which could happen if deletion failed
        # Add the appropriate code to handle this situation
        pass


def test_create_bridge_failure(ovs_manager):
    """
    Test for failure case when creating an OVS bridge with an invalid name.
    """
    with pytest.raises(OVSManagerException):
        ovs_manager.create_bridge('invalid name')


def test_remove_interface_failure(ovs_manager, tmp_bridge):
    """
    Test for failure case when removing a non-existing interface.
    """
    with pytest.raises(InterfaceNotFoundException):
        ovs_manager.remove_interface(tmp_bridge, 'nonexistent_interface')


def test_edit_interface(ovs_manager, tmp_bridge):
    """
    Test for editing the configuration of an OVS interface.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)
    options = 'type=internal'
    ovs_manager.edit_interface(interface_name, options)
    output = ovs_manager._execute_command(
        f'sudo ovs-vsctl get Interface {interface_name} type'
    )
    assert output.stdout.strip() == 'internal'


def test_turn_off_interface(ovs_manager, tmp_bridge):
    """
    Test for turning off an OVS interface.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)

    # Check that the interface is initially on or in an unknown state
    assert ovs_manager.check_interface_state(
        interface_name, {'DOWN', 'UNKNOWN'}
    )

    ovs_manager.turn_off_interface(interface_name)

    # Check that the interface is now off
    assert ovs_manager.check_interface_state(interface_name)


def test_turn_on_interface(ovs_manager, tmp_bridge):
    """
    Test for turning on an OVS interface.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)

    # Check that the interface is initially off or in an unknown state
    assert ovs_manager.check_interface_state(interface_name)

    ovs_manager.turn_on_interface(interface_name)

    # Check that the interface is now on
    assert ovs_manager.check_interface_state(interface_name, {'UP', 'UNKNOWN'})


def test_check_interface_state(ovs_manager, tmp_bridge):
    """
    Test for checking the state of an OVS interface.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    ovs_manager.add_interface(tmp_bridge, interface_name)

    # Check that the initial state is either up or in an unknown state
    assert ovs_manager.check_interface_state(interface_name)

    # Turn off the interface
    ovs_manager.turn_off_interface(interface_name)

    # Check that the state is now down
    assert ovs_manager.check_interface_state(interface_name, {'DOWN'})


def test_check_interface_existence(ovs_manager, tmp_bridge):
    """
    Test for checking the existence of an interface in an OVS bridge.
    """
    interface_name = f'{TEST_INTERFACE_PREFIX}{generate_unique_id()}'
    assert not ovs_manager.check_interface_existence(tmp_bridge, interface_name)

    # Add the interface to the bridge
    ovs_manager.add_interface(tmp_bridge, interface_name)

    # Check if the interface exists in the bridge
    assert ovs_manager.check_interface_existence(tmp_bridge, interface_name)
