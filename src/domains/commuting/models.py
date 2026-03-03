from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base import Base


class CommutingEmpresa(Base):
    __tablename__ = "commuting_empresas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    dominio_email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    logo_url: Mapped[str | None] = mapped_column(Text)
    cidade: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str | None] = mapped_column(String(50))
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255))

    colaboradores: Mapped[list["CommutingColaborador"]] = relationship(
        back_populates="empresa", cascade="all, delete-orphan")


class CommutingColaborador(Base):
    __tablename__ = "commuting_colaboradores"

    __table_args__ = (
        UniqueConstraint("user_id", "empresa_id", name="uq_colaborador_user_empresa"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    empresa_id: Mapped[UUID] = mapped_column(
        ForeignKey("commuting_empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    departamento: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    pontos_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    streak_semanas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    empresa: Mapped["CommutingEmpresa"] = relationship(back_populates="colaboradores")
    registros: Mapped[list["CommutingRegistro"]] = relationship(
        back_populates="colaborador", cascade="all, delete-orphan")
    transportes_habituais: Mapped[list["CommutingTransporteHabitual"]] = relationship(
        back_populates="colaborador", cascade="all, delete-orphan")
    medalhas: Mapped[list["CommutingColaboradorMedalha"]] = relationship(
        back_populates="colaborador", cascade="all, delete-orphan")


class CommutingTransporteHabitual(Base):
    __tablename__ = "commuting_transportes_habituais"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    colaborador_id: Mapped[UUID] = mapped_column(
        ForeignKey("commuting_colaboradores.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_transporte: Mapped[str] = mapped_column(String(50), nullable=False)
    combustivel: Mapped[str | None] = mapped_column(String(100))
    subtipo_veiculo: Mapped[str | None] = mapped_column(String(100))
    distancia_km: Mapped[float] = mapped_column(Float, nullable=False)
    ida_e_volta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    dias_por_semana: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    colaborador: Mapped["CommutingColaborador"] = relationship(
        back_populates="transportes_habituais")


class CommutingRegistro(Base):
    __tablename__ = "commuting_registros"

    __table_args__ = (
        UniqueConstraint("colaborador_id", "semana_inicio", "tipo_transporte",
                         name="uq_registro_colaborador_semana_transporte"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    colaborador_id: Mapped[UUID] = mapped_column(
        ForeignKey("commuting_colaboradores.id", ondelete="CASCADE"), nullable=False, index=True)
    semana_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    tipo_transporte: Mapped[str] = mapped_column(String(50), nullable=False)
    combustivel: Mapped[str | None] = mapped_column(String(100))
    distancia_km: Mapped[float] = mapped_column(Float, nullable=False)
    dias_utilizados: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    emissoes_tco2e: Mapped[float | None] = mapped_column(Float)
    pontos_ganhos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    colaborador: Mapped["CommutingColaborador"] = relationship(back_populates="registros")


class CommutingMedalha(Base):
    __tablename__ = "commuting_medalhas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    icone: Mapped[str] = mapped_column(String(10), nullable=False, default="🏅")
    criterio: Mapped[str] = mapped_column(String(100), nullable=False)
    pontos_bonus: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    colaborador_medalhas: Mapped[list["CommutingColaboradorMedalha"]] = relationship(
        back_populates="medalha", cascade="all, delete-orphan")


class CommutingColaboradorMedalha(Base):
    __tablename__ = "commuting_colaborador_medalhas"

    __table_args__ = (
        UniqueConstraint("colaborador_id", "medalha_id",
                         name="uq_colaborador_medalha"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    colaborador_id: Mapped[UUID] = mapped_column(
        ForeignKey("commuting_colaboradores.id", ondelete="CASCADE"), nullable=False, index=True)
    medalha_id: Mapped[UUID] = mapped_column(
        ForeignKey("commuting_medalhas.id", ondelete="CASCADE"), nullable=False, index=True)
    conquistada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    colaborador: Mapped["CommutingColaborador"] = relationship(back_populates="medalhas")
    medalha: Mapped["CommutingMedalha"] = relationship(back_populates="colaborador_medalhas")
