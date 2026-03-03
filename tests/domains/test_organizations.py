from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.organizations import service
from src.domains.organizations.models import Organizacao, OrganizacaoUsuario
from src.domains.organizations.schemas import (
    OrganizacaoCreate,
    OrganizacaoUpdate,
    OrganizacaoUsuarioCreate,
)


class TestListOrganizations:
    async def test_returns_empty_list_when_no_organizations(self, database_session: AsyncSession):
        result = await service.list_organizations(database_session)
        assert result == []

    async def test_returns_organizations_ordered_by_name(self, database_session: AsyncSession):
        database_session.add(Organizacao(nome="Zeta Corp"))
        database_session.add(Organizacao(nome="Alpha Ltd"))
        database_session.add(Organizacao(nome="Beta Inc"))
        await database_session.flush()

        result = await service.list_organizations(database_session)

        assert len(result) == 3
        assert result[0].nome == "Alpha Ltd"
        assert result[1].nome == "Beta Inc"
        assert result[2].nome == "Zeta Corp"


class TestGetOrganization:
    async def test_returns_organization_when_found(self, database_session: AsyncSession):
        organization = Organizacao(nome="Test Org")
        database_session.add(organization)
        await database_session.flush()

        result = await service.get_organization(organization.id, database_session)

        assert result.id == organization.id
        assert result.nome == "Test Org"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.get_organization(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestCreateOrganization:
    async def test_creates_organization_with_required_fields(self, database_session: AsyncSession):
        data = OrganizacaoCreate(nome="New Organization")

        result = await service.create_organization(data, database_session)

        assert result.id is not None
        assert result.nome == "New Organization"
        assert result.ativa is True
        assert result.modulo_inventario_habilitado is True
        assert result.modulo_deslocamentos_habilitado is False

    async def test_creates_organization_with_optional_fields(self, database_session: AsyncSession):
        data = OrganizacaoCreate(
            nome="Complete Organization",
            cnpj="12.345.678/0001-90",
            cidade="São Paulo",
            estado="SP",
            pais="Brasil",
            num_funcionarios=100,
            segmento="Tecnologia",
        )

        result = await service.create_organization(data, database_session)

        assert result.nome == "Complete Organization"
        assert result.cnpj == "12.345.678/0001-90"
        assert result.cidade == "São Paulo"
        assert result.num_funcionarios == 100


class TestUpdateOrganization:
    async def test_updates_organization_fields(self, database_session: AsyncSession):
        organization = Organizacao(nome="Original Name")
        database_session.add(organization)
        await database_session.flush()

        data = OrganizacaoUpdate(nome="Updated Name", cidade="Rio de Janeiro")
        result = await service.update_organization(organization.id, data, database_session)

        assert result.nome == "Updated Name"
        assert result.cidade == "Rio de Janeiro"

    async def test_update_ignores_none_fields(self, database_session: AsyncSession):
        organization = Organizacao(nome="Original", cidade="São Paulo")
        database_session.add(organization)
        await database_session.flush()

        data = OrganizacaoUpdate(nome="New Name")
        result = await service.update_organization(organization.id, data, database_session)

        assert result.nome == "New Name"
        assert result.cidade == "São Paulo"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.update_organization(uuid4(), OrganizacaoUpdate(), database_session)

        assert exception_info.value.status_code == 404


class TestDeleteOrganization:
    async def test_deletes_existing_organization(self, database_session: AsyncSession):
        organization = Organizacao(nome="To Be Deleted")
        database_session.add(organization)
        await database_session.flush()
        organization_id = organization.id

        await service.delete_organization(organization_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await service.get_organization(organization_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.delete_organization(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestListOrganizationUsers:
    async def test_returns_empty_list_when_no_users(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        result = await service.list_organization_users(organization.id, database_session)

        assert result == []

    async def test_returns_users_for_organization(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        membership = OrganizacaoUsuario(
            organizacao_id=organization.id,
            user_id="user-123",
            papel="admin",
        )
        database_session.add(membership)
        await database_session.flush()

        result = await service.list_organization_users(organization.id, database_session)

        assert len(result) == 1
        assert result[0].user_id == "user-123"
        assert result[0].papel == "admin"


class TestAddOrganizationUser:
    async def test_adds_user_to_organization(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        data = OrganizacaoUsuarioCreate(user_id="new-user-id", papel="viewer")
        result = await service.add_organization_user(
            organization.id, data, "granter-id", database_session
        )

        assert result.organizacao_id == organization.id
        assert result.user_id == "new-user-id"
        assert result.papel == "viewer"
        assert result.granted_by == "granter-id"


class TestRemoveOrganizationUser:
    async def test_removes_user_from_organization(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        membership = OrganizacaoUsuario(
            organizacao_id=organization.id,
            user_id="user-to-remove",
            papel="viewer",
        )
        database_session.add(membership)
        await database_session.flush()

        await service.remove_organization_user(
            organization.id, "user-to-remove", database_session
        )
        await database_session.flush()

        remaining = await service.list_organization_users(organization.id, database_session)
        assert len(remaining) == 0

    async def test_raises_404_when_user_not_in_organization(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await service.remove_organization_user(
                organization.id, "nonexistent-user", database_session
            )

        assert exception_info.value.status_code == 404


class TestOrganizationRoutes:
    async def test_list_organizations_returns_200(self, client):
        response = await client.get("/organizations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_organization_returns_201(self, client):
        payload = {"nome": "Route Test Org"}
        response = await client.post("/organizations", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["nome"] == "Route Test Org"
        assert "id" in body

    async def test_get_organization_returns_200(self, client):
        create_response = await client.post("/organizations", json={"nome": "Fetch Org"})
        organization_id = create_response.json()["id"]

        response = await client.get(f"/organizations/{organization_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "Fetch Org"

    async def test_get_organization_returns_404_for_unknown_id(self, client):
        response = await client.get(f"/organizations/{uuid4()}")
        assert response.status_code == 404

    async def test_update_organization_returns_200(self, client):
        create_response = await client.post("/organizations", json={"nome": "Before Update"})
        organization_id = create_response.json()["id"]

        response = await client.put(
            f"/organizations/{organization_id}", json={"nome": "After Update"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "After Update"

    async def test_delete_organization_returns_204(self, client):
        create_response = await client.post("/organizations", json={"nome": "Delete Me"})
        organization_id = create_response.json()["id"]

        response = await client.delete(f"/organizations/{organization_id}")
        assert response.status_code == 204

    async def test_list_organization_users_returns_200(self, client):
        create_response = await client.post("/organizations", json={"nome": "Users Org"})
        organization_id = create_response.json()["id"]

        response = await client.get(f"/organizations/{organization_id}/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_add_organization_user_returns_201(self, client):
        create_response = await client.post("/organizations", json={"nome": "Membership Org"})
        organization_id = create_response.json()["id"]

        payload = {"user_id": "route-user-id", "papel": "member"}
        response = await client.post(f"/organizations/{organization_id}/users", json=payload)
        assert response.status_code == 201
        assert response.json()["user_id"] == "route-user-id"

    async def test_remove_organization_user_returns_204(self, client):
        create_response = await client.post("/organizations", json={"nome": "Remove User Org"})
        organization_id = create_response.json()["id"]

        await client.post(
            f"/organizations/{organization_id}/users",
            json={"user_id": "user-for-removal", "papel": "viewer"},
        )

        response = await client.delete(
            f"/organizations/{organization_id}/users/user-for-removal"
        )
        assert response.status_code == 204
