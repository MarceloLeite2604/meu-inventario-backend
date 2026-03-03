from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....authentication import CurrentUser
from ....database import retrieve_database
from . import service
from .schemas import EmissaoFugitivaCreate, EmissaoFugitivaResponse

router = APIRouter(prefix="/inventories/{inventory_id}/scope1/fugitive", tags=["scope1"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "",
    response_model=list[EmissaoFugitivaResponse],
    summary="List fugitive emission records",
    description="Returns all fugitive emission records for the inventory.",
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
    response_model=EmissaoFugitivaResponse,
    status_code=201,
    summary="Create fugitive emission record",
    description="Creates a new fugitive emission record.",
)
async def create_record(
    inventory_id: UUID,
    data: EmissaoFugitivaCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.create_record(data, session)


@router.get(
    "/{record_id}",
    response_model=EmissaoFugitivaResponse,
    summary="Get fugitive emission record",
    description="Returns a single fugitive emission record by ID.",
)
async def get_record(
    inventory_id: UUID, record_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_record(record_id, session)


@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Delete fugitive emission record",
    description="Deletes a fugitive emission record by ID.",
)
async def delete_record(
    inventory_id: UUID, record_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    await service.delete_record(record_id, session)
