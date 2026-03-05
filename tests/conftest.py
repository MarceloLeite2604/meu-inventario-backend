import os

os.environ.setdefault("MNZ_PB_HOST", "0.0.0.0")
os.environ.setdefault("MNZ_PB_PORT", "8000")
os.environ.setdefault("MNZ_PB_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("MNZ_PB_KEYCLOAK_SERVER_URL", "http://localhost:8080/auth")
os.environ.setdefault("MNZ_PB_KEYCLOAK_REALM", "test-realm")
os.environ.setdefault("MNZ_PB_KEYCLOAK_CLIENT_ID", "test-client")
os.environ.setdefault("MNZ_PB_KEYCLOAK_CLIENT_SECRET_KEY", "test-secret")
os.environ.setdefault("MNZ_PB_CORS_ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("MNZ_PB_CORS_ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS")
os.environ.setdefault("MNZ_PB_CORS_ALLOWED_HEADERS", "Content-Type,Authorization")
os.environ.setdefault("MNZ_PB_SMTP_HOST", "localhost")
os.environ.setdefault("MNZ_PB_SMTP_PORT", "587")
os.environ.setdefault("MNZ_PB_SMTP_USERNAME", "test-smtp-user")
os.environ.setdefault("MNZ_PB_SMTP_PASSWORD", "test-smtp-password")
os.environ.setdefault("MNZ_PB_SMTP_SENDER", "test@example.com")

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.authentication import AuthenticationOrganization, AuthenticationUser, retrieve_authentication_user
from src.database import retrieve_database
from src.main import app
from src.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def make_authentication_user(
    user_id: str = "test-user-id",
    username: str = "testuser",
    email: str = "test@example.com",
    organization_id: str = "1",
    organization_name: str = "Test Organization",
    roles: list[str] | None = None,
) -> AuthenticationUser:
    return AuthenticationUser(
        id=user_id,
        username=username,
        email=email,
        organization=AuthenticationOrganization(
            id=organization_id,
            name=organization_name,
        ),
        roles=roles or [],
    )


@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture
async def database_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def client(database_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_database():
        yield database_session

    def _override_authentication():
        return make_authentication_user()

    app.dependency_overrides[retrieve_database] = _override_database
    app.dependency_overrides[retrieve_authentication_user] = _override_authentication
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_user() -> AuthenticationUser:
    return make_authentication_user()
