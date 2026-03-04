from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domains.reference_data.models import FatorEstacionaria, Gwp
from ....util.logger import retrieve_logger
from .calculations import calculate
from .models import EmissaoEstacionaria
from .schemas import EmissaoEstacionariaCreate, SpedImportRequest, SpedItem
from .sped_parser import parse_sped

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


async def reprocess_records(session: AsyncSession) -> int:
    _LOGGER.info("Reprocessing stationary combustion records with missing emissions")
    result = await session.execute(
        select(EmissaoEstacionaria).where(EmissaoEstacionaria.emissoes_total_tco2e.is_(None))
    )
    records = list(result.scalars().all())
    gwp_ch4 = await _get_gwp("CH4", session)
    gwp_n2o = await _get_gwp("N2O", session)
    count = 0
    for record in records:
        if not record.combustivel_fossil:
            continue
        factor_result = await session.execute(
            select(FatorEstacionaria).where(
                FatorEstacionaria.combustivel == record.combustivel_fossil
            )
        )
        factor = factor_result.scalar_one_or_none()
        if not factor:
            continue
        fator_co2 = factor.co2 or 0.0
        fator_ch4 = factor.ch4_energia or 0.0
        fator_n2o = factor.n2o_energia or 0.0
        calc = calculate(
            record.quantidade_fossil or 0.0,
            record.quantidade_biocombustivel or 0.0,
            fator_co2, fator_ch4, fator_n2o,
            gwp_ch4=gwp_ch4, gwp_n2o=gwp_n2o,
        )
        record.emissoes_co2 = calc.emissoes_co2
        record.emissoes_ch4 = calc.emissoes_ch4
        record.emissoes_n2o = calc.emissoes_n2o
        record.emissoes_co2_biogenico = calc.emissoes_co2_biogenico
        record.emissoes_ch4_biogenico = calc.emissoes_ch4_biogenico
        record.emissoes_n2o_biogenico = calc.emissoes_n2o_biogenico
        record.emissoes_total_tco2e = calc.emissoes_total_tco2e
        record.fator_co2 = fator_co2
        record.fator_ch4 = fator_ch4
        record.fator_n2o = fator_n2o
        count += 1
    await session.flush()
    _LOGGER.info("Reprocessed %d stationary combustion records", count)
    return count


def parse_sped_file(content: bytes) -> list[SpedItem]:
    _LOGGER.info("Parsing SPED file (%d bytes)", len(content))
    parsed = parse_sped(content)
    return [
        SpedItem(
            codigo=item.codigo,
            descricao=item.descricao,
            quantidade=item.quantidade,
            unidade=item.unidade,
            combustivel_fossil_sugerido=item.combustivel_fossil_sugerido,
        )
        for item in parsed
    ]


async def import_sped_items(
    request: SpedImportRequest, session: AsyncSession
) -> tuple[int, list[EmissaoEstacionaria]]:
    _LOGGER.info(
        "Importing %d SPED items for organization %s", len(request.items), request.organizacao_id
    )
    records: list[EmissaoEstacionaria] = []
    for item in request.items:
        data = EmissaoEstacionariaCreate(
            organizacao_id=request.organizacao_id,
            combustivel=item.descricao,
            combustivel_fossil=item.combustivel_fossil,
            quantidade=item.quantidade,
            quantidade_fossil=item.quantidade,
            unidade=item.unidade,
            ano=request.ano,
            mes=request.mes,
            descricao=request.descricao,
        )
        record = await create_record(data, session)
        records.append(record)
    return len(records), records
