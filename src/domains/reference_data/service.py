from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


async def list_fuel_type_factors(session: AsyncSession) -> list[FatorTipoCombustivel]:
    result = await session.execute(
        select(FatorTipoCombustivel).order_by(
            FatorTipoCombustivel.combustivel, FatorTipoCombustivel.ano_referencia))
    return list(result.scalars().all())


async def list_fleet_fuel_factors(session: AsyncSession) -> list[FatorFrotaTipoCombustivel]:
    result = await session.execute(
        select(FatorFrotaTipoCombustivel).order_by(
            FatorFrotaTipoCombustivel.tipo_veiculo, FatorFrotaTipoCombustivel.combustivel))
    return list(result.scalars().all())


async def list_stationary_factors(session: AsyncSession) -> list[FatorEstacionaria]:
    result = await session.execute(
        select(FatorEstacionaria).order_by(FatorEstacionaria.combustivel))
    return list(result.scalars().all())


async def list_energy_factors(
    ano: int | None, session: AsyncSession
) -> list[FatorEmissaoEnergia]:
    query = select(FatorEmissaoEnergia)
    if ano:
        query = query.where(FatorEmissaoEnergia.ano == ano)
    result = await session.execute(query.order_by(FatorEmissaoEnergia.ano, FatorEmissaoEnergia.mes))
    return list(result.scalars().all())


async def list_aerial_factors(session: AsyncSession) -> list[FatorEmissaoAerea]:
    result = await session.execute(
        select(FatorEmissaoAerea).order_by(
            FatorEmissaoAerea.ano_referencia, FatorEmissaoAerea.distancia_aerea))
    return list(result.scalars().all())


async def list_bus_factors(session: AsyncSession) -> list[FatorTransporteOnibus]:
    result = await session.execute(
        select(FatorTransporteOnibus).order_by(
            FatorTransporteOnibus.ano, FatorTransporteOnibus.tipo_onibus))
    return list(result.scalars().all())


async def list_effluent_treatment_factors(
    session: AsyncSession,
) -> list[FatorTratamentoEfluente]:
    result = await session.execute(
        select(FatorTratamentoEfluente).order_by(FatorTratamentoEfluente.tipo_tratamento))
    return list(result.scalars().all())


async def list_gwp(session: AsyncSession) -> list[Gwp]:
    result = await session.execute(select(Gwp).order_by(Gwp.nome_ghg))
    return list(result.scalars().all())


async def list_airports(query: str | None, session: AsyncSession) -> list[AeroportoCoordenada]:
    stmt = select(AeroportoCoordenada)
    if query:
        q = f"%{query.upper()}%"
        stmt = stmt.where(
            AeroportoCoordenada.sigla.ilike(q) | AeroportoCoordenada.nome.ilike(q)
        )
    result = await session.execute(stmt.order_by(AeroportoCoordenada.sigla).limit(50))
    return list(result.scalars().all())


async def list_vehicle_equivalences(session: AsyncSession) -> list[EquivalenciaVeiculo]:
    result = await session.execute(
        select(EquivalenciaVeiculo).order_by(EquivalenciaVeiculo.transporte))
    return list(result.scalars().all())
