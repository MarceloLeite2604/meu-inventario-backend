from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import Gwp
from ....util.logger import retrieve_logger
from .calculations import calculate
from .models import EmissaoFugitiva
from .schemas import EmissaoFugitivaCreate

_LOGGER = retrieve_logger(__name__)


async def list_records(organizacao_id: UUID | None, session: AsyncSession) -> list[EmissaoFugitiva]:
    _LOGGER.info("Listing fugitive emission records for organization %s", organizacao_id)
    query = select(EmissaoFugitiva)
    if organizacao_id:
        query = query.where(EmissaoFugitiva.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(EmissaoFugitiva.created_at.desc()))
    return list(result.scalars().all())


async def get_record(record_id: UUID, session: AsyncSession) -> EmissaoFugitiva:
    _LOGGER.info("Retrieving fugitive emission record %s", record_id)
    result = await session.execute(
        select(EmissaoFugitiva).where(EmissaoFugitiva.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        _LOGGER.warning("Fugitive emission record %s not found", record_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def create_record(
    data: EmissaoFugitivaCreate, session: AsyncSession
) -> EmissaoFugitiva:
    _LOGGER.info("Creating fugitive emission record for gas %s, organization %s", data.gas, data.organizacao_id)
    gwp_result = await session.execute(select(Gwp).where(Gwp.nome_ghg == data.gas))
    gwp_row = gwp_result.scalar_one_or_none()
    gwp_value = gwp_row.gwp_value if gwp_row else 1.0

    emissoes_tco2e = calculate(data.quantidade, gwp_value)

    record = EmissaoFugitiva(
        **data.model_dump(),
        gwp_value=gwp_value,
        emissoes_tco2e=emissoes_tco2e,
    )
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def delete_record(record_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting fugitive emission record %s", record_id)
    record = await get_record(record_id, session)
    await session.delete(record)
