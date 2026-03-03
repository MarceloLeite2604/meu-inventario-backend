from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import InventarioCreate, InventarioResponse, InventarioUpdate

router = APIRouter(prefix="/inventories", tags=["inventories"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get("", response_model=list[InventarioResponse])
async def list_inventories(
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: UUID | None = Query(default=None),
):
    return await service.list_inventories(organizacao_id, session)


@router.post("", response_model=InventarioResponse, status_code=201)
async def create_inventory(
    data: InventarioCreate, current_user: CurrentUser, session: DatabaseSession
):
    return await service.create_inventory(data, session)


@router.get("/{inventory_id}", response_model=InventarioResponse)
async def get_inventory(
    inventory_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_inventory(inventory_id, session)


@router.put("/{inventory_id}", response_model=InventarioResponse)
async def update_inventory(
    inventory_id: UUID,
    data: InventarioUpdate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.update_inventory(inventory_id, data, session)


@router.delete("/{inventory_id}", status_code=204)
async def delete_inventory(
    inventory_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    await service.delete_inventory(inventory_id, session)
