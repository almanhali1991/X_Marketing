"""
Database session management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

from .config import get_settings


def get_database_url() -> str:
    """Get SQLite database URL with proper path handling"""
    settings = get_settings()
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.absolute()}"


# Create engine with SQLite-specific optimizations
engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode and foreign keys for SQLite"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session (dependency for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from .models import Base
    Base.metadata.create_all(bind=engine)
