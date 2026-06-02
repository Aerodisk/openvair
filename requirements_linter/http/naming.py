"""Rules for which symbol names belong in the public contract."""


def is_contract_public_name(name: str) -> bool:
    """Return True if ``name`` is treated as public API (no leading underscore)."""
    return not name.startswith('_')
