from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import (
    CommutingColaboradorCreate,
    CommutingColaboradorMedalhaResponse,
    CommutingColaboradorResponse,
    CommutingEmpresaCreate,
    CommutingEmpresaResponse,
    CommutingMedalhaResponse,
    CommutingRegistroCreate,
    CommutingRegistroResponse,
    CommutingTransporteHabitualCreate,
    CommutingTransporteHabitualResponse,
)

router = APIRouter(prefix="/commuting", tags=["commuting"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


# ── Companies ───────────────────────────────────────────────────────────────

@router.get("/companies", response_model=list[CommutingEmpresaResponse])
async def list_companies(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_companies(session)


@router.post("/companies", response_model=CommutingEmpresaResponse, status_code=201)
async def create_company(
    data: CommutingEmpresaCreate, current_user: CurrentUser, session: DatabaseSession
):
    return await service.create_company(data, current_user.id, session)


# ── Employees ───────────────────────────────────────────────────────────────

@router.get("/companies/{company_id}/employees", response_model=list[CommutingColaboradorResponse])
async def list_employees(
    company_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_employees(company_id, session)


@router.post(
    "/companies/{company_id}/employees",
    response_model=CommutingColaboradorResponse,
    status_code=201,
)
async def create_employee(
    company_id: UUID,
    data: CommutingColaboradorCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    data.empresa_id = company_id
    return await service.create_employee(data, session)


@router.get(
    "/companies/{company_id}/employees/{employee_id}",
    response_model=CommutingColaboradorResponse,
)
async def get_employee(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_employee(employee_id, session)


# ── Habitual transport ──────────────────────────────────────────────────────

@router.get(
    "/companies/{company_id}/employees/{employee_id}/habitual-transports",
    response_model=list[CommutingTransporteHabitualResponse],
)
async def list_habitual_transports(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_habitual_transports(employee_id, session)


@router.post(
    "/companies/{company_id}/employees/{employee_id}/habitual-transports",
    response_model=CommutingTransporteHabitualResponse,
    status_code=201,
)
async def set_habitual_transport(
    company_id: UUID,
    employee_id: UUID,
    data: CommutingTransporteHabitualCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.set_habitual_transport(employee_id, data, session)


# ── Records ─────────────────────────────────────────────────────────────────

@router.get(
    "/companies/{company_id}/employees/{employee_id}/records",
    response_model=list[CommutingRegistroResponse],
)
async def list_records(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_records(employee_id, session)


@router.post(
    "/companies/{company_id}/employees/{employee_id}/records",
    response_model=CommutingRegistroResponse,
    status_code=201,
)
async def create_record(
    company_id: UUID,
    employee_id: UUID,
    data: CommutingRegistroCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    data.colaborador_id = employee_id
    return await service.create_record(employee_id, data, session)


# ── Medals ──────────────────────────────────────────────────────────────────

@router.get("/medals", response_model=list[CommutingMedalhaResponse])
async def list_medals(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_medals(session)


@router.get(
    "/companies/{company_id}/employees/{employee_id}/medals",
    response_model=list[CommutingColaboradorMedalhaResponse],
)
async def list_employee_medals(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_employee_medals(employee_id, session)


@router.post(
    "/companies/{company_id}/employees/{employee_id}/medals/{medal_id}",
    response_model=CommutingColaboradorMedalhaResponse,
    status_code=201,
)
async def award_medal(
    company_id: UUID,
    employee_id: UUID,
    medal_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.award_medal(employee_id, medal_id, session)
