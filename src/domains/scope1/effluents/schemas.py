from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmissaoEfluenteCreate(BaseModel):
    inventario_id: UUID | None = None
    organizacao_id: UUID | None = None
    tipo_efluente: str
    tipo_tratamento: str | None = None
    tipo_tratamento_2: str | None = None
    tipo_disposicao_final: str | None = None
    volume_efluente: float | None = None
    unidade_carga_organica: str | None = None
    carga_organica_entrada: float | None = None
    carga_organica_lodo: float | None = None
    nitrogenio_efluente: float | None = None
    efluente_lancado_ambiente: bool | None = None
    tratamento_sequencial: bool | None = None
    mcf_tratamento: float | None = None
    mcf_tratamento_2: float | None = None
    mcf_disposicao: float | None = None
    ch4_recuperado: float | None = None
    ano: int
    setor_industrial: str | None = None
    descricao: str | None = None


class EmissaoEfluenteResponse(BaseModel):
    id: UUID
    inventario_id: UUID | None
    organizacao_id: UUID | None
    tipo_efluente: str
    ano: int
    emissoes_ch4: float | None
    emissoes_co2_biogenico: float | None
    emissoes_n2o: float | None
    emissoes_tco2e: float | None
    descricao: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
