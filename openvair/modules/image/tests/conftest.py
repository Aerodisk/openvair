import uuid  # noqa: D100
import random
import string

# it looks more like utils

def generate_random_string(length: int) -> str:  # noqa: D103
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))  # noqa: S311


def generate_image_name(prefix: str = 'test') -> str:
    """Generate a unique name for a test entity.

    Creates a name in the format "{prefix}-{entity_type}-{uuid}" where uuid
    is a 6-character random hex string. This ensures unique names for test
    entities while maintaining readability.

    Args:
        entity_type: The type of entity (e.g. 'volume', 'storage')
        prefix: Optional prefix to prepend to the name (default: 'test')

    Returns:
        A unique name string for the test entity
    """
    return f'{prefix}-image-{uuid.uuid4().hex[:6]}.iso'
