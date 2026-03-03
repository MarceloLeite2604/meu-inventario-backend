from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import FatorEstacionaria, Gwp
from ....util.logger import retrieve_logger
from .calculations import calculate
from .models import EmissaoEstacionaria
from .schemas import EmissaoEstacionariaCreate

_LOGGER = retrieve_logger(__name__)


async def _get_gwp(gas: str, session: AsyncSession) -> float:
    result = await session.execute(select(Gwp).where(Gwp.nome_ghg == gas))
    row = result.scalar_one_or_none()
    return row.gwp_value if row else 1.0


async def list_records(organizacao_id: UUID | None, session: AsyncSession) -> list[EmissaoEstacionaria]:
    _LOGGER.info("Listing stationary combustion records for organization %s", organizacao_id)
    query = select(EmissaoEstacionaria)
    if organizacao_id:
        query = query.where(EmissaoEstacionaria.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(EmissaoEstacionaria.created_at.desc()))
    return list(result.scalars().all())


async def get_record(record_id: UUID, session: AsyncSession) -> EmissaoEstacionaria:
    _LOGGER.info("Retrieving stationary combustion record %s", record_id)
    result = await session.execute(
        select(EmissaoEstacionaria).where(EmissaoEstacionaria.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        _LOGGER.warning("Stationary combustion record %s not found", record_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def create_record(
    data: EmissaoEstacionariaCreate, session: AsyncSession
) -> EmissaoEstacionaria:
    _LOGGER.info("Creating stationary combustion record for organization %s", data.organizacao_id)
    gwp_ch4 = await _get_gwp("CH4", session)
    gwp_n2o = await _get_gwp("N2O", session)

    fator_co2 = fator_ch4 = fator_n2o = 0.0
    if data.combustivel_fossil:
        result = await session.execute(
            select(FatorEstacionaria).where(
                FatorEstacionaria.combustivel == data.combustivel_fossil))
        factor = result.scalar_one_or_none()
        if factor:
            fator_co2 = factor.co2 or 0.0
            fator_ch4 = factor.ch4_energia or 0.0
            fator_n2o = factor.n2o_energia or 0.0

    result = calculate(
        data.quantidade_fossil or 0.0,
        data.quantidade_biocombustivel or 0.0,
        fator_co2, fator_ch4, fator_n2o,
        gwp_ch4=gwp_ch4, gwp_n2o=gwp_n2o,
    )

    record = EmissaoEstacionaria(
        **data.model_dump(),
        emissoes_co2=result.emissoes_co2,
        emissoes_ch4=result.emissoes_ch4,
        emissoes_n2o=result.emissoes_n2o,
        emissoes_co2_biogenico=result.emissoes_co2_biogenico,
        emissoes_ch4_biogenico=result.emissoes_ch4_biogenico,
        emissoes_n2o_biogenico=result.emissoes_n2o_biogenico,
        emissoes_total_tco2e=result.emissoes_total_tco2e,
        fator_co2=fator_co2,
        fator_ch4=fator_ch4,
        fator_n2o=fator_n2o,
    )
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def delete_record(record_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting stationary combustion record %s", record_id)
    record = await get_record(record_id, session)
    await session.delete(record)
