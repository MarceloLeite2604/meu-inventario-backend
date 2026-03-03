from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class QuestionarioSalvoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    organizacao_id: UUID | None = None


class QuestionarioSalvoResponse(BaseModel):
    id: UUID
    nome: str
    descricao: str | None
    organizacao_id: UUID | None
    token: str
    ativo: bool
    total_deslocamentos: int | None
    total_emissoes: float | None
    created_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionarioPublicoResponse(BaseModel):
    """Reduced view for anonymous respondents — omits org details."""
    id: UUID
    nome: str
    descricao: str | None
    ativo: bool

    model_config = {"from_attributes": True}


class DeslocamentoCreate(BaseModel):
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
    questionario_id: UUID
    respondente_id: UUID | None
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


class RespostaCreate(BaseModel):
    """Full questionnaire response submitted by an anonymous respondent."""
    nome: str
    email: EmailStr
    deslocamentos: list[DeslocamentoCreate]


class RespostaResponse(BaseModel):
    respondente_id: UUID
    deslocamentos: list[DeslocamentoResponse]
