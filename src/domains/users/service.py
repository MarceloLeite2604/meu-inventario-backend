from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Profile, UserPermissao
from .schemas import ProfileUpdate, UserPermissaoCreate


async def get_profile(user_id: str, session: AsyncSession) -> Profile:
    result = await session.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


async def upsert_profile(user_id: str, data: ProfileUpdate, session: AsyncSession) -> Profile:
    result = await session.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = Profile(id=user_id)
        session.add(profile)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    await session.flush()
    await session.refresh(profile)
    return profile


async def list_user_permissions(user_id: str, session: AsyncSession) -> list[UserPermissao]:
    result = await session.execute(
        select(UserPermissao).where(UserPermissao.user_id == user_id))
    return list(result.scalars().all())


async def grant_permission(
    user_id: str,
    data: UserPermissaoCreate,
    granted_by: str,
    session: AsyncSession,
) -> UserPermissao:
    permission = UserPermissao(
        user_id=user_id,
        organizacao_id=data.organizacao_id,
        tipo=data.tipo,
        referencia=data.referencia,
        granted_by=granted_by,
    )
    session.add(permission)
    await session.flush()
    await session.refresh(permission)
    return permission


async def has_system_access(
    user_id: str, org_id: str, scope: str, session: AsyncSession
) -> bool:
    result = await session.execute(
        select(UserPermissao).where(
            UserPermissao.user_id == user_id,
            UserPermissao.organizacao_id == org_id,
            UserPermissao.tipo == "escopo",
            UserPermissao.referencia == scope,
        ))
    return result.scalar_one_or_none() is not None
