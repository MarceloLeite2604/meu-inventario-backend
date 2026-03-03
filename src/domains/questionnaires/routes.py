from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import (
    QuestionarioPublicoResponse,
    QuestionarioSalvoCreate,
    QuestionarioSalvoResponse,
    RespostaCreate,
    RespostaResponse,
)

router = APIRouter(tags=["questionnaires"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


# ── Authenticated management endpoints ─────────────────────────────────────

@router.get("/questionnaires", response_model=list[QuestionarioSalvoResponse])
async def list_questionnaires(
    current_user: CurrentUser,
    session: DatabaseSession,
    organizacao_id: UUID | None = Query(default=None),
):
    return await service.list_questionnaires(organizacao_id, session)


@router.post("/questionnaires", response_model=QuestionarioSalvoResponse, status_code=201)
async def create_questionnaire(
    data: QuestionarioSalvoCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.create_questionnaire(data, current_user.id, session)


@router.get("/questionnaires/{questionnaire_id}", response_model=QuestionarioSalvoResponse)
async def get_questionnaire(
    questionnaire_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.get_questionnaire(questionnaire_id, session)


@router.delete("/questionnaires/{questionnaire_id}", status_code=204)
async def delete_questionnaire(
    questionnaire_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    await service.delete_questionnaire(questionnaire_id, session)


# ── Anonymous public endpoints (no auth) ───────────────────────────────────

@router.get("/public/questionnaires/{token}", response_model=QuestionarioPublicoResponse)
async def get_public_questionnaire(token: str, session: DatabaseSession):
    return await service.get_questionnaire_by_token(token, session)


@router.post(
    "/public/questionnaires/{token}/responses",
    response_model=RespostaResponse,
    status_code=201,
)
async def submit_response(
    token: str,
    data: RespostaCreate,
    request: Request,
    session: DatabaseSession,
):
    respondente, deslocamentos = await service.submit_response(token, data, request, session)
    return RespostaResponse(
        respondente_id=respondente.id,
        deslocamentos=deslocamentos,
    )
