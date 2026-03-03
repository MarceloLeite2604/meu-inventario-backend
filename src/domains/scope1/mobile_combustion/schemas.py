from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmissaoCombustaoMovelCreate(BaseModel):
    inventario_id: UUID | None = None
    organizacao_id: UUID | None = None
    metodo_calculo: str
    tipo_veiculo: str | None = None
    ano_veiculo: int | None = None
    combustivel: str | None = None
    combustivel_fossil: str | None = None
    biocombustivel: str | None = None
    quantidade: float
    quantidade_fossil: float | None = None
    quantidade_biocombustivel: float | None = None
    unidade: str
    ano: int
    mes: int
    descricao: str | None = None


class EmissaoCombustaoMovelResponse(BaseModel):
    id: UUID
    inventario_id: UUID | None
    organizacao_id: UUID | None
    metodo_calculo: str
    tipo_veiculo: str | None
    ano_veiculo: int | None
    combustivel: str | None
    quantidade: float
    unidade: str
    ano: int
    mes: int
    emissoes_co2: float | None
    emissoes_ch4: float | None
    emissoes_n2o: float | None
    emissoes_co2_biogenico: float | None
    emissoes_ch4_biogenico: float | None
    emissoes_n2o_biogenico: float | None
    emissoes_total_tco2e: float | None
    fator_co2: float | None
    fator_ch4: float | None
    fator_n2o: float | None
    descricao: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
