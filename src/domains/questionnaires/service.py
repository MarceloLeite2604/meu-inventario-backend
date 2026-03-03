import secrets
from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...util.logger import retrieve_logger
from ...util.rate_limiting import check_rate_limit
from .models import QuestionarioDeslocamento, QuestionarioRespondente, QuestionarioSalvo
from .schemas import DeslocamentoCreate, QuestionarioSalvoCreate, RespostaCreate

_LOGGER = retrieve_logger(__name__)


async def list_questionnaires(
    organizacao_id: UUID | None, session: AsyncSession
) -> list[QuestionarioSalvo]:
    _LOGGER.info("Listing questionnaires for organization %s", organizacao_id)
    query = select(QuestionarioSalvo)
    if organizacao_id:
        query = query.where(QuestionarioSalvo.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(QuestionarioSalvo.created_at.desc()))
    return list(result.scalars().all())


async def get_questionnaire(questionnaire_id: UUID, session: AsyncSession) -> QuestionarioSalvo:
    _LOGGER.info("Retrieving questionnaire %s", questionnaire_id)
    result = await session.execute(
        select(QuestionarioSalvo).where(QuestionarioSalvo.id == questionnaire_id))
    questionnaire = result.scalar_one_or_none()
    if not questionnaire:
        _LOGGER.warning("Questionnaire %s not found", questionnaire_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    return questionnaire


async def get_questionnaire_by_token(
    token: str, session: AsyncSession
) -> QuestionarioSalvo:
    result = await session.execute(
        select(QuestionarioSalvo).where(QuestionarioSalvo.token == token))
    questionnaire = result.scalar_one_or_none()
    if not questionnaire or not questionnaire.ativo:
        _LOGGER.warning("Questionnaire not found or inactive for token")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    return questionnaire


async def create_questionnaire(
    data: QuestionarioSalvoCreate, created_by: str, session: AsyncSession
) -> QuestionarioSalvo:
    _LOGGER.info("Creating questionnaire for organization %s", data.organizacao_id)
    token = secrets.token_urlsafe(32)
    questionnaire = QuestionarioSalvo(
        **data.model_dump(),
        token=token,
        created_by=created_by,
    )
    session.add(questionnaire)
    await session.flush()
    await session.refresh(questionnaire)
    return questionnaire


async def delete_questionnaire(questionnaire_id: UUID, session: AsyncSession) -> None:
    _LOGGER.info("Deleting questionnaire %s", questionnaire_id)
    questionnaire = await get_questionnaire(questionnaire_id, session)
    await session.delete(questionnaire)


async def submit_response(
    token: str,
    data: RespostaCreate,
    request: Request,
    session: AsyncSession,
) -> tuple[QuestionarioRespondente, list[QuestionarioDeslocamento]]:
    _LOGGER.info("Processing questionnaire response for token")
    await check_rate_limit(request, f"submit_response:{token}", session)

    questionnaire = await get_questionnaire_by_token(token, session)

    respondente = QuestionarioRespondente(
        questionario_id=questionnaire.id,
        nome=data.nome,
        email=data.email,
    )
    session.add(respondente)
    await session.flush()
    await session.refresh(respondente)

    deslocamentos = await _save_displacements(
        questionnaire.id, respondente.id, data.deslocamentos, session
    )

    questionnaire.total_deslocamentos = (questionnaire.total_deslocamentos or 0) + len(deslocamentos)
    total_em = sum(deslocamento.emissoes_tco2e_total or 0.0 for deslocamento in deslocamentos)
    questionnaire.total_emissoes = (questionnaire.total_emissoes or 0.0) + total_em

    _LOGGER.info("Saved %s displacements for questionnaire response", len(deslocamentos))
    return respondente, deslocamentos


async def _save_displacements(
    questionario_id: UUID,
    respondente_id: UUID,
    items: list[DeslocamentoCreate],
    session: AsyncSession,
) -> list[QuestionarioDeslocamento]:
    saved: list[QuestionarioDeslocamento] = []
    for item in items:
        deslocamento = QuestionarioDeslocamento(
            questionario_id=questionario_id,
            respondente_id=respondente_id,
            **item.model_dump(),
        )
        session.add(deslocamento)
        saved.append(deslocamento)
    await session.flush()
    for deslocamento in saved:
        await session.refresh(deslocamento)
    return saved
