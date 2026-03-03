from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import AeroportoCoordenada, FatorEmissaoAerea, FatorTransporteOnibus, TransporteMetro, TransporteTrem
from ....util.logger import retrieve_logger
from .calculations import (
    AirEmissions,
    GroundEmissions,
    calculate_air,
    calculate_ground,
    classify_haul,
    haversine_km,
)
from .models import Deslocamento, EmissaoViagemNegocio
from .schemas import DeslocamentoCreate, EmissaoViagemNegocioCreate

_LOGGER = retrieve_logger(__name__)


async def list_records(
    inventario_id: UUID | None, organizacao_id: UUID | None, session: AsyncSession
) -> list[EmissaoViagemNegocio]:
    _LOGGER.info("Listing business travel records for inventory %s", inventario_id)
    query = select(EmissaoViagemNegocio)
    if organizacao_id:
        query = query.where(EmissaoViagemNegocio.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(EmissaoViagemNegocio.created_at.desc()))
    return list(result.scalars().all())


async def get_record(record_id: UUID, session: AsyncSession) -> EmissaoViagemNegocio:
    _LOGGER.info("Retrieving business travel record %s", record_id)
    result = await session.execute(
        select(EmissaoViagemNegocio).where(EmissaoViagemNegocio.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        _LOGGER.warning("Business travel record %s not found", record_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def _get_airport(code: str, session: AsyncSession) -> AeroportoCoordenada:
    result = await session.execute(
        select(AeroportoCoordenada).where(AeroportoCoordenada.sigla == code.upper()))
    airport = result.scalar_one_or_none()
    if not airport:
        _LOGGER.warning("Airport not found: %s", code)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Airport not found: {code}",
        )
    return airport


async def _calculate_air_emissions(
    data: EmissaoViagemNegocioCreate, session: AsyncSession
) -> dict:
    if not data.origin or not data.destination:
        return {}

    origin = await _get_airport(data.origin, session)
    destination = await _get_airport(data.destination, session)

    distance_km = haversine_km(origin.latitude, origin.longitude, destination.latitude, destination.longitude)
    haul = classify_haul(distance_km)

    factor_result = await session.execute(
        select(FatorEmissaoAerea).where(
            FatorEmissaoAerea.distancia_aerea == haul,
            FatorEmissaoAerea.ano_referencia == data.ano,
        ))
    factor = factor_result.scalar_one_or_none()
    if not factor:
        return {"distance": distance_km}

    passengers = data.quantidade_passageiros or 1
    round_trip = data.round_trip or False

    emissions: AirEmissions = calculate_air(
        distance_km=distance_km,
        round_trip=round_trip,
        passengers=passengers,
        co2_per_pkm=factor.co2_aereo_passageiro_km,
        ch4_per_pkm=factor.ch4_aereo_passageiro_km,
        n2o_per_pkm=factor.n2o_aereo_passageiro_km,
        route_factor=factor.acrescimo_rota,
    )

    return {
        "distance": distance_km,
        "emissoes_aerea_co2": emissions.co2_tco2,
        "emissoes_aerea_ch4": emissions.ch4_tco2e,
        "emissoes_aerea_n2o": emissions.n2o_tco2e,
        "emissoes_tco2e_total": emissions.total_tco2e,
        "fator_co2": factor.co2_aereo_passageiro_km,
        "fator_ch4": factor.ch4_aereo_passageiro_km,
        "fator_n2o": factor.n2o_aereo_passageiro_km,
    }


async def _calculate_bus_emissions(
    data: EmissaoViagemNegocioCreate, session: AsyncSession
) -> dict:
    if not data.distance:
        return {}

    factor_result = await session.execute(
        select(FatorTransporteOnibus).where(
            FatorTransporteOnibus.tipo_onibus == (data.tipo_onibus or "urbano"),
            FatorTransporteOnibus.ano == data.ano,
        ))
    factor = factor_result.scalar_one_or_none()
    if not factor:
        return {}

    passengers = data.quantidade_passageiros or 1
    round_trip = data.round_trip or False
    co2 = factor.diesel_co2_pkm or 0.0
    ch4 = factor.diesel_ch4_pkm or 0.0
    n2o = factor.diesel_n2o_pkm or 0.0

    emissions: GroundEmissions = calculate_ground(
        distance_km=data.distance,
        round_trip=round_trip,
        passengers=passengers,
        co2_per_pkm=co2,
        ch4_per_pkm=ch4,
        n2o_per_pkm=n2o,
    )

    return {
        "emissoes_co2": emissions.co2_tco2,
        "emissoes_ch4": emissions.ch4_tco2e,
        "emissoes_n2o": emissions.n2o_tco2e,
        "emissoes_tco2e_total": emissions.total_tco2e,
        "fator_co2": co2,
        "fator_ch4": ch4,
        "fator_n2o": n2o,
    }


async def _calculate_metro_emissions(
    data: EmissaoViagemNegocioCreate, session: AsyncSession
) -> dict:
    if not data.distance:
        return {}

    factor_result = await session.execute(
        select(TransporteMetro).where(TransporteMetro.ano == data.ano))
    factor = factor_result.scalar_one_or_none()
    if not factor:
        return {}

    passengers = data.quantidade_passageiros or 1
    round_trip = data.round_trip or False
    co2_per_pkm = factor.g_co2_passageiro_km / 1_000_000

    emissions: GroundEmissions = calculate_ground(
        distance_km=data.distance,
        round_trip=round_trip,
        passengers=passengers,
        co2_per_pkm=co2_per_pkm,
        ch4_per_pkm=0.0,
        n2o_per_pkm=0.0,
    )

    return {
        "emissoes_co2": emissions.co2_tco2,
        "emissoes_tco2e_total": emissions.total_tco2e,
        "fator_co2": co2_per_pkm,
    }


async def _calculate_train_emissions(
    data: EmissaoViagemNegocioCreate, session: AsyncSession
) -> dict:
    if not data.distance:
        return {}

    factor_result = await session.execute(
        select(TransporteTrem).where(TransporteTrem.ano == data.ano))
    factor = factor_result.scalar_one_or_none()
    if not factor:
        return {}

    passengers = data.quantidade_passageiros or 1
    round_trip = data.round_trip or False
    co2_per_pkm = factor.g_co2_passageiro_km / 1_000_000

    emissions: GroundEmissions = calculate_ground(
        distance_km=data.distance,
        round_trip=round_trip,
        passengers=passengers,
        co2_per_pkm=co2_per_pkm,
        ch4_per_pkm=0.0,
        n2o_per_pkm=0.0,
    )

    return {
        "emissoes_co2": emissions.co2_tco2,
        "emissoes_tco2e_total": emissions.total_tco2e,
        "fator_co2": co2_per_pkm,
    }


async def create_record(
    data: EmissaoViagemNegocioCreate, session: AsyncSession
) -> EmissaoViagemNegocio:
    _LOGGER.info("Creating business travel record with transport type %s", data.tipo_transporte)
    transport = data.tipo_transporte.lower()
    calculated: dict = {}

    if transport == "aereo":
        calculated = await _calculate_air_emissions(data, session)
    elif transport == "onibus":
        calculated = await _calculate_bus_emissions(data, session)
    elif transport == "metro":
        calculated = await _calculate_metro_emissions(data, session)
    elif transport == "trem":
        calculated = await _calculate_train_emissions(data, session)

    record_data = data.model_dump()
    if "distance" in calculated:
        record_data["distance"] = calculated.pop("distance")
    record_data.update(calculated)

    record = EmissaoViagemNegocio(**record_data)
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def delete_record(record_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting business travel record %s", record_id)
    record = await get_record(record_id, session)
    await session.delete(record)


async def list_displacements(
    organizacao_id: UUID | None, session: AsyncSession
) -> list[Deslocamento]:
    _LOGGER.info("Listing displacements for organization %s", organizacao_id)
    query = select(Deslocamento)
    if organizacao_id:
        query = query.where(Deslocamento.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(Deslocamento.created_at.desc()))
    return list(result.scalars().all())


async def create_displacement(
    data: DeslocamentoCreate, session: AsyncSession
) -> Deslocamento:
    _LOGGER.info("Creating displacement for organization %s", data.organizacao_id)
    record = Deslocamento(**data.model_dump())
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record
