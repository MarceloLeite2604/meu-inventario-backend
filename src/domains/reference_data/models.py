from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...base import Base


class FatorTipoCombustivel(Base):
    __tablename__ = "fatores_tipo_combustivel"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    combustivel: Mapped[str] = mapped_column(String(100), nullable=False)
    ano_referencia: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_transporte: Mapped[str | None] = mapped_column(String(100))
    unidade: Mapped[str | None] = mapped_column(String(50))
    fator_co2: Mapped[float | None] = mapped_column(Float)
    fator_ch4: Mapped[float | None] = mapped_column(Float)
    fator_n2o: Mapped[float | None] = mapped_column(Float)
    densidade: Mapped[float | None] = mapped_column(Float)
    poder_calorifico_inferior: Mapped[float | None] = mapped_column(Float)
    referencia: Mapped[str | None] = mapped_column(Text)


class FatorFrotaTipoCombustivel(Base):
    __tablename__ = "fatores_frota_tipo_combustivel"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tipo_veiculo: Mapped[str] = mapped_column(String(100), nullable=False)
    combustivel: Mapped[str] = mapped_column(String(100), nullable=False)
    ano_veiculo: Mapped[int] = mapped_column(Integer, nullable=False)
    ch4_originais: Mapped[float | None] = mapped_column(Float)
    ch4_convertida: Mapped[float | None] = mapped_column(Float)
    n2o_originais: Mapped[float | None] = mapped_column(Float)
    n2o_convertida: Mapped[float | None] = mapped_column(Float)


class FatorEstacionaria(Base):
    __tablename__ = "fatores_estacionaria"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    combustivel: Mapped[str] = mapped_column(String(100), nullable=False)
    ano_referencia: Mapped[int | None] = mapped_column(Integer)
    co2: Mapped[float] = mapped_column(Float, nullable=False)
    unidade: Mapped[str] = mapped_column(String(50), nullable=False)
    ch4_energia: Mapped[float | None] = mapped_column(Float)
    ch4_manufatura_construcao: Mapped[float | None] = mapped_column(Float)
    ch4_comercial_institucional: Mapped[float | None] = mapped_column(Float)
    ch4_residencial_agro_pesca: Mapped[float | None] = mapped_column(Float)
    n2o_energia: Mapped[float | None] = mapped_column(Float)
    n2o_manufatura_construcao: Mapped[float | None] = mapped_column(Float)
    n2o_comercial_institucional: Mapped[float | None] = mapped_column(Float)
    n2o_residencial_agro_pesca: Mapped[float | None] = mapped_column(Float)


class FatorEmissaoEnergia(Base):
    __tablename__ = "fatores_emissao_energia"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    fator_emissao: Mapped[float] = mapped_column(Float, nullable=False)


class FatorEmissaoAerea(Base):
    __tablename__ = "fatores_emissao_aereas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ano_referencia: Mapped[int] = mapped_column(Integer, nullable=False)
    distancia_aerea: Mapped[str] = mapped_column(String(50), nullable=False)
    acrescimo_rota: Mapped[float] = mapped_column(Float, nullable=False)
    co2_aereo_passageiro_km: Mapped[float] = mapped_column(Float, nullable=False)
    ch4_aereo_passageiro_km: Mapped[float] = mapped_column(Float, nullable=False)
    n2o_aereo_passageiro_km: Mapped[float] = mapped_column(Float, nullable=False)


class FatorTransporteOnibus(Base):
    __tablename__ = "fatores_transporte_onibus"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_onibus: Mapped[str] = mapped_column(String(100), nullable=False)
    diesel_co2_pkm: Mapped[float | None] = mapped_column(Float)
    diesel_ch4_pkm: Mapped[float | None] = mapped_column(Float)
    diesel_n2o_pkm: Mapped[float | None] = mapped_column(Float)
    biodiesel_co2_pkm: Mapped[float | None] = mapped_column(Float)
    biodiesel_ch4_pkm: Mapped[float | None] = mapped_column(Float)
    biodiesel_n2o_pkm: Mapped[float | None] = mapped_column(Float)
    fator_consumo_l_pkm: Mapped[float | None] = mapped_column(Float)
    fator_defra_kgco2e_pkm: Mapped[float | None] = mapped_column(Float)


class FatorTratamentoEfluente(Base):
    __tablename__ = "fatores_tratamento_efluentes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tipo_tratamento: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_efluente_aplicavel: Mapped[str] = mapped_column(String(50), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    mcf: Mapped[float] = mapped_column(Float, nullable=False)
    fator_n2o_default: Mapped[float | None] = mapped_column(Float)
    descricao: Mapped[str | None] = mapped_column(Text)
    referencia: Mapped[str | None] = mapped_column(Text)


class FatorVariavelGhg(Base):
    __tablename__ = "fatores_variaveis_ghg"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int | None] = mapped_column(Integer)
    perc_etanol_gasolina: Mapped[float | None] = mapped_column(Float)
    perc_biodiesel_diesel: Mapped[float | None] = mapped_column(Float)


class Gwp(Base):
    __tablename__ = "gwp"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nome_ghg: Mapped[str] = mapped_column(String(100), nullable=False)
    gwp_value: Mapped[float] = mapped_column(Float, nullable=False)


class ComposicaoCombustivel(Base):
    __tablename__ = "composicao_combustiveis"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tipo_combustivel: Mapped[str] = mapped_column(String(100), nullable=False)
    combustivel_fossil: Mapped[str | None] = mapped_column(String(100))
    biocombustivel: Mapped[str | None] = mapped_column(String(100))


class ConsumoUnidadeMedida(Base):
    __tablename__ = "consumo_unidade_medida"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tipo_frota_veiculos: Mapped[str] = mapped_column(String(100), nullable=False)
    ano_veiculo: Mapped[int] = mapped_column(Integer, nullable=False)
    media_por_unidade: Mapped[float] = mapped_column(Float, nullable=False)


class EquivalenciaVeiculo(Base):
    __tablename__ = "equivalencia_veiculos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transporte: Mapped[str] = mapped_column(String(100), nullable=False)
    motor: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_combustivel: Mapped[str] = mapped_column(String(100), nullable=False)
    equivalencia: Mapped[str] = mapped_column(String(100), nullable=False)


class AeroportoCoordenada(Base):
    __tablename__ = "aeroportos_coordenadas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sigla: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    nome: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    graus_lat: Mapped[float | None] = mapped_column(Float)
    minutos_lat: Mapped[float | None] = mapped_column(Float)
    segundos_lat: Mapped[float | None] = mapped_column(Float)
    direcao_lat: Mapped[str | None] = mapped_column(String(1))
    graus_lon: Mapped[float | None] = mapped_column(Float)
    minutos_lon: Mapped[float | None] = mapped_column(Float)
    segundos_lon: Mapped[float | None] = mapped_column(Float)
    direcao_lon: Mapped[str | None] = mapped_column(String(1))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class TipoEfluenteIndustrial(Base):
    __tablename__ = "tipos_efluentes_industriais"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    setor_industrial: Mapped[str] = mapped_column(String(255), nullable=False)
    dqo_default: Mapped[float] = mapped_column(Float, nullable=False)
    dqo_minimo: Mapped[float | None] = mapped_column(Float)
    dqo_maximo: Mapped[float | None] = mapped_column(Float)
    referencia: Mapped[str | None] = mapped_column(Text)


class TransporteMetro(Base):
    __tablename__ = "transporte_metro"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    g_co2_passageiro_km: Mapped[float] = mapped_column(Float, nullable=False)


class TransporteTrem(Base):
    __tablename__ = "transporte_trem"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    g_co2_passageiro_km: Mapped[float] = mapped_column(Float, nullable=False)
