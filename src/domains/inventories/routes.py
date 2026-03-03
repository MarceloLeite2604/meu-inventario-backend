from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...authentication import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import InventarioCreate, InventarioResponse, InventarioUpdate

router = APIRouter(prefix="/inventories", tags=["inventories"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "",
    response_model=list[InventarioResponse],
    summary="List inventories",
    description="Returns all inventories, optionally filtered by organization.",
)
async def list_inventories(
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: Annotated[UUID | None, Query()] = None,
):
    return await service.list_inventories(organizacao_id, session)


@router.post(
    "",
    response_model=InventarioResponse,
    status_code=201,
    summary="Create inventory",
    description="Creates a new GHG emissions inventory.",
)
async def create_inventory(
    data: InventarioCreate, current_user: CurrentUser, session: DatabaseSession
):
    return await service.create_inventory(data, session)


@router.get(
    "/{inventory_id}",
    response_model=InventarioResponse,
    summary="Get inventory",
    description="Returns a single inventory by ID.",
)
async def get_inventory(
    inventory_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_inventory(inventory_id, session)


@router.put(
    "/{inventory_id}",
    response_model=InventarioResponse,
    summary="Update inventory",
    description="Updates an existing inventory's data.",
)
async def update_inventory(
    inventory_id: UUID,
    data: InventarioUpdate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.update_inventory(inventory_id, data, session)


@router.delete(
    "/{inventory_id}",
    status_code=204,
    summary="Delete inventory",
    description="Deletes an inventory by ID.",
)
async def delete_inventory(
    inventory_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    await service.delete_inventory(inventory_id, session)
