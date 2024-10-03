from sqlalchemy.orm import sessionmaker

from openvair.config import get_default_session_factory

DEFAULT_SESSION_FACTORY: sessionmaker = get_default_session_factory()
