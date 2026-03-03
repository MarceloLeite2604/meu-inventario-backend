from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...util.logger import retrieve_logger
from .models import Organizacao, OrganizacaoUsuario
from .schemas import OrganizacaoCreate, OrganizacaoUpdate, OrganizacaoUsuarioCreate

_LOGGER = retrieve_logger(__name__)


async def list_organizations(session: AsyncSession) -> list[Organizacao]:
    _LOGGER.info("Listing all organizations")
    result = await session.execute(select(Organizacao).order_by(Organizacao.nome))
    return list(result.scalars().all())


async def get_organization(organization_id: UUID, session: AsyncSession) -> Organizacao:
    _LOGGER.info("Retrieving organization %s", organization_id)
    result = await session.execute(
        select(Organizacao).where(Organizacao.id == organization_id))
    organization = result.scalar_one_or_none()
    if not organization:
        _LOGGER.warning("Organization %s not found", organization_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return organization


async def create_organization(data: OrganizacaoCreate, session: AsyncSession) -> Organizacao:
    _LOGGER.info("Creating organization with name %s", data.nome)
    organization = Organizacao(**data.model_dump())
    session.add(organization)
    await session.flush()
    await session.refresh(organization)
    return organization


async def update_organization(
    organization_id: UUID,
    data: OrganizacaoUpdate,
    session: AsyncSession,
) -> Organizacao:
    _LOGGER.info("Updating organization %s", organization_id)
    organization = await get_organization(organization_id, session)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(organization, field, value)
    await session.flush()
    await session.refresh(organization)
    return organization


async def delete_organization(organization_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting organization %s", organization_id)
    organization = await get_organization(organization_id, session)
    await session.delete(organization)


async def list_organization_users(
    organization_id: UUID, session: AsyncSession
) -> list[OrganizacaoUsuario]:
    _LOGGER.info("Listing users for organization %s", organization_id)
    result = await session.execute(
        select(OrganizacaoUsuario).where(
            OrganizacaoUsuario.organizacao_id == organization_id))
    return list(result.scalars().all())


async def add_organization_user(
    organization_id: UUID,
    data: OrganizacaoUsuarioCreate,
    granted_by: str,
    session: AsyncSession,
) -> OrganizacaoUsuario:
    _LOGGER.info("Adding user %s to organization %s", data.user_id, organization_id)
    membership = OrganizacaoUsuario(
        organizacao_id=organization_id,
        user_id=data.user_id,
        papel=data.papel,
        granted_by=granted_by,
    )
    session.add(membership)
    await session.flush()
    await session.refresh(membership)
    return membership


async def remove_organization_user(
    organization_id: UUID, user_id: str, session: AsyncSession
) -> None:
    _LOGGER.info("Removing user %s from organization %s", user_id, organization_id)
    result = await session.execute(
        select(OrganizacaoUsuario).where(
            OrganizacaoUsuario.organizacao_id == organization_id,
            OrganizacaoUsuario.user_id == user_id,
        ))
    membership = result.scalar_one_or_none()
    if not membership:
        _LOGGER.warning("User %s not found in organization %s", user_id, organization_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not in organization")
    await session.delete(membership)
