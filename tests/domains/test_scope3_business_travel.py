from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.reference_data.models import (
    AeroportoCoordenada,
    FatorEmissaoAerea,
    FatorTransporteOnibus,
    TransporteMetro,
    TransporteTrem,
)
from src.domains.scope3.business_travel import service as business_travel_service
from src.domains.scope3.business_travel.models import Deslocamento, EmissaoViagemNegocio
from src.domains.scope3.business_travel.schemas import (
    DeslocamentoCreate,
    EmissaoViagemNegocioCreate,
)


class TestBusinessTravelServiceList:
    async def test_returns_empty_list_when_no_records(self, database_session: AsyncSession):
        result = await business_travel_service.list_records(None, None, database_session)

        assert result == []

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(
            EmissaoViagemNegocio(
                organizacao_id=organization_id, tipo_transporte="aereo", ano=2023, mes=1
            )
        )
        database_session.add(
            EmissaoViagemNegocio(
                organizacao_id=uuid4(), tipo_transporte="onibus", ano=2023, mes=1
            )
        )
        await database_session.flush()

        result = await business_travel_service.list_records(
            None, organization_id, database_session
        )

        assert len(result) == 1
        assert result[0].organizacao_id == organization_id


class TestBusinessTravelServiceGet:
    async def test_returns_record_when_found(self, database_session: AsyncSession):
        record = EmissaoViagemNegocio(tipo_transporte="aereo", ano=2023, mes=1)
        database_session.add(record)
        await database_session.flush()

        result = await business_travel_service.get_record(record.id, database_session)

        assert result.id == record.id
        assert result.tipo_transporte == "aereo"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await business_travel_service.get_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestBusinessTravelServiceCreate:
    async def test_creates_air_record_without_emissions_when_origin_is_missing(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(tipo_transporte="aereo", ano=2023, mes=1)

        result = await business_travel_service.create_record(data, database_session)

        assert result.id is not None
        assert result.emissoes_aerea_co2 is None

    async def test_raises_422_when_origin_airport_not_found_in_database(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(
            tipo_transporte="aereo",
            origin="XXX",
            destination="YYY",
            ano=2023,
            mes=1,
        )

        with pytest.raises(HTTPException) as exception_info:
            await business_travel_service.create_record(data, database_session)

        assert exception_info.value.status_code == 422

    async def test_creates_air_record_with_emissions_when_airports_and_factor_available(
        self, database_session: AsyncSession
    ):
        database_session.add(
            AeroportoCoordenada(sigla="GRU", latitude=-23.4356, longitude=-46.4731)
        )
        database_session.add(
            AeroportoCoordenada(sigla="GIG", latitude=-22.8100, longitude=-43.2506)
        )
        database_session.add(
            FatorEmissaoAerea(
                ano_referencia=2023,
                distancia_aerea="short",
                acrescimo_rota=1.08,
                co2_aereo_passageiro_km=0.133,
                ch4_aereo_passageiro_km=0.000004,
                n2o_aereo_passageiro_km=0.000041,
            )
        )
        await database_session.flush()

        data = EmissaoViagemNegocioCreate(
            tipo_transporte="aereo",
            origin="GRU",
            destination="GIG",
            ano=2023,
            mes=1,
            quantidade_passageiros=1,
            round_trip=False,
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_aerea_co2 is not None
        assert result.emissoes_aerea_co2 > 0
        assert result.emissoes_tco2e_total is not None
        assert result.distance is not None

    async def test_creates_air_record_with_distance_only_when_no_emission_factor(
        self, database_session: AsyncSession
    ):
        database_session.add(
            AeroportoCoordenada(sigla="CGH", latitude=-23.6261, longitude=-46.6565)
        )
        database_session.add(
            AeroportoCoordenada(sigla="SDU", latitude=-22.9105, longitude=-43.1632)
        )
        await database_session.flush()

        data = EmissaoViagemNegocioCreate(
            tipo_transporte="aereo",
            origin="CGH",
            destination="SDU",
            ano=2050,
            mes=1,
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.distance is not None
        assert result.emissoes_aerea_co2 is None

    async def test_creates_bus_record_without_emissions_when_distance_is_missing(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(tipo_transporte="onibus", ano=2023, mes=1)

        result = await business_travel_service.create_record(data, database_session)

        assert result.id is not None
        assert result.emissoes_co2 is None

    async def test_creates_bus_record_without_emissions_when_factor_not_in_database(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(
            tipo_transporte="onibus", distance=100.0, ano=2023, mes=1
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is None

    async def test_creates_bus_record_with_emissions_when_factor_available(
        self, database_session: AsyncSession
    ):
        database_session.add(
            FatorTransporteOnibus(
                ano=2023,
                tipo_onibus="urbano",
                diesel_co2_pkm=0.089,
                diesel_ch4_pkm=0.000003,
                diesel_n2o_pkm=0.000004,
            )
        )
        await database_session.flush()

        data = EmissaoViagemNegocioCreate(
            tipo_transporte="onibus",
            distance=100.0,
            ano=2023,
            mes=1,
            quantidade_passageiros=1,
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is not None
        assert result.emissoes_co2 > 0
        assert result.emissoes_tco2e_total is not None

    async def test_creates_metro_record_without_emissions_when_distance_is_missing(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(tipo_transporte="metro", ano=2023, mes=1)

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is None

    async def test_creates_metro_record_without_emissions_when_factor_not_in_database(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(
            tipo_transporte="metro", distance=20.0, ano=2023, mes=1
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is None

    async def test_creates_metro_record_with_emissions_when_factor_available(
        self, database_session: AsyncSession
    ):
        database_session.add(TransporteMetro(ano=2023, g_co2_passageiro_km=50.0))
        await database_session.flush()

        data = EmissaoViagemNegocioCreate(
            tipo_transporte="metro",
            distance=20.0,
            ano=2023,
            mes=1,
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is not None
        assert result.emissoes_co2 > 0

    async def test_creates_train_record_without_emissions_when_distance_is_missing(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(tipo_transporte="trem", ano=2023, mes=1)

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is None

    async def test_creates_train_record_without_emissions_when_factor_not_in_database(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(
            tipo_transporte="trem", distance=50.0, ano=2023, mes=1
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is None

    async def test_creates_train_record_with_emissions_when_factor_available(
        self, database_session: AsyncSession
    ):
        database_session.add(TransporteTrem(ano=2023, g_co2_passageiro_km=30.0))
        await database_session.flush()

        data = EmissaoViagemNegocioCreate(
            tipo_transporte="trem",
            distance=50.0,
            ano=2023,
            mes=1,
        )

        result = await business_travel_service.create_record(data, database_session)

        assert result.emissoes_co2 is not None
        assert result.emissoes_co2 > 0

    async def test_creates_unknown_transport_record_without_emissions(
        self, database_session: AsyncSession
    ):
        data = EmissaoViagemNegocioCreate(tipo_transporte="taxi", ano=2023, mes=1)

        result = await business_travel_service.create_record(data, database_session)

        assert result.id is not None
        assert result.emissoes_tco2e_total is None


class TestBusinessTravelServiceDelete:
    async def test_deletes_existing_record(self, database_session: AsyncSession):
        record = EmissaoViagemNegocio(tipo_transporte="aereo", ano=2023, mes=1)
        database_session.add(record)
        await database_session.flush()
        record_id = record.id

        await business_travel_service.delete_record(record_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await business_travel_service.get_record(record_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await business_travel_service.delete_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestDisplacementServiceList:
    async def test_returns_empty_list_when_no_records(self, database_session: AsyncSession):
        result = await business_travel_service.list_displacements(None, database_session)

        assert result == []

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(Deslocamento(organizacao_id=organization_id, transport="carro"))
        database_session.add(Deslocamento(transport="aviao"))
        await database_session.flush()

        result = await business_travel_service.list_displacements(
            organization_id, database_session
        )

        assert len(result) == 1
        assert result[0].organizacao_id == organization_id


class TestDisplacementServiceCreate:
    async def test_creates_displacement_with_required_fields(
        self, database_session: AsyncSession
    ):
        data = DeslocamentoCreate(transport="carro")

        result = await business_travel_service.create_displacement(data, database_session)

        assert result.id is not None
        assert result.transport == "carro"

    async def test_creates_displacement_with_optional_fields(
        self, database_session: AsyncSession
    ):
        data = DeslocamentoCreate(
            transport="aviao",
            distance=500.0,
            round_trip=True,
            origin="GRU",
            destination="GIG",
            year=2023,
        )

        result = await business_travel_service.create_displacement(data, database_session)

        assert result.transport == "aviao"
        assert result.distance == pytest.approx(500.0, rel=1e-6)
        assert result.round_trip is True


class TestBusinessTravelRoutes:
    async def test_list_returns_200(self, client):
        response = await client.get(f"/inventories/{uuid4()}/scope3/business-travel")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_returns_201(self, client):
        payload = {"tipo_transporte": "onibus", "ano": 2023, "mes": 1}

        response = await client.post(
            f"/inventories/{uuid4()}/scope3/business-travel", json=payload
        )

        assert response.status_code == 201
        assert response.json()["tipo_transporte"] == "onibus"

    async def test_get_returns_200(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope3/business-travel",
            json={"tipo_transporte": "metro", "ano": 2023, "mes": 2},
        )
        record_id = create_response.json()["id"]

        response = await client.get(
            f"/inventories/{inventory_id}/scope3/business-travel/{record_id}"
        )

        assert response.status_code == 200

    async def test_get_returns_404_for_unknown_id(self, client):
        response = await client.get(
            f"/inventories/{uuid4()}/scope3/business-travel/{uuid4()}"
        )

        assert response.status_code == 404

    async def test_delete_returns_204(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope3/business-travel",
            json={"tipo_transporte": "trem", "ano": 2023, "mes": 1},
        )
        record_id = create_response.json()["id"]

        response = await client.delete(
            f"/inventories/{inventory_id}/scope3/business-travel/{record_id}"
        )

        assert response.status_code == 204

    async def test_create_displacement_returns_201(self, client):
        payload = {"transport": "carro", "distance": 50.0}

        response = await client.post(
            f"/inventories/{uuid4()}/scope3/business-travel/displacements", json=payload
        )

        assert response.status_code == 201
        assert response.json()["transport"] == "carro"
