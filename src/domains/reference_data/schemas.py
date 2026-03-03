from uuid import UUID

from pydantic import BaseModel


class FatorTipoCombustivelResponse(BaseModel):
    id: UUID
    combustivel: str
    ano_referencia: int
    tipo_transporte: str | None
    unidade: str | None
    fator_co2: float | None
    fator_ch4: float | None
    fator_n2o: float | None
    densidade: float | None
    poder_calorifico_inferior: float | None

    model_config = {"from_attributes": True}


class FatorFrotaTipoCombustivelResponse(BaseModel):
    id: UUID
    tipo_veiculo: str
    combustivel: str
    ano_veiculo: int
    ch4_originais: float | None
    ch4_convertida: float | None
    n2o_originais: float | None
    n2o_convertida: float | None

    model_config = {"from_attributes": True}


class FatorEstacionariaResponse(BaseModel):
    id: UUID
    combustivel: str
    ano_referencia: int | None
    co2: float
    unidade: str
    ch4_energia: float | None
    n2o_energia: float | None

    model_config = {"from_attributes": True}


class FatorEmissaoEnergiaResponse(BaseModel):
    id: UUID
    ano: int
    mes: int
    fator_emissao: float

    model_config = {"from_attributes": True}


class FatorEmissaoAereaResponse(BaseModel):
    id: UUID
    ano_referencia: int
    distancia_aerea: str
    acrescimo_rota: float
    co2_aereo_passageiro_km: float
    ch4_aereo_passageiro_km: float
    n2o_aereo_passageiro_km: float

    model_config = {"from_attributes": True}


class FatorTransporteOnibusResponse(BaseModel):
    id: UUID
    ano: int
    tipo_onibus: str
    diesel_co2_pkm: float | None
    diesel_ch4_pkm: float | None
    diesel_n2o_pkm: float | None

    model_config = {"from_attributes": True}


class FatorTratamentoEfluenteResponse(BaseModel):
    id: UUID
    tipo_tratamento: str
    tipo_efluente_aplicavel: str
    categoria: str
    mcf: float
    fator_n2o_default: float | None

    model_config = {"from_attributes": True}


class GwpResponse(BaseModel):
    id: UUID
    nome_ghg: str
    gwp_value: float

    model_config = {"from_attributes": True}


class AeroportoCoordenadaResponse(BaseModel):
    id: UUID
    sigla: str
    nome: str | None
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}


class EquivalenciaVeiculoResponse(BaseModel):
    id: UUID
    transporte: str
    motor: str
    tipo_combustivel: str
    equivalencia: str

    model_config = {"from_attributes": True}
