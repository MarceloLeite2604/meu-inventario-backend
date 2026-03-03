from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import FatorEmissaoEnergia
from .calculations import calculate
from .models import ConsumoEnergia, EvidenciaConsumoEnergia, UnidadeConsumidora
from .schemas import (
    ConsumoEnergiaCreate,
    EvidenciaConsumoEnergiaCreate,
    UnidadeConsumidoraCreate,
)


async def list_consumer_units(
    organizacao_id: UUID, session: AsyncSession
) -> list[UnidadeConsumidora]:
    result = await session.execute(
        select(UnidadeConsumidora).where(
            UnidadeConsumidora.organizacao_id == organizacao_id))
    return list(result.scalars().all())


async def create_consumer_unit(
    data: UnidadeConsumidoraCreate, session: AsyncSession
) -> UnidadeConsumidora:
    unit = UnidadeConsumidora(**data.model_dump())
    session.add(unit)
    await session.flush()
    await session.refresh(unit)
    return unit


async def list_consumption_records(
    inventario_id: UUID | None, organizacao_id: UUID | None, session: AsyncSession
) -> list[ConsumoEnergia]:
    query = select(ConsumoEnergia)
    if organizacao_id:
        query = query.where(ConsumoEnergia.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(ConsumoEnergia.created_at.desc()))
    return list(result.scalars().all())


async def get_consumption_record(record_id: UUID, session: AsyncSession) -> ConsumoEnergia:
    result = await session.execute(
        select(ConsumoEnergia).where(ConsumoEnergia.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def create_consumption_record(
    data: ConsumoEnergiaCreate, session: AsyncSession
) -> ConsumoEnergia:
    factor_result = await session.execute(
        select(FatorEmissaoEnergia).where(
            FatorEmissaoEnergia.ano == data.ano,
            FatorEmissaoEnergia.mes == data.mes,
        ))
    factor_row = factor_result.scalar_one_or_none()
    emissoes = calculate(data.consumo_mwh, factor_row.fator_emissao) if factor_row else None

    record = ConsumoEnergia(**data.model_dump(), emissoes_energia_tco2e=emissoes)
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def delete_consumption_record(record_id: UUID, session: AsyncSession) -> None:
    record = await get_consumption_record(record_id, session)
    await session.delete(record)


async def add_evidence(
    consumo_id: UUID,
    organizacao_id: UUID,
    data: EvidenciaConsumoEnergiaCreate,
    uploaded_by: str,
    session: AsyncSession,
) -> EvidenciaConsumoEnergia:
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
