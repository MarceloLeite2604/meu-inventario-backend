from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class CommutingEmpresaCreate(BaseModel):
    nome: str
    dominio_email: str
    logo_url: str | None = None
    cidade: str | None = None
    estado: str | None = None
    ativa: bool = True


class CommutingEmpresaResponse(BaseModel):
    id: UUID
    nome: str
    dominio_email: str
    logo_url: str | None
    cidade: str | None
    estado: str | None
    ativa: bool
    created_at: datetime
    created_by: str | None

    model_config = {"from_attributes": True}


class CommutingColaboradorCreate(BaseModel):
    user_id: str
    empresa_id: UUID
    nome: str
    departamento: str | None = None
    avatar_url: str | None = None


class CommutingColaboradorResponse(BaseModel):
    id: UUID
    user_id: str
    empresa_id: UUID
    nome: str
    departamento: str | None
    avatar_url: str | None
    pontos_total: int
    nivel: int
    streak_semanas: int
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CommutingTransporteHabitualCreate(BaseModel):
    tipo_transporte: str
    combustivel: str | None = None
    subtipo_veiculo: str | None = None
    distancia_km: float
    ida_e_volta: bool = True
    dias_por_semana: int = 5
    principal: bool = True


class CommutingTransporteHabitualResponse(BaseModel):
    id: UUID
    colaborador_id: UUID
    tipo_transporte: str
    combustivel: str | None
    subtipo_veiculo: str | None
    distancia_km: float
    ida_e_volta: bool
    dias_por_semana: int
    principal: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CommutingRegistroCreate(BaseModel):
    colaborador_id: UUID
    semana_inicio: date
    tipo_transporte: str
    combustivel: str | None = None
    distancia_km: float
    dias_utilizados: int = 1


class CommutingRegistroResponse(BaseModel):
    id: UUID
    colaborador_id: UUID
    semana_inicio: date
    tipo_transporte: str
    combustivel: str | None
    distancia_km: float
    dias_utilizados: int
    emissoes_tco2e: float | None
    pontos_ganhos: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CommutingMedalhaResponse(BaseModel):
    id: UUID
    nome: str
    descricao: str
    icone: str
    criterio: str
    pontos_bonus: int

    model_config = {"from_attributes": True}


class CommutingColaboradorMedalhaResponse(BaseModel):
    id: UUID
    colaborador_id: UUID
    medalha_id: UUID
    conquistada_em: datetime
    medalha: CommutingMedalhaResponse

    model_config = {"from_attributes": True}
