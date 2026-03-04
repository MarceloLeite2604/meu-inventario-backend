"""Tests for reprocess emissions endpoints (energy and stationary combustion)."""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.reference_data.models import FatorEmissaoEnergia, FatorEstacionaria, Gwp
from src.domains.scope1.stationary_combustion import service as stationary_service
from src.domains.scope1.stationary_combustion.models import EmissaoEstacionaria
from src.domains.scope2.energy import service as energy_service
from src.domains.scope2.energy.models import ConsumoEnergia

INVENTORY_ID = str(uuid4())


async def _seed_energy_factor(session: AsyncSession, ano: int, mes: int, fator: float):
    f = FatorEmissaoEnergia(ano=ano, mes=mes, fator_emissao=fator)
    session.add(f)
    await session.flush()
    return f


async def _seed_stationary_factor(session: AsyncSession, combustivel: str, co2: float):
    f = FatorEstacionaria(combustivel=combustivel, co2=co2, unidade="kg/l")
    session.add(f)
    await session.flush()
    return f


async def _seed_gwp(session: AsyncSession):
    session.add(Gwp(nome_ghg="CH4", gwp_value=28.0))
    session.add(Gwp(nome_ghg="N2O", gwp_value=265.0))
    await session.flush()


# ─── Energy reprocess service tests ─────────────────────────────────────────

@pytest.mark.anyio
class TestEnergyReprocessService:
    async def test_updates_records_with_null_emissions(self, database_session: AsyncSession):
        await _seed_energy_factor(database_session, 2023, 1, 0.5)
        record = ConsumoEnergia(
            consumo_mwh=100.0, ano=2023, mes=1, emissoes_energia_tco2e=None
        )
        database_session.add(record)
        await database_session.flush()

        count = await energy_service.reprocess_emissions(database_session)

        assert count == 1
        assert record.emissoes_energia_tco2e == pytest.approx(50.0)

    async def test_skips_records_already_calculated(self, database_session: AsyncSession):
        await _seed_energy_factor(database_session, 2023, 2, 0.5)
        record = ConsumoEnergia(
            consumo_mwh=100.0, ano=2023, mes=2, emissoes_energia_tco2e=42.0
        )
        database_session.add(record)
        await database_session.flush()

        count = await energy_service.reprocess_emissions(database_session)

        assert count == 0
        assert record.emissoes_energia_tco2e == pytest.approx(42.0)

    async def test_skips_records_without_factor(self, database_session: AsyncSession):
        record = ConsumoEnergia(
            consumo_mwh=100.0, ano=1999, mes=1, emissoes_energia_tco2e=None
        )
        database_session.add(record)
        await database_session.flush()

        count = await energy_service.reprocess_emissions(database_session)

        assert count == 0
        assert record.emissoes_energia_tco2e is None

    async def test_reprocesses_multiple_records(self, database_session: AsyncSession):
        await _seed_energy_factor(database_session, 2024, 1, 0.3)
        await _seed_energy_factor(database_session, 2024, 2, 0.4)
        for mes in (1, 2):
            database_session.add(ConsumoEnergia(
                consumo_mwh=10.0, ano=2024, mes=mes, emissoes_energia_tco2e=None
            ))
        await database_session.flush()

        count = await energy_service.reprocess_emissions(database_session)

        assert count == 2


# ─── Stationary combustion reprocess service tests ──────────────────────────

@pytest.mark.anyio
class TestStationaryReprocessService:
    async def test_updates_records_with_null_emissions(self, database_session: AsyncSession):
        await _seed_gwp(database_session)
        await _seed_stationary_factor(database_session, "Óleo Diesel", 2.7)
        record = EmissaoEstacionaria(
            combustivel="Diesel",
            combustivel_fossil="Óleo Diesel",
            quantidade=100.0,
            quantidade_fossil=100.0,
            unidade="l",
            ano=2023,
            mes=1,
            emissoes_total_tco2e=None,
        )
        database_session.add(record)
        await database_session.flush()

        count = await stationary_service.reprocess_records(database_session)

        assert count == 1
        await database_session.flush()
        await database_session.refresh(record)
        assert record.emissoes_total_tco2e is not None
        assert record.emissoes_total_tco2e > 0

    async def test_skips_records_already_calculated(self, database_session: AsyncSession):
        await _seed_gwp(database_session)
        await _seed_stationary_factor(database_session, "GLP", 1.5)
        record = EmissaoEstacionaria(
            combustivel="GLP",
            combustivel_fossil="GLP",
            quantidade=50.0,
            unidade="kg",
            ano=2023,
            mes=3,
            emissoes_total_tco2e=99.9,
        )
        database_session.add(record)
        await database_session.flush()

        count = await stationary_service.reprocess_records(database_session)

        assert count == 0
        assert record.emissoes_total_tco2e == pytest.approx(99.9)

    async def test_skips_records_without_combustivel_fossil(self, database_session: AsyncSession):
        await _seed_gwp(database_session)
        record = EmissaoEstacionaria(
            combustivel="Unknown Fuel",
            combustivel_fossil=None,
            quantidade=10.0,
            unidade="kg",
            ano=2023,
            mes=4,
            emissoes_total_tco2e=None,
        )
        database_session.add(record)
        await database_session.flush()

        count = await stationary_service.reprocess_records(database_session)

        assert count == 0

    async def test_skips_records_without_matching_factor(self, database_session: AsyncSession):
        await _seed_gwp(database_session)
        record = EmissaoEstacionaria(
            combustivel="Unknown",
            combustivel_fossil="Combustível Inexistente",
            quantidade=10.0,
            unidade="kg",
            ano=2023,
            mes=5,
            emissoes_total_tco2e=None,
        )
        database_session.add(record)
        await database_session.flush()

        count = await stationary_service.reprocess_records(database_session)

        assert count == 0


# ─── Route tests ─────────────────────────────────────────────────────────────

@pytest.mark.anyio
class TestEnergyReprocessRoute:
    async def test_reprocess_returns_200(self, client: AsyncClient):
        response = await client.post(
            f"/inventories/{INVENTORY_ID}/scope2/energy/reprocess"
        )
        assert response.status_code == 200
        assert "reprocessados" in response.json()

    async def test_reprocess_returns_count(self, client: AsyncClient, database_session: AsyncSession):
        await _seed_energy_factor(database_session, 2025, 6, 0.6)
        database_session.add(ConsumoEnergia(
            consumo_mwh=10.0, ano=2025, mes=6, emissoes_energia_tco2e=None
        ))
        await database_session.flush()

        response = await client.post(
            f"/inventories/{INVENTORY_ID}/scope2/energy/reprocess"
        )
        assert response.status_code == 200
        assert response.json()["reprocessados"] >= 1


@pytest.mark.anyio
class TestStationaryReprocessRoute:
    async def test_reprocess_returns_200(self, client: AsyncClient):
        response = await client.post(
            f"/inventories/{INVENTORY_ID}/scope1/stationary-combustion/reprocess"
        )
        assert response.status_code == 200
        assert "reprocessados" in response.json()

    async def test_reprocess_returns_count(
        self, client: AsyncClient, database_session: AsyncSession
    ):
        await _seed_gwp(database_session)
        await _seed_stationary_factor(database_session, "Gasolina", 2.2)
        database_session.add(EmissaoEstacionaria(
            combustivel="Gasolina Comum",
            combustivel_fossil="Gasolina",
            quantidade=20.0,
            quantidade_fossil=20.0,
            unidade="l",
            ano=2025,
            mes=7,
            emissoes_total_tco2e=None,
        ))
        await database_session.flush()

        response = await client.post(
            f"/inventories/{INVENTORY_ID}/scope1/stationary-combustion/reprocess"
        )
        assert response.status_code == 200
        assert response.json()["reprocessados"] >= 1
