import secrets
from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...util.rate_limiting import check_rate_limit
from .models import QuestionarioDeslocamento, QuestionarioRespondente, QuestionarioSalvo
from .schemas import DeslocamentoCreate, QuestionarioSalvoCreate, RespostaCreate


async def list_questionnaires(
    organizacao_id: UUID | None, session: AsyncSession
) -> list[QuestionarioSalvo]:
    query = select(QuestionarioSalvo)
    if organizacao_id:
        query = query.where(QuestionarioSalvo.organizacao_id == organizacao_id)
    result = await session.execute(query.order_by(QuestionarioSalvo.created_at.desc()))
    return list(result.scalars().all())


async def get_questionnaire(questionnaire_id: UUID, session: AsyncSession) -> QuestionarioSalvo:
    result = await session.execute(
        select(QuestionarioSalvo).where(QuestionarioSalvo.id == questionnaire_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    return q


async def get_questionnaire_by_token(
    token: str, session: AsyncSession
) -> QuestionarioSalvo:
    result = await session.execute(
        select(QuestionarioSalvo).where(QuestionarioSalvo.token == token))
    q = result.scalar_one_or_none()
    if not q or not q.ativo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    return q


async def create_questionnaire(
    data: QuestionarioSalvoCreate, created_by: str, session: AsyncSession
) -> QuestionarioSalvo:
    token = secrets.token_urlsafe(32)
    q = QuestionarioSalvo(
        **data.model_dump(),
        token=token,
        created_by=created_by,
    )
    session.add(q)
    await session.flush()
    await session.refresh(q)
    return q


async def delete_questionnaire(questionnaire_id: UUID, session: AsyncSession) -> None:
    q = await get_questionnaire(questionnaire_id, session)
    await session.delete(q)


async def submit_response(
    token: str,
    data: RespostaCreate,
    request: Request,
    session: AsyncSession,
) -> tuple[QuestionarioRespondente, list[QuestionarioDeslocamento]]:
    await check_rate_limit(request, f"submit_response:{token}", session)

    q = await get_questionnaire_by_token(token, session)

    respondente = QuestionarioRespondente(
        questionario_id=q.id,
        nome=data.nome,
        email=data.email,
    )
    session.add(respondente)
    await session.flush()
    await session.refresh(respondente)

    deslocamentos = await _save_displacements(
        q.id, respondente.id, data.deslocamentos, session
    )

    # Update questionnaire aggregates
    q.total_deslocamentos = (q.total_deslocamentos or 0) + len(deslocamentos)
    total_em = sum(d.emissoes_tco2e_total or 0.0 for d in deslocamentos)
    q.total_emissoes = (q.total_emissoes or 0.0) + total_em

    return respondente, deslocamentos


async def _save_displacements(
    questionario_id: UUID,
    respondente_id: UUID,
    items: list[DeslocamentoCreate],
    session: AsyncSession,
) -> list[QuestionarioDeslocamento]:
    saved: list[QuestionarioDeslocamento] = []
    for item in items:
        d = QuestionarioDeslocamento(
            questionario_id=questionario_id,
            respondente_id=respondente_id,
            **item.model_dump(),
        )
        session.add(d)
        saved.append(d)
    await session.flush()
    for d in saved:
        await session.refresh(d)
    return saved
