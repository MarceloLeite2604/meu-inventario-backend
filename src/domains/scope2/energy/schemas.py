from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UnidadeConsumidoraCreate(BaseModel):
    organizacao_id: UUID
    nome: str
    numero_uc: str | None = None
    endereco: str | None = None
    distribuidora: str | None = None
    ativa: bool = True


class UnidadeConsumidoraResponse(BaseModel):
    id: UUID
    organizacao_id: UUID
    nome: str
    numero_uc: str | None
    endereco: str | None
    distribuidora: str | None
    ativa: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsumoEnergiaCreate(BaseModel):
    organizacao_id: UUID | None = None
    unidade_consumidora_id: UUID | None = None
    consumo_mwh: float
    ano: int
    mes: int
    descricao: str | None = None


class ConsumoEnergiaResponse(BaseModel):
    id: UUID
    organizacao_id: UUID | None
    unidade_consumidora_id: UUID | None
    consumo_mwh: float
    ano: int
    mes: int
    emissoes_energia_tco2e: float | None
    descricao: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvidenciaConsumoEnergiaCreate(BaseModel):
    arquivo_url: str
    nome_arquivo_original: str
    tipo_documento: str = "fatura"
    observacoes: str | None = None


class EvidenciaConsumoEnergiaResponse(BaseModel):
    id: UUID
    consumo_energia_id: UUID
    organizacao_id: UUID
    arquivo_url: str
    nome_arquivo_original: str
    tipo_documento: str
    observacoes: str | None
    uploaded_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReprocessResponse(BaseModel):
    reprocessados: int
