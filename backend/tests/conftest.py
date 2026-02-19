"""Shared fixtures for the RayUK backend test suite.

Sets up an async SQLite database (via aiosqlite) and an httpx AsyncClient
wired to the FastAPI app through dependency overrides, so that tests can
run without a live PostgreSQL instance.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Make the PostgreSQL UUID type work on SQLite.
# SQLAlchemy's postgresql.UUID dialect-specific type cannot be rendered on
# SQLite, so we register a custom DDL compiler that emits CHAR(32) instead.
# ---------------------------------------------------------------------------
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models import Base  # noqa: E402  (import order after dialect patch)

# Compile PG UUID as CHAR(32) when the target dialect is SQLite.
from sqlalchemy.ext.compiler import compiles


@compiles(PG_UUID, "sqlite")
def _compile_pg_uuid_for_sqlite(type_, compiler, **kw):  # noqa: ARG001
    return "CHAR(32)"


# ---------------------------------------------------------------------------
# Test database engine & session factory (in-memory SQLite)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    # SQLite does not support pool_size / max_overflow, but the defaults
    # for StaticPool are fine for testing.
    connect_args={"check_same_thread": False},
)

test_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Enable SQLite foreign-key enforcement (off by default).
@event.listens_for(test_engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
async def _setup_database():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override that provides a test database session."""
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Standalone async session for direct DB manipulation in tests."""
    async with test_session_factory() as session:
        yield session


@pytest.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    """httpx AsyncClient wired to the FastAPI app with test DB."""
    from app.database import get_db
    from app.main import app

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
