from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import FatorTratamentoEfluente, Gwp
from ....util.logger import retrieve_logger
from .calculations import calculate
from .models import EmissaoEfluente
from .schemas import EmissaoEfluenteCreate

_LOGGER = retrieve_logger(__name__)


async def _get_gwp(gas: str, session: AsyncSession) -> float:
    result = await session.execute(select(Gwp).where(Gwp.nome_ghg == gas))
    row = result.scalar_one_or_none()
    return row.gwp_value if row else 1.0


async def list_records(
    inventario_id: UUID | None, organizacao_id: UUID | None, session: AsyncSession
) -> list[EmissaoEfluente]:
    _LOGGER.info("Listing effluent emission records for inventory %s", inventario_id)
    query = select(EmissaoEfluente)
    if inventario_id:
        query = query.where(EmissaoEfluente.inventario_id == inventario_id)
    if organizacao_id:
        query = query.where(EmissaoEfluente.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(EmissaoEfluente.created_at.desc()))
    return list(result.scalars().all())


async def get_record(record_id: UUID, session: AsyncSession) -> EmissaoEfluente:
    _LOGGER.info("Retrieving effluent emission record %s", record_id)
    result = await session.execute(
        select(EmissaoEfluente).where(EmissaoEfluente.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        _LOGGER.warning("Effluent emission record %s not found", record_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def create_record(data: EmissaoEfluenteCreate, session: AsyncSession) -> EmissaoEfluente:
    _LOGGER.info("Creating effluent emission record for organization %s", data.organizacao_id)
    gwp_ch4 = await _get_gwp("CH4", session)
    gwp_n2o = await _get_gwp("N2O", session)

    fator_n2o = 0.0
    if data.tipo_tratamento:
        result = await session.execute(
            select(FatorTratamentoEfluente).where(
                FatorTratamentoEfluente.tipo_tratamento == data.tipo_tratamento))
        factor = result.scalar_one_or_none()
        if factor and factor.fator_n2o_default:
            fator_n2o = factor.fator_n2o_default

    calculated = None
    if not all(v is not None for v in [
        data.volume_efluente, data.carga_organica_entrada, data.carga_organica_lodo,
        data.mcf_tratamento, data.nitrogenio_efluente
    ]):
        _LOGGER.warning(
            "Insufficient data to calculate effluent emissions for organization %s",
            data.organizacao_id,
        )
    if all(v is not None for v in [
        data.volume_efluente, data.carga_organica_entrada, data.carga_organica_lodo,
        data.mcf_tratamento, data.nitrogenio_efluente
    ]):
        calculated = calculate(
            volume_efluente=data.volume_efluente,  # type: ignore[arg-type]
            carga_organica_entrada=data.carga_organica_entrada,  # type: ignore[arg-type]
            carga_organica_lodo=data.carga_organica_lodo,  # type: ignore[arg-type]
            mcf_tratamento=data.mcf_tratamento,  # type: ignore[arg-type]
            mcf_tratamento_2=data.mcf_tratamento_2 or 0.0,
            mcf_disposicao=data.mcf_disposicao or 0.0,
            ch4_recuperado=data.ch4_recuperado or 0.0,
            nitrogenio_efluente=data.nitrogenio_efluente,  # type: ignore[arg-type]
            fator_n2o=fator_n2o,
            tratamento_sequencial=data.tratamento_sequencial or False,
            efluente_lancado_ambiente=data.efluente_lancado_ambiente or False,
            gwp_ch4=gwp_ch4,
            gwp_n2o=gwp_n2o,
        )

    record = EmissaoEfluente(
        **data.model_dump(),
        fator_n2o=fator_n2o,
        emissoes_ch4=calculated.emissoes_ch4 if calculated else None,
        emissoes_n2o=calculated.emissoes_n2o if calculated else None,
        emissoes_co2_biogenico=calculated.emissoes_co2_biogenico if calculated else None,
        emissoes_tco2e=calculated.emissoes_tco2e if calculated else None,
    )
    session.add(record)
    await session.flush()
    await session.refresh(record)
    return record


async def delete_record(record_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting effluent emission record %s", record_id)
    record = await get_record(record_id, session)
    await session.delete(record)
