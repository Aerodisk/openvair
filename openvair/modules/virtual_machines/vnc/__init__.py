"""Simplified VNC management subsystem for Open vAIR virtual machines.

This module provides simple thread-safe port allocation and websockify process
management for VNC access to virtual machines.

Upgraded from complex 940-line system to simple ~250-line solution.
"""

# Import the new simple VNC functions for easy access
from .manager import (
    VNCManager,
)
from .exceptions import (
    VncManagerError,
    VncPortAllocationError,
    VncSessionStartupError,
    VncProcessNotFoundError,
)

# Make functions available at package level
__all__ = [
    'VNCManager',
    # Exceptions
    'VncManagerError',
    'VncPortAllocationError',
    'VncProcessNotFoundError',
    'VncSessionStartupError',
]
