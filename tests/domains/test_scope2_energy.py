from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.reference_data.models import FatorEmissaoEnergia
from src.domains.scope2.energy import service as energy_service
from src.domains.scope2.energy.models import ConsumoEnergia, UnidadeConsumidora
from src.domains.scope2.energy.schemas import (
    ConsumoEnergiaCreate,
    EvidenciaConsumoEnergiaCreate,
    UnidadeConsumidoraCreate,
)


class TestConsumerUnitServiceList:
    async def test_returns_empty_list_when_no_units(self, database_session: AsyncSession):
        result = await energy_service.list_consumer_units(uuid4(), database_session)

        assert result == []

    async def test_returns_units_for_organization(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(
            UnidadeConsumidora(organizacao_id=organization_id, nome="Unidade Principal")
        )
        database_session.add(
            UnidadeConsumidora(organizacao_id=uuid4(), nome="Outra Unidade")
        )
        await database_session.flush()

        result = await energy_service.list_consumer_units(organization_id, database_session)

        assert len(result) == 1
        assert result[0].nome == "Unidade Principal"


class TestConsumerUnitServiceCreate:
    async def test_creates_consumer_unit_with_required_fields(
        self, database_session: AsyncSession
    ):
        data = UnidadeConsumidoraCreate(
            organizacao_id=uuid4(),
            nome="Matriz",
        )

        result = await energy_service.create_consumer_unit(data, database_session)

        assert result.id is not None
        assert result.nome == "Matriz"
        assert result.ativa is True

    async def test_creates_consumer_unit_with_optional_fields(
        self, database_session: AsyncSession
    ):
        data = UnidadeConsumidoraCreate(
            organizacao_id=uuid4(),
            nome="Filial",
            numero_uc="123456",
            distribuidora="CPFL",
            endereco="Rua Teste, 100",
        )

        result = await energy_service.create_consumer_unit(data, database_session)

        assert result.numero_uc == "123456"
        assert result.distribuidora == "CPFL"


class TestEnergyConsumptionServiceList:
    async def test_returns_empty_list_when_no_records(self, database_session: AsyncSession):
        result = await energy_service.list_consumption_records(None, None, database_session)

        assert result == []

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(
            ConsumoEnergia(organizacao_id=organization_id, consumo_mwh=10.0, ano=2023, mes=1)
        )
        database_session.add(
            ConsumoEnergia(organizacao_id=uuid4(), consumo_mwh=5.0, ano=2023, mes=1)
        )
        await database_session.flush()

        result = await energy_service.list_consumption_records(
            None, organization_id, database_session
        )

        assert len(result) == 1
        assert result[0].organizacao_id == organization_id


class TestEnergyConsumptionServiceGet:
    async def test_returns_record_when_found(self, database_session: AsyncSession):
        record = ConsumoEnergia(consumo_mwh=10.0, ano=2023, mes=1)
        database_session.add(record)
        await database_session.flush()

        result = await energy_service.get_consumption_record(record.id, database_session)

        assert result.id == record.id
        assert result.consumo_mwh == pytest.approx(10.0, rel=1e-6)

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await energy_service.get_consumption_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestEnergyConsumptionServiceCreate:
    async def test_creates_record_without_emissions_when_no_factor_in_database(
        self, database_session: AsyncSession
    ):
        data = ConsumoEnergiaCreate(consumo_mwh=10.0, ano=2023, mes=1)

        result = await energy_service.create_consumption_record(data, database_session)

        assert result.id is not None
        assert result.consumo_mwh == pytest.approx(10.0, rel=1e-6)
        assert result.emissoes_energia_tco2e is None

    async def test_creates_record_with_emissions_when_factor_exists_in_database(
        self, database_session: AsyncSession
    ):
        database_session.add(FatorEmissaoEnergia(ano=2023, mes=6, fator_emissao=0.09))
        await database_session.flush()

        data = ConsumoEnergiaCreate(consumo_mwh=10.0, ano=2023, mes=6)

        result = await energy_service.create_consumption_record(data, database_session)

        assert result.emissoes_energia_tco2e is not None
        assert result.emissoes_energia_tco2e == pytest.approx(0.9, rel=1e-6)


class TestEnergyConsumptionServiceDelete:
    async def test_deletes_existing_record(self, database_session: AsyncSession):
        record = ConsumoEnergia(consumo_mwh=10.0, ano=2023, mes=1)
        database_session.add(record)
        await database_session.flush()
        record_id = record.id

        await energy_service.delete_consumption_record(record_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await energy_service.get_consumption_record(record_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await energy_service.delete_consumption_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestAddEvidenceService:
    async def test_adds_evidence_to_consumption_record(self, database_session: AsyncSession):
        organization_id = uuid4()
        record = ConsumoEnergia(
            organizacao_id=organization_id, consumo_mwh=10.0, ano=2023, mes=1
        )
        database_session.add(record)
        await database_session.flush()

        data = EvidenciaConsumoEnergiaCreate(
            arquivo_url="https://example.com/fatura.pdf",
            nome_arquivo_original="fatura.pdf",
        )

        result = await energy_service.add_evidence(
            consumo_id=record.id,
            organizacao_id=organization_id,
            data=data,
            uploaded_by="test-user",
            session=database_session,
        )

        assert result.id is not None
        assert result.arquivo_url == "https://example.com/fatura.pdf"
        assert result.uploaded_by == "test-user"
        assert result.tipo_documento == "fatura"

    async def test_adds_evidence_with_custom_document_type(
        self, database_session: AsyncSession
    ):
        organization_id = uuid4()
        record = ConsumoEnergia(
            organizacao_id=organization_id, consumo_mwh=5.0, ano=2023, mes=2
        )
        database_session.add(record)
        await database_session.flush()

        data = EvidenciaConsumoEnergiaCreate(
            arquivo_url="https://example.com/relatorio.pdf",
            nome_arquivo_original="relatorio.pdf",
            tipo_documento="relatorio",
            observacoes="Relatório anual de consumo",
        )

        result = await energy_service.add_evidence(
            consumo_id=record.id,
            organizacao_id=organization_id,
            data=data,
            uploaded_by="auditor-user",
            session=database_session,
        )

        assert result.tipo_documento == "relatorio"
        assert result.observacoes == "Relatório anual de consumo"


class TestEnergyRoutes:
    async def test_list_consumer_units_returns_200(self, client):
        organization_id = uuid4()
        response = await client.get(
            f"/inventories/{uuid4()}/scope2/energy/consumer-units"
            f"?organizacao_id={organization_id}"
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_consumer_unit_returns_201(self, client):
        payload = {
            "organizacao_id": str(uuid4()),
            "nome": "Unidade Teste",
        }

        response = await client.post(
            f"/inventories/{uuid4()}/scope2/energy/consumer-units", json=payload
        )

        assert response.status_code == 201
        assert response.json()["nome"] == "Unidade Teste"

    async def test_list_consumption_records_returns_200(self, client):
        response = await client.get(f"/inventories/{uuid4()}/scope2/energy")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_consumption_record_returns_201(self, client):
        payload = {"consumo_mwh": 10.0, "ano": 2023, "mes": 1}

        response = await client.post(
            f"/inventories/{uuid4()}/scope2/energy", json=payload
        )

        assert response.status_code == 201
        assert response.json()["consumo_mwh"] == pytest.approx(10.0, rel=1e-6)

    async def test_get_consumption_record_returns_200(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope2/energy",
            json={"consumo_mwh": 5.0, "ano": 2023, "mes": 3},
        )
        record_id = create_response.json()["id"]

        response = await client.get(
            f"/inventories/{inventory_id}/scope2/energy/{record_id}"
        )

        assert response.status_code == 200

    async def test_get_consumption_record_returns_404_for_unknown_id(self, client):
        response = await client.get(f"/inventories/{uuid4()}/scope2/energy/{uuid4()}")

        assert response.status_code == 404

    async def test_delete_consumption_record_returns_204(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope2/energy",
            json={"consumo_mwh": 10.0, "ano": 2023, "mes": 1},
        )
        record_id = create_response.json()["id"]

        response = await client.delete(
            f"/inventories/{inventory_id}/scope2/energy/{record_id}"
        )

        assert response.status_code == 204
