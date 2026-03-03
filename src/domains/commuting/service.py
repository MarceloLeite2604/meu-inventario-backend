from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...util.logger import retrieve_logger
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

_LOGGER = retrieve_logger(__name__)

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


async def list_companies(session: AsyncSession) -> list[CommutingEmpresa]:
    _LOGGER.info("Listing all commuting companies")
    result = await session.execute(
        select(CommutingEmpresa).order_by(CommutingEmpresa.nome))
    return list(result.scalars().all())


async def get_company(company_id: UUID, session: AsyncSession) -> CommutingEmpresa:
    _LOGGER.info("Retrieving commuting company %s", company_id)
    result = await session.execute(
        select(CommutingEmpresa).where(CommutingEmpresa.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        _LOGGER.warning("Commuting company %s not found", company_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


async def create_company(
    data: CommutingEmpresaCreate, created_by: str, session: AsyncSession
) -> CommutingEmpresa:
    _LOGGER.info("Creating commuting company with name %s", data.nome)
    company = CommutingEmpresa(**data.model_dump(), created_by=created_by)
    session.add(company)
    await session.flush()
    await session.refresh(company)
    return company


async def list_employees(
    company_id: UUID, session: AsyncSession
) -> list[CommutingColaborador]:
    _LOGGER.info("Listing employees for company %s", company_id)
    result = await session.execute(
        select(CommutingColaborador).where(
            CommutingColaborador.empresa_id == company_id
        ).order_by(CommutingColaborador.pontos_total.desc()))
    return list(result.scalars().all())


async def get_employee(employee_id: UUID, session: AsyncSession) -> CommutingColaborador:
    _LOGGER.info("Retrieving employee %s", employee_id)
    result = await session.execute(
        select(CommutingColaborador).where(CommutingColaborador.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        _LOGGER.warning("Employee %s not found", employee_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


async def create_employee(
    data: CommutingColaboradorCreate, session: AsyncSession
) -> CommutingColaborador:
    _LOGGER.info("Creating employee for company %s", data.empresa_id)
    employee = CommutingColaborador(**data.model_dump())
    session.add(employee)
    await session.flush()
    await session.refresh(employee)
    return employee


async def list_habitual_transports(
    employee_id: UUID, session: AsyncSession
) -> list[CommutingTransporteHabitual]:
    _LOGGER.info("Listing habitual transports for employee %s", employee_id)
    result = await session.execute(
        select(CommutingTransporteHabitual).where(
            CommutingTransporteHabitual.colaborador_id == employee_id))
    return list(result.scalars().all())


async def set_habitual_transport(
    employee_id: UUID, data: CommutingTransporteHabitualCreate, session: AsyncSession
) -> CommutingTransporteHabitual:
    _LOGGER.info("Setting habitual transport %s for employee %s", data.tipo_transporte, employee_id)
    transport = CommutingTransporteHabitual(colaborador_id=employee_id, **data.model_dump())
    session.add(transport)
    await session.flush()
    await session.refresh(transport)
    return transport


async def create_record(
    employee_id: UUID, data: CommutingRegistroCreate, session: AsyncSession
) -> CommutingRegistro:
    points = _award_points(data.tipo_transporte, data.dias_utilizados)
    _LOGGER.info(
        "Creating commuting record for employee %s, transport %s, points awarded: %s",
        employee_id, data.tipo_transporte, points,
    )

    record_data = data.model_dump()
    record_data["colaborador_id"] = employee_id
    record_data["pontos_ganhos"] = points

    record = CommutingRegistro(**record_data)
    session.add(record)

    employee = await get_employee(employee_id, session)
    employee.pontos_total += points
    employee.nivel = max(1, employee.pontos_total // 500 + 1)

    await session.flush()
    await session.refresh(record)
    return record


async def list_records(
    employee_id: UUID, session: AsyncSession
) -> list[CommutingRegistro]:
    _LOGGER.info("Listing commuting records for employee %s", employee_id)
    result = await session.execute(
        select(CommutingRegistro).where(
            CommutingRegistro.colaborador_id == employee_id
        ).order_by(CommutingRegistro.semana_inicio.desc()))
    return list(result.scalars().all())


async def list_medals(session: AsyncSession) -> list[CommutingMedalha]:
    _LOGGER.info("Listing all medals")
    result = await session.execute(
        select(CommutingMedalha).order_by(CommutingMedalha.nome))
    return list(result.scalars().all())


async def list_employee_medals(
    employee_id: UUID, session: AsyncSession
) -> list[CommutingColaboradorMedalha]:
    _LOGGER.info("Listing medals for employee %s", employee_id)
    result = await session.execute(
        select(CommutingColaboradorMedalha)
        .where(CommutingColaboradorMedalha.colaborador_id == employee_id)
        .options(selectinload(CommutingColaboradorMedalha.medalha))
    )
    return list(result.scalars().all())


async def award_medal(
    employee_id: UUID, medal_id: UUID, session: AsyncSession
) -> CommutingColaboradorMedalha:
    _LOGGER.info("Awarding medal %s to employee %s", medal_id, employee_id)
    existing = await session.execute(
        select(CommutingColaboradorMedalha).where(
            CommutingColaboradorMedalha.colaborador_id == employee_id,
            CommutingColaboradorMedalha.medalha_id == medal_id,
        ))
    if existing.scalar_one_or_none():
        _LOGGER.warning("Medal %s already awarded to employee %s", medal_id, employee_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Medal already awarded to this employee",
        )

    medal_result = await session.execute(
        select(CommutingMedalha).where(CommutingMedalha.id == medal_id))
    medal = medal_result.scalar_one_or_none()
    if not medal:
        _LOGGER.warning("Medal %s not found", medal_id)
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
