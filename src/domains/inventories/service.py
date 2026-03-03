from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...util.logger import retrieve_logger
from .models import Inventario
from .schemas import InventarioCreate, InventarioUpdate

_LOGGER = retrieve_logger(__name__)


async def list_inventories(
    organizacao_id: UUID | None, session: AsyncSession
) -> list[Inventario]:
    _LOGGER.info("Listing inventories for organization %s", organizacao_id)
    query = select(Inventario)
    if organizacao_id:
        query = query.where(Inventario.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(Inventario.ano_base.desc()))
    return list(result.scalars().all())


async def get_inventory(inventory_id: UUID, session: AsyncSession) -> Inventario:
    _LOGGER.info("Retrieving inventory %s", inventory_id)
    result = await session.execute(
        select(Inventario).where(Inventario.id == inventory_id))
    inventory = result.scalar_one_or_none()
    if not inventory:
        _LOGGER.warning("Inventory %s not found", inventory_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inventory


async def create_inventory(data: InventarioCreate, session: AsyncSession) -> Inventario:
    _LOGGER.info("Creating inventory for organization %s", data.organizacao_id)
    inventory = Inventario(**data.model_dump())
    session.add(inventory)
    await session.flush()
    await session.refresh(inventory)
    return inventory


async def update_inventory(
    inventory_id: UUID, data: InventarioUpdate, session: AsyncSession
) -> Inventario:
    _LOGGER.info("Updating inventory %s", inventory_id)
    inventory = await get_inventory(inventory_id, session)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(inventory, field, value)
    await session.flush()
    await session.refresh(inventory)
    return inventory


async def delete_inventory(inventory_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting inventory %s", inventory_id)
    inventory = await get_inventory(inventory_id, session)
    await session.delete(inventory)
