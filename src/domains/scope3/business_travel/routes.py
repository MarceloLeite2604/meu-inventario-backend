from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....auth import CurrentUser
from ....database import retrieve_database
from . import service
from .schemas import (
    DeslocamentoCreate,
    DeslocamentoResponse,
    EmissaoViagemNegocioCreate,
    EmissaoViagemNegocioResponse,
)

router = APIRouter(prefix="/inventories/{inventory_id}/scope3/business-travel", tags=["scope3"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get("", response_model=list[EmissaoViagemNegocioResponse])
async def list_records(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: UUID | None = Query(default=None),
):
    return await service.list_records(inventory_id, organizacao_id, session)


@router.post("", response_model=EmissaoViagemNegocioResponse, status_code=201)
async def create_record(
    inventory_id: UUID,
    data: EmissaoViagemNegocioCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.create_record(data, session)


@router.get("/{record_id}", response_model=EmissaoViagemNegocioResponse)
async def get_record(
    inventory_id: UUID,
    record_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.get_record(record_id, session)


@router.delete("/{record_id}", status_code=204)
async def delete_record(
    inventory_id: UUID,
    record_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    await service.delete_record(record_id, session)


@router.get("/displacements", response_model=list[DeslocamentoResponse])
async def list_displacements(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: UUID | None = Query(default=None),
):
    return await service.list_displacements(organizacao_id, session)


@router.post("/displacements", response_model=DeslocamentoResponse, status_code=201)
async def create_displacement(
    inventory_id: UUID,
    data: DeslocamentoCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.create_displacement(data, session)
