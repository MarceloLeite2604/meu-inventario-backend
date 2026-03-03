from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.reference_data.models import (
    FatorEstacionaria,
    FatorTipoCombustivel,
    FatorTratamentoEfluente,
    Gwp,
)
from src.domains.scope1.effluents import service as effluent_service
from src.domains.scope1.effluents.models import EmissaoEfluente
from src.domains.scope1.effluents.schemas import EmissaoEfluenteCreate
from src.domains.scope1.fugitive import service as fugitive_service
from src.domains.scope1.fugitive.models import EmissaoFugitiva
from src.domains.scope1.fugitive.schemas import EmissaoFugitivaCreate
from src.domains.scope1.mobile_combustion import service as mobile_combustion_service
from src.domains.scope1.mobile_combustion.models import EmissaoCombustaoMovel
from src.domains.scope1.mobile_combustion.schemas import EmissaoCombustaoMovelCreate
from src.domains.scope1.stationary_combustion import service as stationary_combustion_service
from src.domains.scope1.stationary_combustion.models import EmissaoEstacionaria
from src.domains.scope1.stationary_combustion.schemas import EmissaoEstacionariaCreate


class TestEffluentServiceList:
    async def test_returns_empty_list_when_no_records(self, database_session: AsyncSession):
        result = await effluent_service.list_records(None, None, database_session)

        assert result == []

    async def test_filters_by_inventory_id(self, database_session: AsyncSession):
        inventory_id = uuid4()
        database_session.add(
            EmissaoEfluente(inventario_id=inventory_id, tipo_efluente="domestico", ano=2023)
        )
        database_session.add(
            EmissaoEfluente(inventario_id=uuid4(), tipo_efluente="industrial", ano=2023)
        )
        await database_session.flush()

        result = await effluent_service.list_records(inventory_id, None, database_session)

        assert len(result) == 1
        assert result[0].inventario_id == inventory_id

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(
            EmissaoEfluente(organizacao_id=organization_id, tipo_efluente="domestico", ano=2023)
        )
        database_session.add(EmissaoEfluente(tipo_efluente="industrial", ano=2023))
        await database_session.flush()

        result = await effluent_service.list_records(None, organization_id, database_session)

        assert len(result) == 1
        assert result[0].organizacao_id == organization_id


class TestEffluentServiceGet:
    async def test_returns_record_when_found(self, database_session: AsyncSession):
        record = EmissaoEfluente(tipo_efluente="domestico", ano=2023)
        database_session.add(record)
        await database_session.flush()

        result = await effluent_service.get_record(record.id, database_session)

        assert result.id == record.id
        assert result.tipo_efluente == "domestico"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await effluent_service.get_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestEffluentServiceCreate:
    async def test_creates_record_without_calculation_when_data_is_incomplete(
        self, database_session: AsyncSession
    ):
        data = EmissaoEfluenteCreate(tipo_efluente="domestico", ano=2023)

        result = await effluent_service.create_record(data, database_session)

        assert result.id is not None
        assert result.tipo_efluente == "domestico"
        assert result.emissoes_ch4 is None
        assert result.emissoes_tco2e is None

    async def test_creates_record_with_calculation_when_all_required_data_provided(
        self, database_session: AsyncSession
    ):
        data = EmissaoEfluenteCreate(
            tipo_efluente="domestico",
            ano=2023,
            volume_efluente=1000.0,
            carga_organica_entrada=0.5,
            carga_organica_lodo=0.05,
            mcf_tratamento=0.1,
            nitrogenio_efluente=0.05,
        )

        result = await effluent_service.create_record(data, database_session)

        assert result.emissoes_ch4 is not None
        assert result.emissoes_ch4 >= 0
        assert result.emissoes_tco2e is not None

    async def test_creates_record_using_gwp_values_from_database(
        self, database_session: AsyncSession
    ):
        database_session.add(Gwp(nome_ghg="CH4", gwp_value=27.9))
        database_session.add(Gwp(nome_ghg="N2O", gwp_value=273.0))
        await database_session.flush()

        data = EmissaoEfluenteCreate(
            tipo_efluente="domestico",
            ano=2023,
            volume_efluente=1000.0,
            carga_organica_entrada=0.5,
            carga_organica_lodo=0.05,
            mcf_tratamento=0.1,
            nitrogenio_efluente=0.05,
        )

        result = await effluent_service.create_record(data, database_session)

        assert result.emissoes_tco2e is not None
        assert result.emissoes_tco2e > 0

    async def test_creates_record_with_treatment_factor_from_database(
        self, database_session: AsyncSession
    ):
        database_session.add(
            FatorTratamentoEfluente(
                tipo_tratamento="lagoa_anaerobia",
                tipo_efluente_aplicavel="domestico",
                categoria="anaerobic",
                mcf=0.8,
                fator_n2o_default=0.005,
            )
        )
        await database_session.flush()

        data = EmissaoEfluenteCreate(
            tipo_efluente="domestico",
            tipo_tratamento="lagoa_anaerobia",
            ano=2023,
        )

        result = await effluent_service.create_record(data, database_session)

        assert result.fator_n2o == 0.005


class TestEffluentServiceDelete:
    async def test_deletes_existing_record(self, database_session: AsyncSession):
        record = EmissaoEfluente(tipo_efluente="domestico", ano=2023)
        database_session.add(record)
        await database_session.flush()
        record_id = record.id

        await effluent_service.delete_record(record_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await effluent_service.get_record(record_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await effluent_service.delete_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestEffluentRoutes:
    async def test_list_returns_200(self, client):
        response = await client.get(f"/inventories/{uuid4()}/scope1/effluents")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_returns_201(self, client):
        payload = {"tipo_efluente": "domestico", "ano": 2023}

        response = await client.post(
            f"/inventories/{uuid4()}/scope1/effluents", json=payload
        )

        assert response.status_code == 201
        assert response.json()["tipo_efluente"] == "domestico"

    async def test_get_returns_200(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/effluents",
            json={"tipo_efluente": "industrial", "ano": 2023},
        )
        record_id = create_response.json()["id"]

        response = await client.get(
            f"/inventories/{inventory_id}/scope1/effluents/{record_id}"
        )

        assert response.status_code == 200

    async def test_get_returns_404_for_unknown_id(self, client):
        response = await client.get(
            f"/inventories/{uuid4()}/scope1/effluents/{uuid4()}"
        )

        assert response.status_code == 404

    async def test_delete_returns_204(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/effluents",
            json={"tipo_efluente": "domestico", "ano": 2023},
        )
        record_id = create_response.json()["id"]

        response = await client.delete(
            f"/inventories/{inventory_id}/scope1/effluents/{record_id}"
        )

        assert response.status_code == 204


class TestFugitiveServiceList:
    async def test_returns_empty_list_when_no_records(self, database_session: AsyncSession):
        result = await fugitive_service.list_records(None, database_session)

        assert result == []

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(
            EmissaoFugitiva(
                organizacao_id=organization_id,
                gas="SF6",
                quantidade=1.0,
                gwp_value=23500.0,
                emissoes_tco2e=23.5,
                ano=2023,
                mes=1,
            )
        )
        database_session.add(
            EmissaoFugitiva(
                gas="HFC-134a",
                quantidade=2.0,
                gwp_value=1430.0,
                emissoes_tco2e=2.86,
                ano=2023,
                mes=1,
            )
        )
        await database_session.flush()

        result = await fugitive_service.list_records(organization_id, database_session)

        assert len(result) == 1
        assert result[0].organizacao_id == organization_id


class TestFugitiveServiceGet:
    async def test_returns_record_when_found(self, database_session: AsyncSession):
        record = EmissaoFugitiva(
            gas="SF6", quantidade=1.0, gwp_value=23500.0, emissoes_tco2e=23.5, ano=2023, mes=1
        )
        database_session.add(record)
        await database_session.flush()

        result = await fugitive_service.get_record(record.id, database_session)

        assert result.id == record.id
        assert result.gas == "SF6"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await fugitive_service.get_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestFugitiveServiceCreate:
    async def test_creates_record_using_default_gwp_when_gas_not_in_database(
        self, database_session: AsyncSession
    ):
        data = EmissaoFugitivaCreate(gas="UnknownGas", quantidade=10.0, ano=2023, mes=1)

        result = await fugitive_service.create_record(data, database_session)

        assert result.id is not None
        assert result.gwp_value == 1.0
        assert result.emissoes_tco2e == pytest.approx(10.0 / 1000, rel=1e-6)

    async def test_creates_record_using_gwp_from_database(
        self, database_session: AsyncSession
    ):
        database_session.add(Gwp(nome_ghg="SF6", gwp_value=23500.0))
        await database_session.flush()

        data = EmissaoFugitivaCreate(gas="SF6", quantidade=1.0, ano=2023, mes=6)

        result = await fugitive_service.create_record(data, database_session)

        assert result.gwp_value == 23500.0
        assert result.emissoes_tco2e == pytest.approx(23.5, rel=1e-6)


class TestFugitiveServiceDelete:
    async def test_deletes_existing_record(self, database_session: AsyncSession):
        record = EmissaoFugitiva(
            gas="SF6", quantidade=1.0, gwp_value=23500.0, emissoes_tco2e=23.5, ano=2023, mes=1
        )
        database_session.add(record)
        await database_session.flush()
        record_id = record.id

        await fugitive_service.delete_record(record_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await fugitive_service.get_record(record_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await fugitive_service.delete_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestFugitiveRoutes:
    async def test_list_returns_200(self, client):
        response = await client.get(f"/inventories/{uuid4()}/scope1/fugitive")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_returns_201(self, client):
        payload = {"gas": "SF6", "quantidade": 1.0, "ano": 2023, "mes": 3}

        response = await client.post(
            f"/inventories/{uuid4()}/scope1/fugitive", json=payload
        )

        assert response.status_code == 201
        assert response.json()["gas"] == "SF6"

    async def test_get_returns_200(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/fugitive",
            json={"gas": "HFC-134a", "quantidade": 2.0, "ano": 2023, "mes": 1},
        )
        record_id = create_response.json()["id"]

        response = await client.get(
            f"/inventories/{inventory_id}/scope1/fugitive/{record_id}"
        )

        assert response.status_code == 200

    async def test_get_returns_404_for_unknown_id(self, client):
        response = await client.get(
            f"/inventories/{uuid4()}/scope1/fugitive/{uuid4()}"
        )

        assert response.status_code == 404

    async def test_delete_returns_204(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/fugitive",
            json={"gas": "SF6", "quantidade": 1.0, "ano": 2023, "mes": 1},
        )
        record_id = create_response.json()["id"]

        response = await client.delete(
            f"/inventories/{inventory_id}/scope1/fugitive/{record_id}"
        )

        assert response.status_code == 204


class TestMobileCombustionServiceList:
    async def test_returns_empty_list_when_no_records(self, database_session: AsyncSession):
        result = await mobile_combustion_service.list_records(None, None, database_session)

        assert result == []

    async def test_filters_by_inventory_id(self, database_session: AsyncSession):
        inventory_id = uuid4()
        database_session.add(
            EmissaoCombustaoMovel(
                inventario_id=inventory_id,
                metodo_calculo="combustivel",
                quantidade=100.0,
                unidade="L",
                ano=2023,
                mes=1,
            )
        )
        database_session.add(
            EmissaoCombustaoMovel(
                inventario_id=uuid4(),
                metodo_calculo="combustivel",
                quantidade=50.0,
                unidade="L",
                ano=2023,
                mes=2,
            )
        )
        await database_session.flush()

        result = await mobile_combustion_service.list_records(
            inventory_id, None, database_session
        )

        assert len(result) == 1
        assert result[0].inventario_id == inventory_id

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(
            EmissaoCombustaoMovel(
                organizacao_id=organization_id,
                metodo_calculo="combustivel",
                quantidade=100.0,
                unidade="L",
                ano=2023,
                mes=1,
            )
        )
        database_session.add(
            EmissaoCombustaoMovel(
                metodo_calculo="combustivel",
                quantidade=50.0,
                unidade="L",
                ano=2023,
                mes=1,
            )
        )
        await database_session.flush()

        result = await mobile_combustion_service.list_records(
            None, organization_id, database_session
        )

        assert len(result) == 1
        assert result[0].organizacao_id == organization_id


class TestMobileCombustionServiceGet:
    async def test_returns_record_when_found(self, database_session: AsyncSession):
        record = EmissaoCombustaoMovel(
            metodo_calculo="combustivel", quantidade=100.0, unidade="L", ano=2023, mes=1
        )
        database_session.add(record)
        await database_session.flush()

        result = await mobile_combustion_service.get_record(record.id, database_session)

        assert result.id == record.id
        assert result.metodo_calculo == "combustivel"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await mobile_combustion_service.get_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestMobileCombustionServiceCreate:
    async def test_creates_record_with_zero_emissions_when_no_factors_in_database(
        self, database_session: AsyncSession
    ):
        data = EmissaoCombustaoMovelCreate(
            metodo_calculo="combustivel",
            quantidade=100.0,
            unidade="L",
            ano=2023,
            mes=1,
        )

        result = await mobile_combustion_service.create_record(data, database_session)

        assert result.id is not None
        assert result.emissoes_co2 == 0.0
        assert result.emissoes_total_tco2e == 0.0

    async def test_creates_record_with_emissions_when_fossil_fuel_factor_found(
        self, database_session: AsyncSession
    ):
        database_session.add(
            FatorTipoCombustivel(
                combustivel="gasolina",
                ano_referencia=2020,
                fator_co2=69.3,
                fator_ch4=0.003,
                fator_n2o=0.0006,
            )
        )
        await database_session.flush()

        data = EmissaoCombustaoMovelCreate(
            metodo_calculo="combustivel",
            combustivel_fossil="gasolina",
            quantidade=100.0,
            quantidade_fossil=100.0,
            unidade="L",
            ano=2023,
            mes=1,
        )

        result = await mobile_combustion_service.create_record(data, database_session)

        assert result.emissoes_co2 is not None
        assert result.emissoes_co2 > 0
        assert result.fator_co2 == 69.3

    async def test_creates_record_with_biofuel_emissions_when_biofuel_factor_found(
        self, database_session: AsyncSession
    ):
        database_session.add(
            FatorTipoCombustivel(
                combustivel="etanol",
                ano_referencia=2020,
                fator_co2=0.0,
                fator_ch4=0.001,
                fator_n2o=0.0003,
            )
        )
        await database_session.flush()

        data = EmissaoCombustaoMovelCreate(
            metodo_calculo="combustivel",
            biocombustivel="etanol",
            quantidade=50.0,
            quantidade_biocombustivel=50.0,
            unidade="L",
            ano=2023,
            mes=3,
        )

        result = await mobile_combustion_service.create_record(data, database_session)

        assert result.id is not None


class TestMobileCombustionServiceDelete:
    async def test_deletes_existing_record(self, database_session: AsyncSession):
        record = EmissaoCombustaoMovel(
            metodo_calculo="combustivel", quantidade=100.0, unidade="L", ano=2023, mes=1
        )
        database_session.add(record)
        await database_session.flush()
        record_id = record.id

        await mobile_combustion_service.delete_record(record_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await mobile_combustion_service.get_record(record_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await mobile_combustion_service.delete_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestMobileCombustionRoutes:
    async def test_list_returns_200(self, client):
        response = await client.get(f"/inventories/{uuid4()}/scope1/mobile-combustion")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_returns_201(self, client):
        payload = {
            "metodo_calculo": "combustivel",
            "quantidade": 100.0,
            "unidade": "L",
            "ano": 2023,
            "mes": 1,
        }

        response = await client.post(
            f"/inventories/{uuid4()}/scope1/mobile-combustion", json=payload
        )

        assert response.status_code == 201
        assert response.json()["metodo_calculo"] == "combustivel"

    async def test_get_returns_200(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/mobile-combustion",
            json={
                "metodo_calculo": "distancia",
                "quantidade": 50.0,
                "unidade": "km",
                "ano": 2023,
                "mes": 2,
            },
        )
        record_id = create_response.json()["id"]

        response = await client.get(
            f"/inventories/{inventory_id}/scope1/mobile-combustion/{record_id}"
        )

        assert response.status_code == 200

    async def test_get_returns_404_for_unknown_id(self, client):
        response = await client.get(
            f"/inventories/{uuid4()}/scope1/mobile-combustion/{uuid4()}"
        )

        assert response.status_code == 404

    async def test_delete_returns_204(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/mobile-combustion",
            json={
                "metodo_calculo": "combustivel",
                "quantidade": 100.0,
                "unidade": "L",
                "ano": 2023,
                "mes": 1,
            },
        )
        record_id = create_response.json()["id"]

        response = await client.delete(
            f"/inventories/{inventory_id}/scope1/mobile-combustion/{record_id}"
        )

        assert response.status_code == 204


class TestStationaryCombustionServiceList:
    async def test_returns_empty_list_when_no_records(self, database_session: AsyncSession):
        result = await stationary_combustion_service.list_records(None, database_session)

        assert result == []

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_id = uuid4()
        database_session.add(
            EmissaoEstacionaria(
                organizacao_id=organization_id,
                combustivel="gasolina",
                quantidade=100.0,
                unidade="L",
                ano=2023,
                mes=1,
            )
        )
        database_session.add(
            EmissaoEstacionaria(
                combustivel="diesel",
                quantidade=50.0,
                unidade="L",
                ano=2023,
                mes=1,
            )
        )
        await database_session.flush()

        result = await stationary_combustion_service.list_records(
            organization_id, database_session
        )

        assert len(result) == 1
        assert result[0].organizacao_id == organization_id


class TestStationaryCombustionServiceGet:
    async def test_returns_record_when_found(self, database_session: AsyncSession):
        record = EmissaoEstacionaria(
            combustivel="gas_natural", quantidade=100.0, unidade="m3", ano=2023, mes=1
        )
        database_session.add(record)
        await database_session.flush()

        result = await stationary_combustion_service.get_record(record.id, database_session)

        assert result.id == record.id
        assert result.combustivel == "gas_natural"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await stationary_combustion_service.get_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestStationaryCombustionServiceCreate:
    async def test_creates_record_without_fossil_fuel_factor(
        self, database_session: AsyncSession
    ):
        data = EmissaoEstacionariaCreate(
            combustivel="lenha",
            quantidade=500.0,
            unidade="kg",
            ano=2023,
            mes=3,
        )

        result = await stationary_combustion_service.create_record(data, database_session)

        assert result.id is not None
        assert result.combustivel == "lenha"
        assert result.emissoes_co2 == 0.0

    async def test_creates_record_with_emission_factors_from_database(
        self, database_session: AsyncSession
    ):
        database_session.add(
            FatorEstacionaria(
                combustivel="gas_natural",
                unidade="m3",
                co2=2.03,
                ch4_energia=0.000005,
                n2o_energia=0.0000001,
            )
        )
        await database_session.flush()

        data = EmissaoEstacionariaCreate(
            combustivel="gas_natural",
            combustivel_fossil="gas_natural",
            quantidade_fossil=1000.0,
            quantidade=1000.0,
            unidade="m3",
            ano=2023,
            mes=1,
        )

        result = await stationary_combustion_service.create_record(data, database_session)

        assert result.emissoes_co2 is not None
        assert result.emissoes_co2 > 0
        assert result.fator_co2 == 2.03


class TestStationaryCombustionServiceDelete:
    async def test_deletes_existing_record(self, database_session: AsyncSession):
        record = EmissaoEstacionaria(
            combustivel="diesel", quantidade=100.0, unidade="L", ano=2023, mes=1
        )
        database_session.add(record)
        await database_session.flush()
        record_id = record.id

        await stationary_combustion_service.delete_record(record_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await stationary_combustion_service.get_record(record_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await stationary_combustion_service.delete_record(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestStationaryCombustionRoutes:
    async def test_list_returns_200(self, client):
        response = await client.get(f"/inventories/{uuid4()}/scope1/stationary-combustion")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_returns_201(self, client):
        payload = {
            "combustivel": "gas_natural",
            "quantidade": 100.0,
            "unidade": "m3",
            "ano": 2023,
            "mes": 1,
        }

        response = await client.post(
            f"/inventories/{uuid4()}/scope1/stationary-combustion", json=payload
        )

        assert response.status_code == 201
        assert response.json()["combustivel"] == "gas_natural"

    async def test_get_returns_200(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/stationary-combustion",
            json={"combustivel": "diesel", "quantidade": 50.0, "unidade": "L", "ano": 2023, "mes": 2},
        )
        record_id = create_response.json()["id"]

        response = await client.get(
            f"/inventories/{inventory_id}/scope1/stationary-combustion/{record_id}"
        )

        assert response.status_code == 200

    async def test_get_returns_404_for_unknown_id(self, client):
        response = await client.get(
            f"/inventories/{uuid4()}/scope1/stationary-combustion/{uuid4()}"
        )

        assert response.status_code == 404

    async def test_delete_returns_204(self, client):
        inventory_id = uuid4()
        create_response = await client.post(
            f"/inventories/{inventory_id}/scope1/stationary-combustion",
            json={
                "combustivel": "gas_natural",
                "quantidade": 100.0,
                "unidade": "m3",
                "ano": 2023,
                "mes": 1,
            },
        )
        record_id = create_response.json()["id"]

        response = await client.delete(
            f"/inventories/{inventory_id}/scope1/stationary-combustion/{record_id}"
        )

        assert response.status_code == 204
