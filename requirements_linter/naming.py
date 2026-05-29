"""Naming rules for symbols that appear in YAML contracts."""

from __future__ import annotations


def is_contract_public_name(name: str) -> bool:
    """Return True when ``name`` is a public symbol (no leading underscore).

    Leading ``_`` marks helpers or other non-contract names.
    """
    return not name.startswith('_')
