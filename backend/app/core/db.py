from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models (app/models/)."""


_engine = None
_SessionLocal: sessionmaker | None = None


def _normalize_url(database_url: str) -> str:
    """We install psycopg (v3), not psycopg2. SQLAlchemy's plain
    'postgresql://' scheme defaults to psycopg2, so rewrite it to be
    explicit. Neon/most providers hand out plain 'postgresql://' URLs."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def init_engine(database_url: str) -> None:
    """Create the engine/session factory and the tables (if missing).
    Called once at app startup, and again by tests with a throwaway
    sqlite URL to get an isolated database per test."""
    global _engine, _SessionLocal
    _engine = create_engine(_normalize_url(database_url), pool_pre_ping=True, future=True)
    _SessionLocal = sessionmaker(bind=_engine, future=True, expire_on_commit=False)

    # Import models so they register on Base.metadata before create_all.
    from app import models  # noqa: F401

    Base.metadata.create_all(_engine)


def get_session() -> Session:
    """Returns a new Session (use as a context manager: `with get_session() as s:`)."""
    if _SessionLocal is None:
        raise RuntimeError(
            "Database not initialized - call init_engine() first "
            "(this should only happen if DATABASE_URL is set but init_engine wasn't called)."
        )
    return _SessionLocal()


def is_initialized() -> bool:
    return _SessionLocal is not None
