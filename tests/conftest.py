import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import retrieve_database
from src.main import app
from src.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncSession:
    async with _session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    async def _override_db():
        yield db_session

    app.dependency_overrides[retrieve_database] = _override_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
