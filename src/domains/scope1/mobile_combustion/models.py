from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....base import Base


class EmissaoCombustaoMovel(Base):
    __tablename__ = "emissoes_combustao_movel"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    inventario_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("inventarios.id", ondelete="SET NULL"), index=True)
    organizacao_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="SET NULL"), index=True)
    metodo_calculo: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo_veiculo: Mapped[str | None] = mapped_column(String(100))
    ano_veiculo: Mapped[int | None] = mapped_column(Integer)
    combustivel: Mapped[str | None] = mapped_column(String(100))
    combustivel_fossil: Mapped[str | None] = mapped_column(String(100))
    biocombustivel: Mapped[str | None] = mapped_column(String(100))
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    quantidade_fossil: Mapped[float | None] = mapped_column(Float)
    quantidade_biocombustivel: Mapped[float | None] = mapped_column(Float)
    unidade: Mapped[str] = mapped_column(String(50), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    emissoes_co2: Mapped[float | None] = mapped_column(Float)
    emissoes_ch4: Mapped[float | None] = mapped_column(Float)
    emissoes_n2o: Mapped[float | None] = mapped_column(Float)
    emissoes_co2_biogenico: Mapped[float | None] = mapped_column(Float)
    emissoes_ch4_biogenico: Mapped[float | None] = mapped_column(Float)
    emissoes_n2o_biogenico: Mapped[float | None] = mapped_column(Float)
    emissoes_total_tco2e: Mapped[float | None] = mapped_column(Float)
    fator_co2: Mapped[float | None] = mapped_column(Float)
    fator_ch4: Mapped[float | None] = mapped_column(Float)
    fator_n2o: Mapped[float | None] = mapped_column(Float)
    ano_referencia: Mapped[int | None] = mapped_column(Integer)
    descricao: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
