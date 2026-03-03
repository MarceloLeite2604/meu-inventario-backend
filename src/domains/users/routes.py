from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import ProfileResponse, ProfileUpdate, UserPermissaoCreate, UserPermissaoResponse

router = APIRouter(prefix="/users", tags=["users"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str, current_user: CurrentUser, session: DatabaseSession):
    return await service.get_profile(user_id, session)


@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(
    user_id: str,
    data: ProfileUpdate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.upsert_profile(user_id, data, session)


@router.get("/{user_id}/permissions", response_model=list[UserPermissaoResponse])
async def list_permissions(user_id: str, current_user: CurrentUser, session: DatabaseSession):
    return await service.list_user_permissions(user_id, session)


@router.post("/{user_id}/permissions", response_model=UserPermissaoResponse, status_code=201)
async def grant_permission(
    user_id: str,
    data: UserPermissaoCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.grant_permission(user_id, data, current_user.id, session)
