from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.inventories import service
from src.domains.inventories.models import Inventario
from src.domains.inventories.schemas import InventarioCreate, InventarioUpdate
from src.domains.organizations.models import Organizacao


class TestListInventories:
    async def test_returns_empty_list_when_no_inventories(self, database_session: AsyncSession):
        result = await service.list_inventories(None, database_session)
        assert result == []

    async def test_returns_all_inventories_when_no_filter(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        database_session.add(Inventario(
            organizacao_id=organization.id, nome="Inventory A", ano_base=2023
        ))
        database_session.add(Inventario(
            organizacao_id=organization.id, nome="Inventory B", ano_base=2024
        ))
        await database_session.flush()

        result = await service.list_inventories(None, database_session)

        assert len(result) >= 2

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_a = Organizacao(nome="Org A")
        organization_b = Organizacao(nome="Org B")
        database_session.add(organization_a)
        database_session.add(organization_b)
        await database_session.flush()

        database_session.add(Inventario(
            organizacao_id=organization_a.id, nome="Org A Inventory", ano_base=2023
        ))
        database_session.add(Inventario(
            organizacao_id=organization_b.id, nome="Org B Inventory", ano_base=2023
        ))
        await database_session.flush()

        result = await service.list_inventories(organization_a.id, database_session)

        assert all(inv.organizacao_id == organization_a.id for inv in result)
        names = [inv.nome for inv in result]
        assert "Org A Inventory" in names
        assert "Org B Inventory" not in names

    async def test_orders_by_ano_base_descending(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        database_session.add(Inventario(
            organizacao_id=organization.id, nome="Old", ano_base=2020
        ))
        database_session.add(Inventario(
            organizacao_id=organization.id, nome="New", ano_base=2024
        ))
        await database_session.flush()

        result = await service.list_inventories(organization.id, database_session)

        assert result[0].ano_base >= result[-1].ano_base


class TestGetInventory:
    async def test_returns_inventory_when_found(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        inventory = Inventario(
            organizacao_id=organization.id, nome="My Inventory", ano_base=2023
        )
        database_session.add(inventory)
        await database_session.flush()

        result = await service.get_inventory(inventory.id, database_session)

        assert result.id == inventory.id
        assert result.nome == "My Inventory"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.get_inventory(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestCreateInventory:
    async def test_creates_inventory_with_required_fields(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        data = InventarioCreate(
            organizacao_id=organization.id,
            nome="New Inventory",
            ano_base=2024,
        )
        result = await service.create_inventory(data, database_session)

        assert result.id is not None
        assert result.nome == "New Inventory"
        assert result.ano_base == 2024
        assert result.organizacao_id == organization.id

    async def test_creates_inventory_with_optional_fields(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        data = InventarioCreate(
            organizacao_id=organization.id,
            nome="Full Inventory",
            ano_base=2024,
            descricao="Detailed description",
            status="em_andamento",
            data_inicio="2024-01-01",
            data_finalizacao="2024-12-31",
        )
        result = await service.create_inventory(data, database_session)

        assert result.descricao == "Detailed description"
        assert result.status == "em_andamento"
        assert result.data_inicio == "2024-01-01"
        assert result.data_finalizacao == "2024-12-31"


class TestUpdateInventory:
    async def test_updates_inventory_fields(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        inventory = Inventario(
            organizacao_id=organization.id, nome="Old Name", ano_base=2023
        )
        database_session.add(inventory)
        await database_session.flush()

        data = InventarioUpdate(nome="New Name", status="concluido")
        result = await service.update_inventory(inventory.id, data, database_session)

        assert result.nome == "New Name"
        assert result.status == "concluido"

    async def test_update_ignores_none_fields(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        inventory = Inventario(
            organizacao_id=organization.id,
            nome="Keep Name",
            ano_base=2023,
            status="rascunho",
        )
        database_session.add(inventory)
        await database_session.flush()

        data = InventarioUpdate(status="concluido")
        result = await service.update_inventory(inventory.id, data, database_session)

        assert result.nome == "Keep Name"
        assert result.status == "concluido"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.update_inventory(uuid4(), InventarioUpdate(), database_session)

        assert exception_info.value.status_code == 404


class TestDeleteInventory:
    async def test_deletes_existing_inventory(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        inventory = Inventario(
            organizacao_id=organization.id, nome="Delete Me", ano_base=2023
        )
        database_session.add(inventory)
        await database_session.flush()
        inventory_id = inventory.id

        await service.delete_inventory(inventory_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await service.get_inventory(inventory_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.delete_inventory(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestInventoryRoutes:
    async def _create_organization(self, client) -> str:
        response = await client.post("/organizations", json={"nome": "Inventory Route Org"})
        return response.json()["id"]

    async def test_list_inventories_returns_200(self, client):
        response = await client.get("/inventories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_inventories_filtered_by_organization(self, client):
        organization_id = await self._create_organization(client)
        response = await client.get(f"/inventories?organizacao_id={organization_id}")
        assert response.status_code == 200

    async def test_create_inventory_returns_201(self, client):
        organization_id = await self._create_organization(client)
        payload = {
            "organizacao_id": organization_id,
            "nome": "Test Inventory",
            "ano_base": 2024,
        }
        response = await client.post("/inventories", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["nome"] == "Test Inventory"
        assert body["ano_base"] == 2024

    async def test_get_inventory_returns_200(self, client):
        organization_id = await self._create_organization(client)
        create_response = await client.post(
            "/inventories",
            json={"organizacao_id": organization_id, "nome": "Get Me", "ano_base": 2023},
        )
        inventory_id = create_response.json()["id"]

        response = await client.get(f"/inventories/{inventory_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "Get Me"

    async def test_get_inventory_returns_404_for_unknown_id(self, client):
        response = await client.get(f"/inventories/{uuid4()}")
        assert response.status_code == 404

    async def test_update_inventory_returns_200(self, client):
        organization_id = await self._create_organization(client)
        create_response = await client.post(
            "/inventories",
            json={"organizacao_id": organization_id, "nome": "Before Update", "ano_base": 2023},
        )
        inventory_id = create_response.json()["id"]

        response = await client.put(
            f"/inventories/{inventory_id}", json={"nome": "After Update"}
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "After Update"

    async def test_delete_inventory_returns_204(self, client):
        organization_id = await self._create_organization(client)
        create_response = await client.post(
            "/inventories",
            json={"organizacao_id": organization_id, "nome": "Delete Me", "ano_base": 2023},
        )
        inventory_id = create_response.json()["id"]

        response = await client.delete(f"/inventories/{inventory_id}")
        assert response.status_code == 204
