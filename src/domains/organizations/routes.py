from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...authentication import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import (
    OrganizacaoCreate,
    OrganizacaoResponse,
    OrganizacaoUpdate,
    OrganizacaoUsuarioCreate,
    OrganizacaoUsuarioResponse,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "",
    response_model=list[OrganizacaoResponse],
    summary="List organizations",
    description="Returns all organizations ordered by name.",
)
async def list_organizations(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_organizations(session)


@router.post(
    "",
    response_model=OrganizacaoResponse,
    status_code=201,
    summary="Create organization",
    description="Creates a new organization.",
)
async def create_organization(
    data: OrganizacaoCreate, current_user: CurrentUser, session: DatabaseSession
):
    return await service.create_organization(data, session)


@router.get(
    "/{organization_id}",
    response_model=OrganizacaoResponse,
    summary="Get organization",
    description="Returns a single organization by ID.",
)
async def get_organization(
    organization_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_organization(organization_id, session)


@router.put(
    "/{organization_id}",
    response_model=OrganizacaoResponse,
    summary="Update organization",
    description="Updates an existing organization's data.",
)
async def update_organization(
    organization_id: UUID,
    data: OrganizacaoUpdate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.update_organization(organization_id, data, session)


@router.delete(
    "/{organization_id}",
    status_code=204,
    summary="Delete organization",
    description="Deletes an organization by ID.",
)
async def delete_organization(
    organization_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    await service.delete_organization(organization_id, session)


@router.get(
    "/{organization_id}/users",
    response_model=list[OrganizacaoUsuarioResponse],
    summary="List organization users",
    description="Returns all users associated with the organization.",
)
async def list_organization_users(
    organization_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_organization_users(organization_id, session)


@router.post(
    "/{organization_id}/users",
    response_model=OrganizacaoUsuarioResponse,
    status_code=201,
    summary="Add user to organization",
    description="Associates a user with the organization.",
)
async def add_organization_user(
    organization_id: UUID,
    data: OrganizacaoUsuarioCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.add_organization_user(organization_id, data, current_user.id, session)


@router.delete(
    "/{organization_id}/users/{user_id}",
    status_code=204,
    summary="Remove user from organization",
    description="Removes a user from the organization.",
)
async def remove_organization_user(
    organization_id: UUID, user_id: str, current_user: CurrentUser, session: DatabaseSession
):
    await service.remove_organization_user(organization_id, user_id, session)
