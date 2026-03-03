from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...base import Base


class QuestionarioSalvo(Base):
    __tablename__ = "questionarios_salvos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    organizacao_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="SET NULL"), index=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    total_deslocamentos: Mapped[int | None] = mapped_column(Integer)
    total_emissoes: Mapped[float | None] = mapped_column(Float)
    created_by: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    respondentes: Mapped[list["QuestionarioRespondente"]] = relationship(
        back_populates="questionario", cascade="all, delete-orphan")
    deslocamentos: Mapped[list["QuestionarioDeslocamento"]] = relationship(
        back_populates="questionario", cascade="all, delete-orphan")


class QuestionarioRespondente(Base):
    __tablename__ = "questionarios_respondentes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    questionario_id: Mapped[UUID] = mapped_column(
        ForeignKey("questionarios_salvos.id", ondelete="CASCADE"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    questionario: Mapped["QuestionarioSalvo"] = relationship(back_populates="respondentes")
    deslocamentos: Mapped[list["QuestionarioDeslocamento"]] = relationship(
        back_populates="respondente", cascade="all, delete-orphan")


class QuestionarioDeslocamento(Base):
    __tablename__ = "questionarios_deslocamentos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    questionario_id: Mapped[UUID] = mapped_column(
        ForeignKey("questionarios_salvos.id", ondelete="CASCADE"), nullable=False, index=True)
    respondente_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("questionarios_respondentes.id", ondelete="SET NULL"), index=True)
    transport: Mapped[str] = mapped_column(String(50), nullable=False)
    fuel: Mapped[str | None] = mapped_column(String(100))
    origin: Mapped[str | None] = mapped_column(Text)
    destination: Mapped[str | None] = mapped_column(Text)
    distance: Mapped[float | None] = mapped_column(Float)
    round_trip: Mapped[bool | None] = mapped_column(Boolean)
    year: Mapped[int | None] = mapped_column(Integer)
    tipo_frota_de_veiculos: Mapped[str | None] = mapped_column(String(100))
    vehicle_subtype: Mapped[str | None] = mapped_column(String(100))
    combustivel_fossil: Mapped[str | None] = mapped_column(String(100))
    biocombustivel: Mapped[str | None] = mapped_column(String(100))
    emissoes_tco2e_total: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    questionario: Mapped["QuestionarioSalvo"] = relationship(back_populates="deslocamentos")
    respondente: Mapped["QuestionarioRespondente | None"] = relationship(
        back_populates="deslocamentos")


class RateLimit(Base):
    __tablename__ = "rate_limits"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)
