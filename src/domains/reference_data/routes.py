from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import (
    AeroportoCoordenadaResponse,
    EquivalenciaVeiculoResponse,
    FatorEmissaoAereaResponse,
    FatorEmissaoEnergiaResponse,
    FatorEstacionariaResponse,
    FatorFrotaTipoCombustivelResponse,
    FatorTipoCombustivelResponse,
    FatorTratamentoEfluenteResponse,
    FatorTransporteOnibusResponse,
    GwpResponse,
)

router = APIRouter(prefix="/reference-data", tags=["reference-data"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get("/fuel-type-factors", response_model=list[FatorTipoCombustivelResponse])
async def list_fuel_type_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_fuel_type_factors(session)


@router.get("/fleet-fuel-factors", response_model=list[FatorFrotaTipoCombustivelResponse])
async def list_fleet_fuel_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_fleet_fuel_factors(session)


@router.get("/stationary-factors", response_model=list[FatorEstacionariaResponse])
async def list_stationary_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_stationary_factors(session)


@router.get("/energy-factors", response_model=list[FatorEmissaoEnergiaResponse])
async def list_energy_factors(
    current_user: CurrentUser,
    session: DatabaseSession,
    ano: int | None = Query(default=None),
):
    return await service.list_energy_factors(ano, session)


@router.get("/aerial-factors", response_model=list[FatorEmissaoAereaResponse])
async def list_aerial_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_aerial_factors(session)


@router.get("/bus-factors", response_model=list[FatorTransporteOnibusResponse])
async def list_bus_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_bus_factors(session)


@router.get("/effluent-treatment-factors", response_model=list[FatorTratamentoEfluenteResponse])
async def list_effluent_treatment_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_effluent_treatment_factors(session)


@router.get("/gwp", response_model=list[GwpResponse])
async def list_gwp(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_gwp(session)


@router.get("/airports", response_model=list[AeroportoCoordenadaResponse])
async def list_airports(
    current_user: CurrentUser,
    session: DatabaseSession,
    q: str | None = Query(default=None, description="Filter by IATA code or name"),
):
    return await service.list_airports(q, session)


@router.get("/vehicle-equivalences", response_model=list[EquivalenciaVeiculoResponse])
async def list_vehicle_equivalences(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_vehicle_equivalences(session)
