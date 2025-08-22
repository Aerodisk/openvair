#!/usr/bin/env python3
"""Simple VNC system test without external dependencies."""

import json
import threading
import time
import tempfile
import os
from pathlib import Path


class SimpleVncPortManager:
    """Simplified VNC port manager for testing."""
    
    def __init__(self):
        self.state_file = tempfile.mktemp(suffix='.json')
        self.start_port = 6100
        self.end_port = 6200  # Small range for testing
        self._init_state()
    
    def _init_state(self):
        """Initialize state file."""
        state = {
            'allocated_ports': {},
            'free_ports': list(range(self.start_port, self.end_port + 1)),
            'lock': False
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def _load_state(self):
        """Load state from file."""
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def _save_state(self, state):
        """Save state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def allocate_port(self, vm_id: str) -> int:
        """Allocate a port."""
        # Simple file-based locking
        while True:
            try:
                state = self._load_state()
                if state.get('lock'):
                    time.sleep(0.001)
                    continue
                
                state['lock'] = True
                self._save_state(state)
                break
            except:
                time.sleep(0.001)
        
        try:
            if not state['free_ports']:
                raise Exception("No free ports")
            
            port = state['free_ports'].pop(0)
            state['allocated_ports'][str(port)] = {
                'vm_id': vm_id,
                'allocated_at': time.time()
            }
            
            return port
        finally:
            state['lock'] = False
            self._save_state(state)
    
    def release_port(self, port: int, vm_id: str = None):
        """Release a port."""
        while True:
            try:
                state = self._load_state()
                if state.get('lock'):
                    time.sleep(0.001)
                    continue
                
                state['lock'] = True
                self._save_state(state)
                break
            except:
                time.sleep(0.001)
        
        try:
            port_str = str(port)
            if port_str in state['allocated_ports']:
                del state['allocated_ports'][port_str]
                if port not in state['free_ports']:
                    state['free_ports'].append(port)
                    state['free_ports'].sort()
        finally:
            state['lock'] = False
            self._save_state(state)
    
    def get_stats(self):
        """Get statistics."""
        state = self._load_state()
        return {
            'allocated': len(state['allocated_ports']),
            'free': len(state['free_ports']),
            'total': self.end_port - self.start_port + 1
        }


def test_basic_allocation():
    """Test basic port allocation."""
    print("Testing basic allocation...")
    
    manager = SimpleVncPortManager()
    
    # Allocate some ports
    port1 = manager.allocate_port("vm1")
    port2 = manager.allocate_port("vm2")
    
    print(f"Allocated ports: {port1}, {port2}")
    
    assert port1 != port2, "Ports should be different"
    assert 6100 <= port1 <= 6200, "Port should be in range"
    assert 6100 <= port2 <= 6200, "Port should be in range"
    
    stats = manager.get_stats()
    print(f"Stats after allocation: {stats}")
    assert stats['allocated'] == 2, "Should have 2 allocated ports"
    
    # Release ports
    manager.release_port(port1, "vm1")
    manager.release_port(port2, "vm2")
    
    stats = manager.get_stats()
    print(f"Stats after release: {stats}")
    assert stats['allocated'] == 0, "Should have 0 allocated ports"
    
    print("✓ Basic allocation test passed")


def test_concurrent_allocation():
    """Test concurrent allocation."""
    print("Testing concurrent allocation...")
    
    manager = SimpleVncPortManager()
    results = []
    results_lock = threading.Lock()
    
    def allocate_worker(worker_id):
        """Worker function to allocate ports."""
        worker_results = []
        for i in range(5):
            try:
                port = manager.allocate_port(f"worker-{worker_id}-vm-{i}")
                worker_results.append(port)
                time.sleep(0.01)  # Small delay
            except Exception as e:
                print(f"Worker {worker_id} failed: {e}")
                break
        
        with results_lock:
            results.extend(worker_results)
    
    # Start multiple threads
    threads = []
    for i in range(10):
        thread = threading.Thread(target=allocate_worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    print(f"Total ports allocated: {len(results)}")
    
    # Check for duplicates
    unique_results = set(results)
    assert len(results) == len(unique_results), f"Found duplicates: {len(results)} vs {len(unique_results)}"
    
    stats = manager.get_stats()
    print(f"Final stats: {stats}")
    
    print("✓ Concurrent allocation test passed")


def main():
    """Run tests."""
    print("=== Simple VNC Port Manager Test ===\n")
    
    try:
        test_basic_allocation()
        print()
        
        test_concurrent_allocation()
        print()
        
        print("🎉 All tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
