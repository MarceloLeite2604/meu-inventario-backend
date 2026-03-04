from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmissaoEstacionariaCreate(BaseModel):
    organizacao_id: UUID | None = None
    combustivel: str
    combustivel_fossil: str | None = None
    biocombustivel: str | None = None
    quantidade: float
    quantidade_fossil: float | None = None
    quantidade_biocombustivel: float | None = None
    unidade: str
    ano: int
    mes: int
    descricao: str | None = None


class EmissaoEstacionariaResponse(BaseModel):
    id: UUID
    organizacao_id: UUID | None
    combustivel: str
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


class SpedItem(BaseModel):
    codigo: str
    descricao: str
    quantidade: float
    unidade: str
    combustivel_fossil_sugerido: str | None = None


class SpedPreviewResponse(BaseModel):
    items: list[SpedItem]


class SpedImportItem(BaseModel):
    codigo: str
    descricao: str
    quantidade: float
    unidade: str
    combustivel_fossil: str


class SpedImportRequest(BaseModel):
    organizacao_id: UUID | None = None
    ano: int
    mes: int
    descricao: str | None = None
    items: list[SpedImportItem]


class SpedImportResponse(BaseModel):
    criados: int
    registros: list[EmissaoEstacionariaResponse]


class ReprocessResponse(BaseModel):
    reprocessados: int
