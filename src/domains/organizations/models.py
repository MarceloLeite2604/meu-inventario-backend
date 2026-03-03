from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base import Base


class Organizacao(Base):
    __tablename__ = "organizacoes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    logo_url: Mapped[str | None] = mapped_column(Text)
    cnpj: Mapped[str | None] = mapped_column(String(20))
    cnae: Mapped[str | None] = mapped_column(String(10))
    endereco: Mapped[str | None] = mapped_column(Text)
    cidade: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str | None] = mapped_column(String(50))
    cep: Mapped[str | None] = mapped_column(String(10))
    pais: Mapped[str | None] = mapped_column(String(100))
    email_responsavel: Mapped[str | None] = mapped_column(String(255))
    telefone_responsavel: Mapped[str | None] = mapped_column(String(30))
    pessoa_responsavel: Mapped[str | None] = mapped_column(String(255))
    num_funcionarios: Mapped[int | None] = mapped_column(Integer)
    segmento: Mapped[str | None] = mapped_column(String(100))
    descricao_atividades: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(String(255))
    organograma_url: Mapped[str | None] = mapped_column(Text)
    abordagem_consolidacao: Mapped[str | None] = mapped_column(String(100))
    justificativa_abordagem: Mapped[str | None] = mapped_column(Text)
    limite_organizacional: Mapped[str | None] = mapped_column(Text)
    modulo_inventario_habilitado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    modulo_deslocamentos_habilitado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    usuarios: Mapped[list["OrganizacaoUsuario"]] = relationship(
        back_populates="organizacao", cascade="all, delete-orphan")


class OrganizacaoUsuario(Base):
    __tablename__ = "organizacao_usuarios"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organizacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    papel: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    granted_by: Mapped[str | None] = mapped_column(String(255))

    organizacao: Mapped["Organizacao"] = relationship(back_populates="usuarios")
    modulos: Mapped[list["OrganizacaoUsuarioModulo"]] = relationship(
        back_populates="organizacao_usuario", cascade="all, delete-orphan")


class OrganizacaoUsuarioModulo(Base):
    __tablename__ = "organizacao_usuario_modulos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organizacao_usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizacao_usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    granted_by: Mapped[str | None] = mapped_column(String(255))

    organizacao_usuario: Mapped["OrganizacaoUsuario"] = relationship(back_populates="modulos")
