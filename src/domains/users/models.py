from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ...base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    granted_by: Mapped[str | None] = mapped_column(String(255))


class UserSystem(Base):
    __tablename__ = "user_systems"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    system_name: Mapped[str] = mapped_column(String(50), nullable=False)
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    granted_by: Mapped[str | None] = mapped_column(String(255))


class UserPermissao(Base):
    __tablename__ = "user_permissoes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    organizacao_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    referencia: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    granted_by: Mapped[str | None] = mapped_column(String(255))


class CategoriaPermissao(Base):
    __tablename__ = "categorias_permissao"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sistema: Mapped[str] = mapped_column(String(50), nullable=False)
    escopo: Mapped[str] = mapped_column(String(50), nullable=False)
    nome_exibicao: Mapped[str] = mapped_column(String(255), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UserTrialStatus(Base):
    __tablename__ = "user_trial_status"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    trial_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    trial_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    extended_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    granted_by: Mapped[str | None] = mapped_column(String(255))
