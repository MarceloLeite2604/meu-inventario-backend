from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....authentication import CurrentUser
from ....database import retrieve_database
from . import service
from .schemas import (
    ConsumoEnergiaCreate,
    ConsumoEnergiaResponse,
    EvidenciaConsumoEnergiaCreate,
    EvidenciaConsumoEnergiaResponse,
    ReprocessResponse,
    UnidadeConsumidoraCreate,
    UnidadeConsumidoraResponse,
)

router = APIRouter(prefix="/inventories/{inventory_id}/scope2/energy", tags=["scope2"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "/consumer-units",
    response_model=list[UnidadeConsumidoraResponse],
    summary="List consumer units",
    description="Returns all electricity consumer units for the organization.",
)
async def list_consumer_units(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: Annotated[UUID | None, Query()] = None,
):
    org_id = organizacao_id or current_user.organization.id
    return await service.list_consumer_units(org_id, session)


@router.post(
    "/consumer-units",
    response_model=UnidadeConsumidoraResponse,
    status_code=201,
    summary="Create consumer unit",
    description="Creates a new electricity consumer unit.",
)
async def create_consumer_unit(
    inventory_id: UUID,
    data: UnidadeConsumidoraCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.create_consumer_unit(data, session)


@router.get(
    "",
    response_model=list[ConsumoEnergiaResponse],
    summary="List energy consumption records",
    description="Returns all energy consumption records for the inventory.",
)
async def list_consumption_records(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: Annotated[UUID | None, Query()] = None,
):
    return await service.list_consumption_records(inventory_id, organizacao_id, session)


@router.post(
    "",
    response_model=ConsumoEnergiaResponse,
    status_code=201,
    summary="Create energy consumption record",
    description="Creates a new energy consumption record with calculated emissions.",
)
async def create_consumption_record(
    inventory_id: UUID,
    data: ConsumoEnergiaCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.create_consumption_record(data, session)


@router.get(
    "/{record_id}",
    response_model=ConsumoEnergiaResponse,
    summary="Get energy consumption record",
    description="Returns a single energy consumption record by ID.",
)
async def get_consumption_record(
    inventory_id: UUID,
    record_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.get_consumption_record(record_id, session)


@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Delete energy consumption record",
    description="Deletes an energy consumption record by ID.",
)
async def delete_consumption_record(
    inventory_id: UUID,
    record_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    await service.delete_consumption_record(record_id, session)


@router.post(
    "/reprocess",
    response_model=ReprocessResponse,
    summary="Reprocess energy emissions",
    description="Recalculates emissions for energy consumption records with missing emission values.",
)
async def reprocess_emissions(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    reprocessados = await service.reprocess_emissions(session)
    return ReprocessResponse(reprocessados=reprocessados)


@router.post(
    "/{record_id}/evidence",
    response_model=EvidenciaConsumoEnergiaResponse,
    status_code=201,
    summary="Add evidence to consumption record",
    description="Uploads an evidence file linked to an energy consumption record.",
)
async def add_evidence(
    inventory_id: UUID,
    record_id: UUID,
    data: EvidenciaConsumoEnergiaCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.add_evidence(
        consumo_id=record_id,
        organizacao_id=current_user.organization.id,
        data=data,
        uploaded_by=current_user.id,
        session=session,
    )
