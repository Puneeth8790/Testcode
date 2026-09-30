import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

db_url = settings.sync_database_url
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

def create_db_engine():
    """Create SQLAlchemy engine with automatic fallback if Postgres DB is not reachable/created."""
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        # Test connection immediately
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        logger.warning(
            f"Unable to connect to primary PostgreSQL database at '{db_url}': {e}. "
            "Falling back to local SQLite database (app.db) for smooth execution."
        )
        fallback_url = "sqlite:///./app.db"
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True
        )

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for obtaining a SQLAlchemy DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
