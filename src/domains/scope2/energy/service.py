from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import FatorEmissaoEnergia
from ....util.logger import retrieve_logger
from .calculations import calculate
from .models import ConsumoEnergia, EvidenciaConsumoEnergia, UnidadeConsumidora
from .schemas import (
    ConsumoEnergiaCreate,
    EvidenciaConsumoEnergiaCreate,
    UnidadeConsumidoraCreate,
)

_LOGGER = retrieve_logger(__name__)


async def list_consumer_units(
    organizacao_id: UUID | str, session: AsyncSession
) -> list[UnidadeConsumidora]:
    _LOGGER.info("Listing consumer units for organization %s", organizacao_id)
    result = await session.execute(
        select(UnidadeConsumidora).where(
            UnidadeConsumidora.organizacao_id == organizacao_id))
    return list(result.scalars().all())


async def create_consumer_unit(
    data: UnidadeConsumidoraCreate, session: AsyncSession
) -> UnidadeConsumidora:
    _LOGGER.info("Creating consumer unit for organization %s", data.organizacao_id)
    unit = UnidadeConsumidora(**data.model_dump())
    session.add(unit)
    await session.flush()
    await session.refresh(unit)
    return unit


async def list_consumption_records(
    inventario_id: UUID | None, organizacao_id: UUID | None, session: AsyncSession
) -> list[ConsumoEnergia]:
    _LOGGER.info("Listing energy consumption records for inventory %s", inventario_id)
    query = select(ConsumoEnergia)
    if organizacao_id:
        query = query.where(ConsumoEnergia.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(ConsumoEnergia.created_at.desc()))
    return list(result.scalars().all())


async def get_consumption_record(record_id: UUID, session: AsyncSession) -> ConsumoEnergia:
    _LOGGER.info("Retrieving energy consumption record %s", record_id)
    result = await session.execute(
        select(ConsumoEnergia).where(ConsumoEnergia.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        _LOGGER.warning("Energy consumption record %s not found", record_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def create_consumption_record(
    data: ConsumoEnergiaCreate, session: AsyncSession
) -> ConsumoEnergia:
    _LOGGER.info("Creating energy consumption record for organization %s", data.organizacao_id)
    factor_result = await session.execute(
        select(FatorEmissaoEnergia).where(
            FatorEmissaoEnergia.ano == data.ano,
            FatorEmissaoEnergia.mes == data.mes,
        ))
    factor_row = factor_result.scalar_one_or_none()
    if not factor_row:
        _LOGGER.warning(
            "No energy emission factor found for year %s month %s", data.ano, data.mes
        )
    emissoes = calculate(data.consumo_mwh, factor_row.fator_emissao) if factor_row else None

    record = ConsumoEnergia(**data.model_dump(), emissoes_energia_tco2e=emissoes)
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def delete_consumption_record(record_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting energy consumption record %s", record_id)
    record = await get_consumption_record(record_id, session)
    await session.delete(record)


async def reprocess_emissions(session: AsyncSession) -> int:
    _LOGGER.info("Reprocessing energy emission records with missing emissions")
    result = await session.execute(
        select(ConsumoEnergia).where(ConsumoEnergia.emissoes_energia_tco2e.is_(None))
    )
    records = list(result.scalars().all())
    count = 0
    for record in records:
        factor_result = await session.execute(
            select(FatorEmissaoEnergia).where(
                FatorEmissaoEnergia.ano == record.ano,
                FatorEmissaoEnergia.mes == record.mes,
            )
        )
        factor = factor_result.scalar_one_or_none()
        if factor:
            record.emissoes_energia_tco2e = calculate(record.consumo_mwh, factor.fator_emissao)
            count += 1
    await session.flush()
    _LOGGER.info("Reprocessed %d energy emission records", count)
    return count


async def add_evidence(
    consumo_id: UUID,
    organizacao_id: UUID | str,
    data: EvidenciaConsumoEnergiaCreate,
    uploaded_by: str,
    session: AsyncSession,
) -> EvidenciaConsumoEnergia:
    _LOGGER.info("Adding evidence to energy consumption record %s", consumo_id)
    evidence = EvidenciaConsumoEnergia(
        consumo_energia_id=consumo_id,
        organizacao_id=organizacao_id,
        uploaded_by=uploaded_by,
        **data.model_dump(),
    )
    session.add(evidence)
    await session.flush()
    await session.refresh(evidence)
    return evidence
