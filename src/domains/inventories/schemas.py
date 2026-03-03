from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class InventarioCreate(BaseModel):
    organizacao_id: UUID
    nome: str
    descricao: str | None = None
    ano_base: int
    status: str | None = None
    data_inicio: str | None = None
    data_finalizacao: str | None = None


class InventarioUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    status: str | None = None
    data_inicio: str | None = None
    data_finalizacao: str | None = None


class InventarioResponse(BaseModel):
    id: UUID
    organizacao_id: UUID
    nome: str
    descricao: str | None
    ano_base: int
    status: str | None
    data_inicio: str | None
    data_finalizacao: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}
