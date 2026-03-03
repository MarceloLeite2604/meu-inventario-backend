from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....authentication import CurrentUser
from ....database import retrieve_database
from . import service
from .schemas import EmissaoEfluenteCreate, EmissaoEfluenteResponse

router = APIRouter(prefix="/inventories/{inventory_id}/scope1/effluents", tags=["scope1"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "",
    response_model=list[EmissaoEfluenteResponse],
    summary="List effluent emission records",
    description="Returns all effluent emission records for the inventory.",
)
async def list_records(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: Annotated[UUID | None, Query()] = None,
):
    return await service.list_records(inventory_id, organizacao_id, session)


@router.post(
    "",
    response_model=EmissaoEfluenteResponse,
    status_code=201,
    summary="Create effluent emission record",
    description="Creates a new effluent emission record with calculated CH4 and N2O emissions.",
)
async def create_record(
    inventory_id: UUID,
    data: EmissaoEfluenteCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    data.inventario_id = inventory_id
    return await service.create_record(data, session)


@router.get(
    "/{record_id}",
    response_model=EmissaoEfluenteResponse,
    summary="Get effluent emission record",
    description="Returns a single effluent emission record by ID.",
)
async def get_record(
    inventory_id: UUID, record_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_record(record_id, session)


@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Delete effluent emission record",
    description="Deletes an effluent emission record by ID.",
)
async def delete_record(
    inventory_id: UUID, record_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    await service.delete_record(record_id, session)
