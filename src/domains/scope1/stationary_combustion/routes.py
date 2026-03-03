from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....authentication import CurrentUser
from ....database import retrieve_database
from . import service
from .schemas import EmissaoEstacionariaCreate, EmissaoEstacionariaResponse

router = APIRouter(
    prefix="/inventories/{inventory_id}/scope1/stationary-combustion", tags=["scope1"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "",
    response_model=list[EmissaoEstacionariaResponse],
    summary="List stationary combustion records",
    description="Returns all stationary combustion emission records for the inventory.",
)
async def list_records(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: Annotated[UUID | None, Query()] = None,
):
    return await service.list_records(organizacao_id, session)


@router.post(
    "",
    response_model=EmissaoEstacionariaResponse,
    status_code=201,
    summary="Create stationary combustion record",
    description="Creates a new stationary combustion emission record.",
)
async def create_record(
    inventory_id: UUID,
    data: EmissaoEstacionariaCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.create_record(data, session)


@router.get(
    "/{record_id}",
    response_model=EmissaoEstacionariaResponse,
    summary="Get stationary combustion record",
    description="Returns a single stationary combustion emission record by ID.",
)
async def get_record(
    inventory_id: UUID, record_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_record(record_id, session)


@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Delete stationary combustion record",
    description="Deletes a stationary combustion emission record by ID.",
)
async def delete_record(
    inventory_id: UUID, record_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    await service.delete_record(record_id, session)
