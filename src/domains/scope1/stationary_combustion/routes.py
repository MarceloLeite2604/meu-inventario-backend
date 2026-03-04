from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ....authentication import CurrentUser
from ....database import retrieve_database
from . import service
from .schemas import (
    EmissaoEstacionariaCreate,
    EmissaoEstacionariaResponse,
    ReprocessResponse,
    SpedImportRequest,
    SpedImportResponse,
    SpedPreviewResponse,
)

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


@router.post(
    "/reprocess",
    response_model=ReprocessResponse,
    summary="Reprocess stationary combustion emissions",
    description="Recalculates emissions for stationary combustion records with missing emission values.",
)
async def reprocess_records(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    reprocessados = await service.reprocess_records(session)
    return ReprocessResponse(reprocessados=reprocessados)


@router.post(
    "/sped-preview",
    response_model=SpedPreviewResponse,
    summary="Preview SPED file items",
    description="Parses a SPED file and returns Bloco C items with auto-mapped fuel suggestions.",
)
async def sped_preview(
    inventory_id: UUID,
    current_user: CurrentUser,
    file: UploadFile,
):
    content = await file.read()
    items = service.parse_sped_file(content)
    return SpedPreviewResponse(items=items)


@router.post(
    "/sped-import",
    response_model=SpedImportResponse,
    status_code=201,
    summary="Import SPED items as stationary combustion records",
    description="Creates stationary combustion emission records from SPED-mapped items.",
)
async def sped_import(
    inventory_id: UUID,
    data: SpedImportRequest,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    criados, registros = await service.import_sped_items(data, session)
    return SpedImportResponse(criados=criados, registros=registros)
