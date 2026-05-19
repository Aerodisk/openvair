import re

# Forbidden command patterns for validation
FORBIDDEN_COMMAND_PATTERNS = [
    r'\brm\s+-rf\b',     # dangerous deletion
    r'\bdd\b',           # raw disk write
    r'\bmkfs\b',         # filesystem creation
    r'\bcurl\b',         # unrestricted network calls
    r'\bwget\b',         # unrestricted downloads
    r'[;&\[\]\|]',       # shell chaining or unsafe symbols
]

def is_command_forbidden(command: str) -> bool:
    """Check if command contains forbidden or unsafe patterns."""
    return any(
        re.search(
            pattern,
            command,
            re.IGNORECASE
        ) for pattern in FORBIDDEN_COMMAND_PATTERNS
    )
