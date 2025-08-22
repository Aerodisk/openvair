#!/usr/bin/env python3
"""Test script for VNC port allocation system.

This script tests the basic functionality of the new VNC port management
system to ensure it can handle concurrent allocations correctly.
"""

import sys
import threading
import time
from pathlib import Path

# Add openvair to Python path
sys.path.insert(0, str(Path(__file__).parent))

from openvair.modules.virtual_machines.vnc.port_pool_manager import VncPortPoolManager
from openvair.modules.virtual_machines.vnc.session_coordinator import VncSessionCoordinator
from openvair.modules.virtual_machines.vnc.exceptions import VncPortPoolExhaustedException


def test_port_allocation():
    """Test basic port allocation and deallocation."""
    print("Testing basic port allocation...")
    
    manager = VncPortPoolManager()
    
    # Test allocation
    port1 = manager.allocate_port("vm-test-1")
    port2 = manager.allocate_port("vm-test-2")
    
    print(f"Allocated ports: {port1}, {port2}")
    
    assert port1 != port2, "Allocated ports should be different"
    assert port1 >= 6100 and port1 <= 6999, "Port should be in configured range"
    assert port2 >= 6100 and port2 <= 6999, "Port should be in configured range"
    
    # Test release
    manager.release_port(port1, "vm-test-1")
    manager.release_port(port2, "vm-test-2")
    
    print("✓ Basic port allocation test passed")


def test_concurrent_allocation():
    """Test concurrent port allocation from multiple threads."""
    print("Testing concurrent port allocation...")
    
    manager = VncPortPoolManager()
    allocated_ports = []
    allocation_lock = threading.Lock()
    
    def allocate_ports(thread_id: int):
        """Allocate ports in a thread."""
        thread_ports = []
        for i in range(5):  # Each thread allocates 5 ports
            vm_id = f"vm-thread-{thread_id}-{i}"
            try:
                port = manager.allocate_port(vm_id)
                thread_ports.append((port, vm_id))
                time.sleep(0.01)  # Small delay to increase contention
            except VncPortPoolExhaustedException:
                print(f"Thread {thread_id}: Port pool exhausted")
                break
        
        with allocation_lock:
            allocated_ports.extend(thread_ports)
    
    # Start 10 threads
    threads = []
    for i in range(10):
        thread = threading.Thread(target=allocate_ports, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print(f"Total ports allocated: {len(allocated_ports)}")
    
    # Check for duplicates
    ports_only = [port for port, _ in allocated_ports]
    unique_ports = set(ports_only)
    
    assert len(ports_only) == len(unique_ports), f"Found duplicate ports: {len(ports_only)} vs {len(unique_ports)}"
    
    # Release all ports
    for port, vm_id in allocated_ports:
        manager.release_port(port, vm_id)
    
    print("✓ Concurrent allocation test passed")


def test_port_statistics():
    """Test port statistics functionality."""
    print("Testing port statistics...")
    
    manager = VncPortPoolManager()
    
    # Get initial stats
    stats = manager.get_port_statistics()
    initial_free = stats['free_ports']
    
    print(f"Initial stats: {stats}")
    
    # Allocate some ports
    allocated_ports = []
    for i in range(10):
        port = manager.allocate_port(f"vm-stats-test-{i}")
        allocated_ports.append(port)
    
    # Check updated stats
    stats = manager.get_port_statistics()
    print(f"After allocation: {stats}")
    
    assert stats['allocated_ports'] == 10, "Should have 10 allocated ports"
    assert stats['free_ports'] == initial_free - 10, "Free ports should decrease by 10"
    
    # Release ports
    for i, port in enumerate(allocated_ports):
        manager.release_port(port, f"vm-stats-test-{i}")
    
    # Check final stats
    stats = manager.get_port_statistics()
    print(f"After release: {stats}")
    
    assert stats['allocated_ports'] == 0, "Should have 0 allocated ports"
    assert stats['free_ports'] == initial_free, "Free ports should return to initial value"
    
    print("✓ Port statistics test passed")


def test_session_coordinator():
    """Test the session coordinator functionality."""
    print("Testing session coordinator...")
    
    coordinator = VncSessionCoordinator()
    
    # Test system status
    status = coordinator.get_system_status()
    print(f"System status: {status}")
    
    # Test cleanup (should not fail even with no stale resources)
    cleanup_stats = coordinator.cleanup_stale_resources()
    print(f"Cleanup stats: {cleanup_stats}")
    
    print("✓ Session coordinator test passed")


def main():
    """Run all tests."""
    print("Starting VNC system tests...\n")
    
    try:
        test_port_allocation()
        print()
        
        test_concurrent_allocation()
        print()
        
        test_port_statistics()
        print()
        
        test_session_coordinator()
        print()
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
