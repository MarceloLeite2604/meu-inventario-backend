from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmissaoViagemNegocioCreate(BaseModel):
    organizacao_id: UUID | None = None
    tipo_transporte: str
    ano: int
    mes: int
    metodo_calculo: str | None = None
    origin: str | None = None
    destination: str | None = None
    distance: float | None = None
    round_trip: bool | None = None
    tipo_veiculo: str | None = None
    ano_veiculo: int | None = None
    tipo_frota_de_veiculos: str | None = None
    vehicle_subtype: str | None = None
    tipo_onibus: str | None = None
    combustivel: str | None = None
    fuel: str | None = None
    combustivel_fossil: str | None = None
    biocombustivel: str | None = None
    quantidade: float | None = None
    quantidade_fossil: float | None = None
    quantidade_biocombustivel: float | None = None
    quantidade_passageiros: int | None = None
    unidade: str | None = None
    descricao: str | None = None


class EmissaoViagemNegocioResponse(BaseModel):
    id: UUID
    organizacao_id: UUID | None
    tipo_transporte: str
    ano: int
    mes: int
    metodo_calculo: str | None
    origin: str | None
    destination: str | None
    distance: float | None
    round_trip: bool | None
    tipo_veiculo: str | None
    ano_veiculo: int | None
    tipo_frota_de_veiculos: str | None
    vehicle_subtype: str | None
    tipo_onibus: str | None
    combustivel: str | None
    fuel: str | None
    combustivel_fossil: str | None
    biocombustivel: str | None
    quantidade: float | None
    quantidade_fossil: float | None
    quantidade_biocombustivel: float | None
    quantidade_passageiros: int | None
    unidade: str | None
    emissoes_ch4: float | None
    emissoes_co2: float | None
    emissoes_n2o: float | None
    emissoes_aerea_ch4: float | None
    emissoes_aerea_co2: float | None
    emissoes_aerea_n2o: float | None
    emissoes_tco2e_total: float | None
    fator_ch4: float | None
    fator_co2: float | None
    fator_n2o: float | None
    descricao: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DeslocamentoCreate(BaseModel):
    organizacao_id: UUID | None = None
    transport: str
    fuel: str | None = None
    origin: str | None = None
    destination: str | None = None
    distance: float | None = None
    round_trip: bool | None = None
    year: int | None = None
    tipo_frota_de_veiculos: str | None = None
    vehicle_subtype: str | None = None
    combustivel_fossil: str | None = None
    biocombustivel: str | None = None


class DeslocamentoResponse(BaseModel):
    id: UUID
    organizacao_id: UUID | None
    transport: str
    fuel: str | None
    origin: str | None
    destination: str | None
    distance: float | None
    round_trip: bool | None
    year: int | None
    tipo_frota_de_veiculos: str | None
    vehicle_subtype: str | None
    combustivel_fossil: str | None
    biocombustivel: str | None
    emissoes_tco2e_total: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
