from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmissaoFugitivaCreate(BaseModel):
    organizacao_id: UUID | None = None
    gas: str
    quantidade: float
    ano: int
    mes: int
    descricao: str | None = None


class EmissaoFugitivaResponse(BaseModel):
    id: UUID
    organizacao_id: UUID | None
    gas: str
    quantidade: float
    gwp_value: float
    emissoes_tco2e: float
    ano: int
    mes: int
    descricao: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
