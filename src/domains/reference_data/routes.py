from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from ...authentication import CurrentUser
from ...database import retrieve_database
from . import service
from .schemas import (
    AeroportoCoordenadaResponse,
    AirportImportResponse,
    EnergyFactorImportResponse,
    EquivalenciaVeiculoResponse,
    FatorEmissaoAereaResponse,
    FatorEmissaoEnergiaResponse,
    FatorEstacionariaResponse,
    FatorFrotaTipoCombustivelResponse,
    FatorTipoCombustivelResponse,
    FatorTratamentoEfluenteResponse,
    FatorTransporteOnibusResponse,
    GwpResponse,
    VehicleFactorImportResponse,
)

router = APIRouter(prefix="/reference-data", tags=["reference-data"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "/fuel-type-factors",
    response_model=list[FatorTipoCombustivelResponse],
    summary="List fuel type emission factors",
    description="Returns all emission factors by fuel type.",
)
async def list_fuel_type_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_fuel_type_factors(session)


@router.get(
    "/fleet-fuel-factors",
    response_model=list[FatorFrotaTipoCombustivelResponse],
    summary="List fleet fuel emission factors",
    description="Returns all fleet fuel emission factors.",
)
async def list_fleet_fuel_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_fleet_fuel_factors(session)


@router.get(
    "/stationary-factors",
    response_model=list[FatorEstacionariaResponse],
    summary="List stationary combustion factors",
    description="Returns all stationary combustion emission factors.",
)
async def list_stationary_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_stationary_factors(session)


@router.get(
    "/energy-factors",
    response_model=list[FatorEmissaoEnergiaResponse],
    summary="List energy emission factors",
    description="Returns energy emission factors, optionally filtered by year.",
)
async def list_energy_factors(
    current_user: CurrentUser,
    session: DatabaseSession,
    ano: Annotated[int | None, Query()] = None,
):
    return await service.list_energy_factors(ano, session)


@router.get(
    "/aerial-factors",
    response_model=list[FatorEmissaoAereaResponse],
    summary="List aerial emission factors",
    description="Returns all aerial transport emission factors.",
)
async def list_aerial_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_aerial_factors(session)


@router.get(
    "/bus-factors",
    response_model=list[FatorTransporteOnibusResponse],
    summary="List bus transport factors",
    description="Returns all bus transport emission factors.",
)
async def list_bus_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_bus_factors(session)


@router.get(
    "/effluent-treatment-factors",
    response_model=list[FatorTratamentoEfluenteResponse],
    summary="List effluent treatment factors",
    description="Returns all effluent treatment emission factors.",
)
async def list_effluent_treatment_factors(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_effluent_treatment_factors(session)


@router.get(
    "/gwp",
    response_model=list[GwpResponse],
    summary="List GWP values",
    description="Returns all Global Warming Potential values by GHG.",
)
async def list_gwp(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_gwp(session)


@router.get(
    "/airports",
    response_model=list[AeroportoCoordenadaResponse],
    summary="List airports",
    description="Returns all airports, optionally filtered by IATA code or name.",
)
async def list_airports(
    current_user: CurrentUser,
    session: DatabaseSession,
    search_query: Annotated[str | None, Query(alias="q", description="Filter by IATA code or name")] = None,
):
    return await service.list_airports(search_query, session)


@router.get(
    "/vehicle-equivalences",
    response_model=list[EquivalenciaVeiculoResponse],
    summary="List vehicle equivalences",
    description="Returns all vehicle equivalence factors.",
)
async def list_vehicle_equivalences(current_user: CurrentUser, session: DatabaseSession):
    return await service.list_vehicle_equivalences(session)


@router.post(
    "/energy-factors/import",
    response_model=EnergyFactorImportResponse,
    status_code=200,
    summary="Import energy emission factors",
    description="Replaces all energy emission factors from an ANEEL-format Excel spreadsheet.",
)
async def import_energy_factors(
    current_user: CurrentUser,
    session: DatabaseSession,
    file: UploadFile,
):
    content = await file.read()
    importados = await service.import_energy_factors(content, session)
    return EnergyFactorImportResponse(importados=importados)


@router.post(
    "/airports/import",
    response_model=AirportImportResponse,
    status_code=200,
    summary="Import airports",
    description="Replaces all airport coordinates from an Excel spreadsheet (Aeroportos sheet + optional Fatores_emissao_aereas sheet).",
)
async def import_airports(
    current_user: CurrentUser,
    session: DatabaseSession,
    file: UploadFile,
):
    content = await file.read()
    counts = await service.import_airports(content, session)
    return AirportImportResponse(**counts)


@router.post(
    "/vehicle-factors/import",
    response_model=VehicleFactorImportResponse,
    status_code=200,
    summary="Import vehicle emission factors",
    description="Replaces reference data tables from a multi-sheet Excel spreadsheet. Each sheet matching a known table name is cleared and re-imported.",
)
async def import_vehicle_factors(
    current_user: CurrentUser,
    session: DatabaseSession,
    file: UploadFile,
):
    content = await file.read()
    tabelas = await service.import_vehicle_factors(content, session)
    return VehicleFactorImportResponse(tabelas=tabelas)
