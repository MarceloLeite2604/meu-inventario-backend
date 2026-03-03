from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None


class ProfileResponse(BaseModel):
    id: str
    email: str | None
    full_name: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class UserPermissaoCreate(BaseModel):
    tipo: str
    referencia: str
    organizacao_id: str


class UserPermissaoResponse(BaseModel):
    id: UUID
    user_id: str
    organizacao_id: str
    tipo: str
    referencia: str
    created_at: datetime
    granted_by: str | None

    model_config = {"from_attributes": True}
