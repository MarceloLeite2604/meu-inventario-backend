import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.users import service
from src.domains.users.models import Profile, UserPermissao
from src.domains.users.schemas import ProfileUpdate, UserPermissaoCreate


class TestGetProfile:
    async def test_returns_profile_when_found(self, database_session: AsyncSession):
        profile = Profile(id="user-abc", email="user@example.com", full_name="Test User")
        database_session.add(profile)
        await database_session.flush()

        result = await service.get_profile("user-abc", database_session)

        assert result.id == "user-abc"
        assert result.email == "user@example.com"
        assert result.full_name == "Test User"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.get_profile("nonexistent-user", database_session)

        assert exception_info.value.status_code == 404


class TestUpsertProfile:
    async def test_creates_profile_when_not_existing(self, database_session: AsyncSession):
        data = ProfileUpdate(email="new@example.com", full_name="New User")

        result = await service.upsert_profile("brand-new-user", data, database_session)

        assert result.id == "brand-new-user"
        assert result.email == "new@example.com"
        assert result.full_name == "New User"

    async def test_updates_existing_profile(self, database_session: AsyncSession):
        profile = Profile(id="existing-user", email="old@example.com", full_name="Old Name")
        database_session.add(profile)
        await database_session.flush()

        data = ProfileUpdate(email="new@example.com", full_name="New Name")
        result = await service.upsert_profile("existing-user", data, database_session)

        assert result.email == "new@example.com"
        assert result.full_name == "New Name"

    async def test_upsert_ignores_none_fields(self, database_session: AsyncSession):
        profile = Profile(id="partial-update-user", email="keep@example.com", full_name="Keep Name")
        database_session.add(profile)
        await database_session.flush()

        data = ProfileUpdate(email="updated@example.com")
        result = await service.upsert_profile("partial-update-user", data, database_session)

        assert result.email == "updated@example.com"
        assert result.full_name == "Keep Name"


class TestListUserPermissions:
    async def test_returns_empty_list_when_no_permissions(self, database_session: AsyncSession):
        result = await service.list_user_permissions("no-perms-user", database_session)
        assert result == []

    async def test_returns_permissions_for_user(self, database_session: AsyncSession):
        permission = UserPermissao(
            user_id="perm-user",
            organizacao_id="org-1",
            tipo="escopo",
            referencia="scope1",
        )
        database_session.add(permission)
        await database_session.flush()

        result = await service.list_user_permissions("perm-user", database_session)

        assert len(result) == 1
        assert result[0].user_id == "perm-user"
        assert result[0].tipo == "escopo"
        assert result[0].referencia == "scope1"

    async def test_returns_only_permissions_for_requested_user(self, database_session: AsyncSession):
        database_session.add(UserPermissao(
            user_id="user-one", organizacao_id="org-1", tipo="escopo", referencia="scope1"
        ))
        database_session.add(UserPermissao(
            user_id="user-two", organizacao_id="org-1", tipo="escopo", referencia="scope2"
        ))
        await database_session.flush()

        result = await service.list_user_permissions("user-one", database_session)

        assert all(permission.user_id == "user-one" for permission in result)


class TestGrantPermission:
    async def test_grants_permission_to_user(self, database_session: AsyncSession):
        data = UserPermissaoCreate(tipo="escopo", referencia="scope1", organizacao_id="org-1")

        result = await service.grant_permission("target-user", data, "granter-id", database_session)

        assert result.user_id == "target-user"
        assert result.organizacao_id == "org-1"
        assert result.tipo == "escopo"
        assert result.referencia == "scope1"
        assert result.granted_by == "granter-id"


class TestHasSystemAccess:
    async def test_returns_true_when_permission_exists(self, database_session: AsyncSession):
        permission = UserPermissao(
            user_id="access-user",
            organizacao_id="org-42",
            tipo="escopo",
            referencia="scope1",
        )
        database_session.add(permission)
        await database_session.flush()

        result = await service.has_system_access(
            "access-user", "org-42", "scope1", database_session
        )

        assert result is True

    async def test_returns_false_when_permission_missing(self, database_session: AsyncSession):
        result = await service.has_system_access(
            "no-access-user", "org-99", "scope1", database_session
        )

        assert result is False

    async def test_returns_false_for_different_scope(self, database_session: AsyncSession):
        permission = UserPermissao(
            user_id="scope-user",
            organizacao_id="org-1",
            tipo="escopo",
            referencia="scope1",
        )
        database_session.add(permission)
        await database_session.flush()

        result = await service.has_system_access(
            "scope-user", "org-1", "scope2", database_session
        )

        assert result is False


class TestUserRoutes:
    async def test_get_profile_returns_404_for_unknown_user(self, client):
        response = await client.get("/users/unknown-user-id")
        assert response.status_code == 404

    async def test_upsert_profile_creates_and_returns_profile(self, client):
        payload = {"email": "route@example.com", "full_name": "Route User"}
        response = await client.put("/users/route-test-user", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == "route-test-user"
        assert body["email"] == "route@example.com"

    async def test_get_profile_returns_200_after_upsert(self, client):
        await client.put(
            "/users/fetch-route-user",
            json={"email": "fetch@example.com", "full_name": "Fetch User"},
        )

        response = await client.get("/users/fetch-route-user")
        assert response.status_code == 200
        assert response.json()["full_name"] == "Fetch User"

    async def test_list_user_permissions_returns_200(self, client):
        response = await client.get("/users/any-user/permissions")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_grant_permission_returns_201(self, client):
        payload = {
            "tipo": "escopo",
            "referencia": "scope1",
            "organizacao_id": "org-route-test",
        }
        response = await client.post("/users/grant-perm-user/permissions", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["user_id"] == "grant-perm-user"
        assert body["tipo"] == "escopo"
