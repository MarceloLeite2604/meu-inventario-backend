from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....base import Base


class EmissaoViagemNegocio(Base):
    __tablename__ = "emissoes_viagens_negocios"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organizacao_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="SET NULL"), index=True)
    tipo_transporte: Mapped[str] = mapped_column(String(50), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    metodo_calculo: Mapped[str | None] = mapped_column(String(50))
    origin: Mapped[str | None] = mapped_column(String(10))
    destination: Mapped[str | None] = mapped_column(String(10))
    distance: Mapped[float | None] = mapped_column(Float)
    round_trip: Mapped[bool | None] = mapped_column(Boolean)
    tipo_veiculo: Mapped[str | None] = mapped_column(String(100))
    ano_veiculo: Mapped[int | None] = mapped_column(Integer)
    tipo_frota_de_veiculos: Mapped[str | None] = mapped_column(String(100))
    vehicle_subtype: Mapped[str | None] = mapped_column(String(100))
    tipo_onibus: Mapped[str | None] = mapped_column(String(100))
    combustivel: Mapped[str | None] = mapped_column(String(100))
    fuel: Mapped[str | None] = mapped_column(String(100))
    combustivel_fossil: Mapped[str | None] = mapped_column(String(100))
    biocombustivel: Mapped[str | None] = mapped_column(String(100))
    quantidade: Mapped[float | None] = mapped_column(Float)
    quantidade_fossil: Mapped[float | None] = mapped_column(Float)
    quantidade_biocombustivel: Mapped[float | None] = mapped_column(Float)
    quantidade_passageiros: Mapped[int | None] = mapped_column(Integer)
    unidade: Mapped[str | None] = mapped_column(String(50))
    emissoes_ch4: Mapped[float | None] = mapped_column(Float)
    emissoes_co2: Mapped[float | None] = mapped_column(Float)
    emissoes_n2o: Mapped[float | None] = mapped_column(Float)
    emissoes_ch4_biogenico: Mapped[float | None] = mapped_column(Float)
    emissoes_co2_biogenico: Mapped[float | None] = mapped_column(Float)
    emissoes_n2o_biogenico: Mapped[float | None] = mapped_column(Float)
    emissoes_aerea_ch4: Mapped[float | None] = mapped_column(Float)
    emissoes_aerea_co2: Mapped[float | None] = mapped_column(Float)
    emissoes_aerea_n2o: Mapped[float | None] = mapped_column(Float)
    emissoes_tco2e_total: Mapped[float | None] = mapped_column(Float)
    fator_ch4: Mapped[float | None] = mapped_column(Float)
    fator_co2: Mapped[float | None] = mapped_column(Float)
    fator_n2o: Mapped[float | None] = mapped_column(Float)
    descricao: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Deslocamento(Base):
    __tablename__ = "deslocamentos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organizacao_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="SET NULL"), index=True)
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
