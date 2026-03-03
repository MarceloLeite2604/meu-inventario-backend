from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import FatorTipoCombustivel, Gwp
from ....util.logger import retrieve_logger
from .calculations import EmissionFactors, calculate
from .models import EmissaoCombustaoMovel
from .schemas import EmissaoCombustaoMovelCreate

_LOGGER = retrieve_logger(__name__)


async def _get_factors(
    combustivel_fossil: str | None,
    biocombustivel: str | None,
    ano: int,
    session: AsyncSession,
) -> EmissionFactors:
    fator_co2 = fator_ch4 = fator_n2o = 0.0

    if combustivel_fossil:
        result = await session.execute(
            select(FatorTipoCombustivel).where(
                FatorTipoCombustivel.combustivel == combustivel_fossil,
                FatorTipoCombustivel.ano_referencia <= ano,
            ).order_by(FatorTipoCombustivel.ano_referencia.desc()).limit(1))
        factor_row = result.scalar_one_or_none()
        if factor_row:
            fator_co2 = factor_row.fator_co2 or 0.0
            fator_ch4 = factor_row.fator_ch4 or 0.0
            fator_n2o = factor_row.fator_n2o or 0.0

    fator_co2_bio = fator_ch4_bio = fator_n2o_bio = 0.0
    if biocombustivel:
        result = await session.execute(
            select(FatorTipoCombustivel).where(
                FatorTipoCombustivel.combustivel == biocombustivel,
                FatorTipoCombustivel.ano_referencia <= ano,
            ).order_by(FatorTipoCombustivel.ano_referencia.desc()).limit(1))
        bio_factor = result.scalar_one_or_none()
        if bio_factor:
            fator_co2_bio = bio_factor.fator_co2 or 0.0
            fator_ch4_bio = bio_factor.fator_ch4 or 0.0
            fator_n2o_bio = bio_factor.fator_n2o or 0.0

    return EmissionFactors(
        fator_co2=fator_co2,
        fator_ch4=fator_ch4,
        fator_n2o=fator_n2o,
        fator_co2_bio=fator_co2_bio,
        fator_ch4_bio=fator_ch4_bio,
        fator_n2o_bio=fator_n2o_bio,
    )


async def _get_gwp(gas: str, session: AsyncSession) -> float:
    result = await session.execute(select(Gwp).where(Gwp.nome_ghg == gas))
    row = result.scalar_one_or_none()
    return row.gwp_value if row else 1.0


async def list_records(
    inventario_id: UUID | None, organizacao_id: UUID | None, session: AsyncSession
) -> list[EmissaoCombustaoMovel]:
    _LOGGER.info("Listing mobile combustion records for inventory %s", inventario_id)
    query = select(EmissaoCombustaoMovel)
    if inventario_id:
        query = query.where(EmissaoCombustaoMovel.inventario_id == inventario_id)
    if organizacao_id:
        query = query.where(EmissaoCombustaoMovel.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(EmissaoCombustaoMovel.created_at.desc()))
    return list(result.scalars().all())


async def get_record(record_id: UUID, session: AsyncSession) -> EmissaoCombustaoMovel:
    _LOGGER.info("Retrieving mobile combustion record %s", record_id)
    result = await session.execute(
        select(EmissaoCombustaoMovel).where(EmissaoCombustaoMovel.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        _LOGGER.warning("Mobile combustion record %s not found", record_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def create_record(
    data: EmissaoCombustaoMovelCreate, session: AsyncSession
) -> EmissaoCombustaoMovel:
    _LOGGER.info("Creating mobile combustion record for organization %s", data.organizacao_id)
    gwp_ch4 = await _get_gwp("CH4", session)
    gwp_n2o = await _get_gwp("N2O", session)

    factors = await _get_factors(
        data.combustivel_fossil, data.biocombustivel, data.ano, session)

    quantidade_fossil = data.quantidade_fossil or 0.0
    quantidade_bio = data.quantidade_biocombustivel or 0.0

    result = calculate(quantidade_fossil, quantidade_bio, factors, gwp_ch4, gwp_n2o)

    record = EmissaoCombustaoMovel(
        **data.model_dump(),
        emissoes_co2=result.emissoes_co2,
        emissoes_ch4=result.emissoes_ch4,
        emissoes_n2o=result.emissoes_n2o,
        emissoes_co2_biogenico=result.emissoes_co2_biogenico,
        emissoes_ch4_biogenico=result.emissoes_ch4_biogenico,
        emissoes_n2o_biogenico=result.emissoes_n2o_biogenico,
        emissoes_total_tco2e=result.emissoes_total_tco2e,
        fator_co2=factors.fator_co2,
        fator_ch4=factors.fator_ch4,
        fator_n2o=factors.fator_n2o,
    )
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def delete_record(record_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting mobile combustion record %s", record_id)
    record = await get_record(record_id, session)
    await session.delete(record)
