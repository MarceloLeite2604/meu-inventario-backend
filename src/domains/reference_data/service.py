from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...util.logger import retrieve_logger
from .models import (
    AeroportoCoordenada,
    EquivalenciaVeiculo,
    FatorEmissaoAerea,
    FatorEmissaoEnergia,
    FatorEstacionaria,
    FatorFrotaTipoCombustivel,
    FatorTipoCombustivel,
    FatorTratamentoEfluente,
    FatorTransporteOnibus,
    Gwp,
)

_LOGGER = retrieve_logger(__name__)


async def list_fuel_type_factors(session: AsyncSession) -> list[FatorTipoCombustivel]:
    _LOGGER.info("Listing fuel type emission factors")
    result = await session.execute(
        select(FatorTipoCombustivel).order_by(
            FatorTipoCombustivel.combustivel, FatorTipoCombustivel.ano_referencia))
    return list(result.scalars().all())


async def list_fleet_fuel_factors(session: AsyncSession) -> list[FatorFrotaTipoCombustivel]:
    _LOGGER.info("Listing fleet fuel emission factors")
    result = await session.execute(
        select(FatorFrotaTipoCombustivel).order_by(
            FatorFrotaTipoCombustivel.tipo_veiculo, FatorFrotaTipoCombustivel.combustivel))
    return list(result.scalars().all())


async def list_stationary_factors(session: AsyncSession) -> list[FatorEstacionaria]:
    _LOGGER.info("Listing stationary combustion factors")
    result = await session.execute(
        select(FatorEstacionaria).order_by(FatorEstacionaria.combustivel))
    return list(result.scalars().all())


async def list_energy_factors(
    ano: int | None, session: AsyncSession
) -> list[FatorEmissaoEnergia]:
    _LOGGER.info("Listing energy emission factors for year %s", ano)
    query = select(FatorEmissaoEnergia)
    if ano:
        query = query.where(FatorEmissaoEnergia.ano == ano)
    result = await session.execute(query.order_by(FatorEmissaoEnergia.ano, FatorEmissaoEnergia.mes))
    return list(result.scalars().all())


async def list_aerial_factors(session: AsyncSession) -> list[FatorEmissaoAerea]:
    _LOGGER.info("Listing aerial emission factors")
    result = await session.execute(
        select(FatorEmissaoAerea).order_by(
            FatorEmissaoAerea.ano_referencia, FatorEmissaoAerea.distancia_aerea))
    return list(result.scalars().all())


async def list_bus_factors(session: AsyncSession) -> list[FatorTransporteOnibus]:
    _LOGGER.info("Listing bus emission factors")
    result = await session.execute(
        select(FatorTransporteOnibus).order_by(
            FatorTransporteOnibus.ano, FatorTransporteOnibus.tipo_onibus))
    return list(result.scalars().all())


async def list_effluent_treatment_factors(
    session: AsyncSession,
) -> list[FatorTratamentoEfluente]:
    _LOGGER.info("Listing effluent treatment factors")
    result = await session.execute(
        select(FatorTratamentoEfluente).order_by(FatorTratamentoEfluente.tipo_tratamento))
    return list(result.scalars().all())


async def list_gwp(session: AsyncSession) -> list[Gwp]:
    _LOGGER.info("Listing global warming potentials")
    result = await session.execute(select(Gwp).order_by(Gwp.nome_ghg))
    return list(result.scalars().all())


async def list_airports(search_query: str | None, session: AsyncSession) -> list[AeroportoCoordenada]:
    _LOGGER.info("Listing airports with search filter %s", search_query)
    stmt = select(AeroportoCoordenada)
    if search_query:
        search_term = f"%{search_query.upper()}%"
        stmt = stmt.where(
            AeroportoCoordenada.sigla.ilike(search_term) | AeroportoCoordenada.nome.ilike(search_term)
        )
    result = await session.execute(stmt.order_by(AeroportoCoordenada.sigla).limit(50))
    return list(result.scalars().all())


async def list_vehicle_equivalences(session: AsyncSession) -> list[EquivalenciaVeiculo]:
    _LOGGER.info("Listing vehicle equivalences")
    result = await session.execute(
        select(EquivalenciaVeiculo).order_by(EquivalenciaVeiculo.transporte))
    return list(result.scalars().all())
