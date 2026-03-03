from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrganizacaoCreate(BaseModel):
    nome: str
    ativa: bool = True
    logo_url: str | None = None
    cnpj: str | None = None
    cnae: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    pais: str | None = None
    email_responsavel: str | None = None
    telefone_responsavel: str | None = None
    pessoa_responsavel: str | None = None
    num_funcionarios: int | None = None
    segmento: str | None = None
    descricao_atividades: str | None = None
    website: str | None = None
    organograma_url: str | None = None
    abordagem_consolidacao: str | None = None
    justificativa_abordagem: str | None = None
    limite_organizacional: str | None = None
    modulo_inventario_habilitado: bool = True
    modulo_deslocamentos_habilitado: bool = False


class OrganizacaoUpdate(BaseModel):
    nome: str | None = None
    ativa: bool | None = None
    logo_url: str | None = None
    cnpj: str | None = None
    cnae: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    pais: str | None = None
    email_responsavel: str | None = None
    telefone_responsavel: str | None = None
    pessoa_responsavel: str | None = None
    num_funcionarios: int | None = None
    segmento: str | None = None
    descricao_atividades: str | None = None
    website: str | None = None
    organograma_url: str | None = None
    abordagem_consolidacao: str | None = None
    justificativa_abordagem: str | None = None
    limite_organizacional: str | None = None
    modulo_inventario_habilitado: bool | None = None
    modulo_deslocamentos_habilitado: bool | None = None


class OrganizacaoResponse(BaseModel):
    id: UUID
    nome: str
    ativa: bool
    logo_url: str | None
    cnpj: str | None
    cnae: str | None
    endereco: str | None
    cidade: str | None
    estado: str | None
    cep: str | None
    pais: str | None
    email_responsavel: str | None
    telefone_responsavel: str | None
    pessoa_responsavel: str | None
    num_funcionarios: int | None
    segmento: str | None
    descricao_atividades: str | None
    website: str | None
    organograma_url: str | None
    abordagem_consolidacao: str | None
    justificativa_abordagem: str | None
    limite_organizacional: str | None
    modulo_inventario_habilitado: bool
    modulo_deslocamentos_habilitado: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrganizacaoUsuarioCreate(BaseModel):
    user_id: str
    papel: str


class OrganizacaoUsuarioResponse(BaseModel):
    id: UUID
    organizacao_id: UUID
    user_id: str
    papel: str
    created_at: datetime
    granted_by: str | None

    model_config = {"from_attributes": True}
