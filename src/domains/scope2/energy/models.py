from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ....base import Base


class UnidadeConsumidora(Base):
    __tablename__ = "unidades_consumidoras"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organizacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="CASCADE"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    numero_uc: Mapped[str | None] = mapped_column(String(100))
    endereco: Mapped[str | None] = mapped_column(Text)
    distribuidora: Mapped[str | None] = mapped_column(String(255))
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    consumos: Mapped[list["ConsumoEnergia"]] = relationship(
        back_populates="unidade_consumidora", cascade="all, delete-orphan")


class ConsumoEnergia(Base):
    __tablename__ = "consumo_energia"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organizacao_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="SET NULL"), index=True)
    unidade_consumidora_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("unidades_consumidoras.id", ondelete="SET NULL"), index=True)
    consumo_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    emissoes_energia_tco2e: Mapped[float | None] = mapped_column(Float)
    descricao: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    unidade_consumidora: Mapped["UnidadeConsumidora | None"] = relationship(
        back_populates="consumos")
    evidencias: Mapped[list["EvidenciaConsumoEnergia"]] = relationship(
        back_populates="consumo_energia", cascade="all, delete-orphan")


class EvidenciaConsumoEnergia(Base):
    __tablename__ = "evidencias_consumo_energia"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    consumo_energia_id: Mapped[UUID] = mapped_column(
        ForeignKey("consumo_energia.id", ondelete="CASCADE"), nullable=False, index=True)
    organizacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="CASCADE"), nullable=False, index=True)
    arquivo_url: Mapped[str] = mapped_column(Text, nullable=False)
    nome_arquivo_original: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False, default="fatura")
    observacoes: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    consumo_energia: Mapped["ConsumoEnergia"] = relationship(back_populates="evidencias")
