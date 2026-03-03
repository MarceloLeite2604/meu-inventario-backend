from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....base import Base


class EmissaoEfluente(Base):
    __tablename__ = "emissoes_efluentes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    inventario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("inventarios.id", ondelete="SET NULL"), index=True)
    organizacao_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="SET NULL"), index=True)
    tipo_efluente: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo_tratamento: Mapped[str | None] = mapped_column(String(100))
    tipo_tratamento_2: Mapped[str | None] = mapped_column(String(100))
    tipo_disposicao_final: Mapped[str | None] = mapped_column(String(100))
    volume_efluente: Mapped[float | None] = mapped_column(Float)
    unidade_carga_organica: Mapped[str | None] = mapped_column(String(10))
    carga_organica_entrada: Mapped[float | None] = mapped_column(Float)
    carga_organica_lodo: Mapped[float | None] = mapped_column(Float)
    nitrogenio_efluente: Mapped[float | None] = mapped_column(Float)
    efluente_lancado_ambiente: Mapped[bool | None] = mapped_column(Boolean)
    tratamento_sequencial: Mapped[bool | None] = mapped_column(Boolean)
    mcf_tratamento: Mapped[float | None] = mapped_column(Float)
    mcf_tratamento_2: Mapped[float | None] = mapped_column(Float)
    mcf_disposicao: Mapped[float | None] = mapped_column(Float)
    ch4_recuperado: Mapped[float | None] = mapped_column(Float)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    emissoes_ch4: Mapped[float | None] = mapped_column(Float)
    emissoes_co2_biogenico: Mapped[float | None] = mapped_column(Float)
    emissoes_n2o: Mapped[float | None] = mapped_column(Float)
    emissoes_tco2e: Mapped[float | None] = mapped_column(Float)
    fator_n2o: Mapped[float | None] = mapped_column(Float)
    setor_industrial: Mapped[str | None] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
