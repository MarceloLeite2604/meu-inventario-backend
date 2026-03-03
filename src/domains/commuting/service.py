from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    CommutingColaborador,
    CommutingColaboradorMedalha,
    CommutingEmpresa,
    CommutingMedalha,
    CommutingRegistro,
    CommutingTransporteHabitual,
)
from .schemas import (
    CommutingColaboradorCreate,
    CommutingEmpresaCreate,
    CommutingRegistroCreate,
    CommutingTransporteHabitualCreate,
)

# Points awarded per transport type (greener = more points)
_POINTS_BY_TRANSPORT: dict[str, int] = {
    "bicicleta": 50,
    "a_pe": 50,
    "onibus": 30,
    "metro": 30,
    "trem": 30,
    "carro_eletrico": 20,
    "carro_hibrido": 10,
    "carro": 0,
    "moto": 0,
}


def _award_points(tipo_transporte: str, dias_utilizados: int) -> int:
    base = _POINTS_BY_TRANSPORT.get(tipo_transporte.lower(), 0)
    return base * dias_utilizados


# ── Companies ──────────────────────────────────────────────────────────────

async def list_companies(session: AsyncSession) -> list[CommutingEmpresa]:
    result = await session.execute(
        select(CommutingEmpresa).order_by(CommutingEmpresa.nome))
    return list(result.scalars().all())


async def get_company(company_id: UUID, session: AsyncSession) -> CommutingEmpresa:
    result = await session.execute(
        select(CommutingEmpresa).where(CommutingEmpresa.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


async def create_company(
    data: CommutingEmpresaCreate, created_by: str, session: AsyncSession
) -> CommutingEmpresa:
    company = CommutingEmpresa(**data.model_dump(), created_by=created_by)
    session.add(company)
    await session.flush()
    await session.refresh(company)
    return company


# ── Employees (colaboradores) ──────────────────────────────────────────────

async def list_employees(
    company_id: UUID, session: AsyncSession
) -> list[CommutingColaborador]:
    result = await session.execute(
        select(CommutingColaborador).where(
            CommutingColaborador.empresa_id == company_id
        ).order_by(CommutingColaborador.pontos_total.desc()))
    return list(result.scalars().all())


async def get_employee(employee_id: UUID, session: AsyncSession) -> CommutingColaborador:
    result = await session.execute(
        select(CommutingColaborador).where(CommutingColaborador.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


async def create_employee(
    data: CommutingColaboradorCreate, session: AsyncSession
) -> CommutingColaborador:
    employee = CommutingColaborador(**data.model_dump())
    session.add(employee)
    await session.flush()
    await session.refresh(employee)
    return employee


# ── Habitual transport ──────────────────────────────────────────────────────

async def list_habitual_transports(
    employee_id: UUID, session: AsyncSession
) -> list[CommutingTransporteHabitual]:
    result = await session.execute(
        select(CommutingTransporteHabitual).where(
            CommutingTransporteHabitual.colaborador_id == employee_id))
    return list(result.scalars().all())


async def set_habitual_transport(
    employee_id: UUID, data: CommutingTransporteHabitualCreate, session: AsyncSession
) -> CommutingTransporteHabitual:
    transport = CommutingTransporteHabitual(colaborador_id=employee_id, **data.model_dump())
    session.add(transport)
    await session.flush()
    await session.refresh(transport)
    return transport


# ── Commuting records ──────────────────────────────────────────────────────

async def create_record(
    employee_id: UUID, data: CommutingRegistroCreate, session: AsyncSession
) -> CommutingRegistro:
    points = _award_points(data.tipo_transporte, data.dias_utilizados)

    record_data = data.model_dump()
    record_data["colaborador_id"] = employee_id
    record_data["pontos_ganhos"] = points

    record = CommutingRegistro(**record_data)
    session.add(record)

    # Update employee points and streak
    employee = await get_employee(employee_id, session)
    employee.pontos_total += points
    # Level up every 500 points
    employee.nivel = max(1, employee.pontos_total // 500 + 1)

    await session.flush()
    await session.refresh(record)
    return record


async def list_records(
    employee_id: UUID, session: AsyncSession
) -> list[CommutingRegistro]:
    result = await session.execute(
        select(CommutingRegistro).where(
            CommutingRegistro.colaborador_id == employee_id
        ).order_by(CommutingRegistro.semana_inicio.desc()))
    return list(result.scalars().all())


# ── Medals ─────────────────────────────────────────────────────────────────

async def list_medals(session: AsyncSession) -> list[CommutingMedalha]:
    result = await session.execute(
        select(CommutingMedalha).order_by(CommutingMedalha.nome))
    return list(result.scalars().all())


async def list_employee_medals(
    employee_id: UUID, session: AsyncSession
) -> list[CommutingColaboradorMedalha]:
    result = await session.execute(
        select(CommutingColaboradorMedalha)
        .where(CommutingColaboradorMedalha.colaborador_id == employee_id)
        .options(selectinload(CommutingColaboradorMedalha.medalha))
    )
    return list(result.scalars().all())


async def award_medal(
    employee_id: UUID, medal_id: UUID, session: AsyncSession
) -> CommutingColaboradorMedalha:
    # Check if already awarded
    existing = await session.execute(
        select(CommutingColaboradorMedalha).where(
            CommutingColaboradorMedalha.colaborador_id == employee_id,
            CommutingColaboradorMedalha.medalha_id == medal_id,
        ))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medal already awarded to this employee",
        )

    medal_result = await session.execute(
        select(CommutingMedalha).where(CommutingMedalha.id == medal_id))
    medal = medal_result.scalar_one_or_none()
    if not medal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medal not found")

    employee = await get_employee(employee_id, session)
    employee.pontos_total += medal.pontos_bonus

    col_medal = CommutingColaboradorMedalha(
        colaborador_id=employee_id, medalha_id=medal_id)
    session.add(col_medal)
    await session.flush()

    result = await session.execute(
        select(CommutingColaboradorMedalha)
        .where(CommutingColaboradorMedalha.id == col_medal.id)
        .options(selectinload(CommutingColaboradorMedalha.medalha))
    )
    return result.scalar_one()
