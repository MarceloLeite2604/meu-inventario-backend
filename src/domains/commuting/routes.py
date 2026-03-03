from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...authentication import CurrentUser
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


@router.get(
    "/companies",
    response_model=list[CommutingEmpresaResponse],
    summary="List commuting companies",
    description="Returns all companies registered in the commuting module.",
)
async def list_companies(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_companies(session)


@router.post(
    "/companies",
    response_model=CommutingEmpresaResponse,
    status_code=201,
    summary="Create commuting company",
    description="Creates a new company in the commuting module.",
)
async def create_company(
    data: CommutingEmpresaCreate, current_user: CurrentUser, session: DatabaseSession
):
    return await service.create_company(data, current_user.id, session)


@router.get(
    "/companies/{company_id}/employees",
    response_model=list[CommutingColaboradorResponse],
    summary="List employees",
    description="Returns all employees for the specified company.",
)
async def list_employees(
    company_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_employees(company_id, session)


@router.post(
    "/companies/{company_id}/employees",
    response_model=CommutingColaboradorResponse,
    status_code=201,
    summary="Create employee",
    description="Creates a new employee for the specified company.",
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
    summary="Get employee",
    description="Returns a single employee by ID.",
)
async def get_employee(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.get_employee(employee_id, session)


@router.get(
    "/companies/{company_id}/employees/{employee_id}/habitual-transports",
    response_model=list[CommutingTransporteHabitualResponse],
    summary="List habitual transports",
    description="Returns the habitual transport modes for the specified employee.",
)
async def list_habitual_transports(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_habitual_transports(employee_id, session)


@router.post(
    "/companies/{company_id}/employees/{employee_id}/habitual-transports",
    response_model=CommutingTransporteHabitualResponse,
    status_code=201,
    summary="Set habitual transport",
    description="Sets a habitual transport mode for the specified employee.",
)
async def set_habitual_transport(
    company_id: UUID,
    employee_id: UUID,
    data: CommutingTransporteHabitualCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.set_habitual_transport(employee_id, data, session)


@router.get(
    "/companies/{company_id}/employees/{employee_id}/records",
    response_model=list[CommutingRegistroResponse],
    summary="List commuting records",
    description="Returns all commuting records for the specified employee.",
)
async def list_records(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_records(employee_id, session)


@router.post(
    "/companies/{company_id}/employees/{employee_id}/records",
    response_model=CommutingRegistroResponse,
    status_code=201,
    summary="Create commuting record",
    description="Creates a commuting record and awards points for sustainable transport.",
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


@router.get(
    "/medals",
    response_model=list[CommutingMedalhaResponse],
    summary="List medals",
    description="Returns all available commuting medals.",
)
async def list_medals(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_medals(session)


@router.get(
    "/companies/{company_id}/employees/{employee_id}/medals",
    response_model=list[CommutingColaboradorMedalhaResponse],
    summary="List employee medals",
    description="Returns all medals awarded to the specified employee.",
)
async def list_employee_medals(
    company_id: UUID, employee_id: UUID, current_user: CurrentUser, session: DatabaseSession
):
    return await service.list_employee_medals(employee_id, session)


@router.post(
    "/companies/{company_id}/employees/{employee_id}/medals/{medal_id}",
    response_model=CommutingColaboradorMedalhaResponse,
    status_code=201,
    summary="Award medal to employee",
    description="Awards a medal to the specified employee.",
)
async def award_medal(
    company_id: UUID,
    employee_id: UUID,
    medal_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    return await service.award_medal(employee_id, medal_id, session)
