from datetime import date
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.commuting import service
from src.domains.commuting.models import (
    CommutingColaborador,
    CommutingEmpresa,
    CommutingMedalha,
)
from src.domains.commuting.schemas import (
    CommutingColaboradorCreate,
    CommutingEmpresaCreate,
    CommutingRegistroCreate,
    CommutingTransporteHabitualCreate,
)


class TestAwardPoints:
    def test_bicycle_earns_fifty_points_per_day(self):
        assert service._award_points("bicicleta", 1) == 50

    def test_walking_earns_fifty_points_per_day(self):
        assert service._award_points("a_pe", 1) == 50

    def test_bus_earns_thirty_points_per_day(self):
        assert service._award_points("onibus", 1) == 30

    def test_metro_earns_thirty_points_per_day(self):
        assert service._award_points("metro", 1) == 30

    def test_train_earns_thirty_points_per_day(self):
        assert service._award_points("trem", 1) == 30

    def test_electric_car_earns_twenty_points_per_day(self):
        assert service._award_points("carro_eletrico", 1) == 20

    def test_hybrid_car_earns_ten_points_per_day(self):
        assert service._award_points("carro_hibrido", 1) == 10

    def test_car_earns_zero_points(self):
        assert service._award_points("carro", 5) == 0

    def test_motorcycle_earns_zero_points(self):
        assert service._award_points("moto", 5) == 0

    def test_unknown_transport_earns_zero_points(self):
        assert service._award_points("helicopter", 3) == 0

    def test_multiplies_by_days_used(self):
        assert service._award_points("bicicleta", 5) == 250

    def test_transport_type_is_case_insensitive(self):
        assert service._award_points("BICICLETA", 1) == 50


class TestListCompanies:
    async def test_returns_empty_list_when_no_companies(self, database_session: AsyncSession):
        result = await service.list_companies(database_session)
        assert result == []

    async def test_returns_companies_ordered_by_name(self, database_session: AsyncSession):
        database_session.add(CommutingEmpresa(nome="Zeta Corp", dominio_email="zeta.com"))
        database_session.add(CommutingEmpresa(nome="Alpha Ltd", dominio_email="alpha.com"))
        await database_session.flush()

        result = await service.list_companies(database_session)

        names = [company.nome for company in result]
        assert names.index("Alpha Ltd") < names.index("Zeta Corp")


class TestGetCompany:
    async def test_returns_company_when_found(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Test Company", dominio_email="test.com")
        database_session.add(company)
        await database_session.flush()

        result = await service.get_company(company.id, database_session)

        assert result.id == company.id
        assert result.nome == "Test Company"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.get_company(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestCreateCompany:
    async def test_creates_company_with_required_fields(self, database_session: AsyncSession):
        data = CommutingEmpresaCreate(nome="New Company", dominio_email="newcompany.com")

        result = await service.create_company(data, "creator-id", database_session)

        assert result.id is not None
        assert result.nome == "New Company"
        assert result.dominio_email == "newcompany.com"
        assert result.created_by == "creator-id"
        assert result.ativa is True

    async def test_creates_company_with_optional_fields(self, database_session: AsyncSession):
        data = CommutingEmpresaCreate(
            nome="Full Company",
            dominio_email="full.com",
            cidade="Curitiba",
            estado="PR",
        )

        result = await service.create_company(data, "creator", database_session)

        assert result.cidade == "Curitiba"
        assert result.estado == "PR"


class TestListEmployees:
    async def test_returns_empty_list_when_no_employees(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Empty Company", dominio_email="empty.com")
        database_session.add(company)
        await database_session.flush()

        result = await service.list_employees(company.id, database_session)

        assert result == []

    async def test_returns_employees_ordered_by_points_descending(
        self, database_session: AsyncSession
    ):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        database_session.add(CommutingColaborador(
            user_id="user-low", empresa_id=company.id, nome="Low Scorer", pontos_total=100
        ))
        database_session.add(CommutingColaborador(
            user_id="user-high", empresa_id=company.id, nome="High Scorer", pontos_total=500
        ))
        await database_session.flush()

        result = await service.list_employees(company.id, database_session)

        assert result[0].pontos_total >= result[-1].pontos_total


class TestGetEmployee:
    async def test_returns_employee_when_found(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        employee = CommutingColaborador(
            user_id="user-xyz", empresa_id=company.id, nome="Jane Doe"
        )
        database_session.add(employee)
        await database_session.flush()

        result = await service.get_employee(employee.id, database_session)

        assert result.id == employee.id
        assert result.nome == "Jane Doe"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.get_employee(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestCreateEmployee:
    async def test_creates_employee_with_default_points_and_level(
        self, database_session: AsyncSession
    ):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        data = CommutingColaboradorCreate(
            user_id="new-employee", empresa_id=company.id, nome="John Doe"
        )
        result = await service.create_employee(data, database_session)

        assert result.pontos_total == 0
        assert result.nivel == 1
        assert result.ativo is True


class TestSetHabitualTransport:
    async def test_sets_habitual_transport_for_employee(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        employee = CommutingColaborador(
            user_id="transport-user", empresa_id=company.id, nome="Transport User"
        )
        database_session.add(employee)
        await database_session.flush()

        data = CommutingTransporteHabitualCreate(
            tipo_transporte="bicicleta",
            distancia_km=15.0,
        )
        result = await service.set_habitual_transport(employee.id, data, database_session)

        assert result.colaborador_id == employee.id
        assert result.tipo_transporte == "bicicleta"
        assert result.distancia_km == 15.0


class TestCreateRecord:
    async def test_awards_points_and_updates_employee_level(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        employee = CommutingColaborador(
            user_id="record-user", empresa_id=company.id, nome="Record User"
        )
        database_session.add(employee)
        await database_session.flush()

        data = CommutingRegistroCreate(
            colaborador_id=employee.id,
            semana_inicio=date(2024, 1, 15),
            tipo_transporte="bicicleta",
            distancia_km=10.0,
            dias_utilizados=5,
        )
        record = await service.create_record(employee.id, data, database_session)

        assert record.pontos_ganhos == 250
        await database_session.refresh(employee)
        assert employee.pontos_total == 250

    async def test_level_is_one_for_less_than_500_points(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        employee = CommutingColaborador(
            user_id="level-user-1", empresa_id=company.id, nome="Level User", pontos_total=0
        )
        database_session.add(employee)
        await database_session.flush()

        data = CommutingRegistroCreate(
            colaborador_id=employee.id,
            semana_inicio=date(2024, 2, 5),
            tipo_transporte="bicicleta",
            distancia_km=5.0,
            dias_utilizados=1,
        )
        await service.create_record(employee.id, data, database_session)

        await database_session.refresh(employee)
        assert employee.nivel == 1

    async def test_level_increases_at_500_points(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        employee = CommutingColaborador(
            user_id="level-user-2", empresa_id=company.id, nome="Level User", pontos_total=450
        )
        database_session.add(employee)
        await database_session.flush()

        data = CommutingRegistroCreate(
            colaborador_id=employee.id,
            semana_inicio=date(2024, 3, 4),
            tipo_transporte="bicicleta",
            distancia_km=10.0,
            dias_utilizados=5,
        )
        await service.create_record(employee.id, data, database_session)

        await database_session.refresh(employee)
        assert employee.pontos_total == 700
        assert employee.nivel == 2

    async def test_car_commute_awards_zero_points(self, database_session: AsyncSession):
        company = CommutingEmpresa(nome="Company", dominio_email="company.com")
        database_session.add(company)
        await database_session.flush()

        employee = CommutingColaborador(
            user_id="car-user", empresa_id=company.id, nome="Car User"
        )
        database_session.add(employee)
        await database_session.flush()

        data = CommutingRegistroCreate(
            colaborador_id=employee.id,
            semana_inicio=date(2024, 4, 1),
            tipo_transporte="carro",
            distancia_km=20.0,
            dias_utilizados=5,
        )
        record = await service.create_record(employee.id, data, database_session)

        assert record.pontos_ganhos == 0


class TestAwardMedal:
    async def _create_company_and_employee(self, session: AsyncSession):
        company = CommutingEmpresa(nome="Medal Company", dominio_email="medals.com")
        session.add(company)
        await session.flush()

        employee = CommutingColaborador(
            user_id="medal-user", empresa_id=company.id, nome="Medal User"
        )
        session.add(employee)
        await session.flush()
        return employee

    async def test_awards_medal_and_adds_bonus_points(self, database_session: AsyncSession):
        employee = await self._create_company_and_employee(database_session)

        medal = CommutingMedalha(
            nome="Green Champion",
            descricao="Awarded for green transport",
            criterio="50_green_trips",
            pontos_bonus=100,
        )
        database_session.add(medal)
        await database_session.flush()

        result = await service.award_medal(employee.id, medal.id, database_session)

        assert result.colaborador_id == employee.id
        assert result.medalha_id == medal.id
        await database_session.refresh(employee)
        assert employee.pontos_total == 100

    async def test_raises_409_when_medal_already_awarded(self, database_session: AsyncSession):
        employee = await self._create_company_and_employee(database_session)

        medal = CommutingMedalha(
            nome="Unique Medal",
            descricao="One-time award",
            criterio="first_trip",
            pontos_bonus=50,
        )
        database_session.add(medal)
        await database_session.flush()

        await service.award_medal(employee.id, medal.id, database_session)

        with pytest.raises(HTTPException) as exception_info:
            await service.award_medal(employee.id, medal.id, database_session)

        assert exception_info.value.status_code == 409

    async def test_raises_404_when_medal_not_found(self, database_session: AsyncSession):
        employee = await self._create_company_and_employee(database_session)

        with pytest.raises(HTTPException) as exception_info:
            await service.award_medal(employee.id, uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestCommutingRoutes:
    async def _create_company(self, client) -> str:
        response = await client.post(
            "/commuting/companies",
            json={"nome": "Route Company", "dominio_email": "route.com"},
        )
        return response.json()["id"]

    async def _create_employee(self, client, company_id: str) -> str:
        response = await client.post(
            f"/commuting/companies/{company_id}/employees",
            json={"user_id": f"emp-{uuid4()}", "empresa_id": company_id, "nome": "Route Employee"},
        )
        return response.json()["id"]

    async def test_list_companies_returns_200(self, client):
        response = await client.get("/commuting/companies")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_company_returns_201(self, client):
        payload = {"nome": "New Route Company", "dominio_email": "newroute.com"}
        response = await client.post("/commuting/companies", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["nome"] == "New Route Company"

    async def test_list_employees_returns_200(self, client):
        company_id = await self._create_company(client)
        response = await client.get(f"/commuting/companies/{company_id}/employees")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_employee_returns_201(self, client):
        company_id = await self._create_company(client)
        payload = {
            "user_id": f"route-emp-{uuid4()}",
            "empresa_id": company_id,
            "nome": "New Employee",
        }
        response = await client.post(
            f"/commuting/companies/{company_id}/employees", json=payload
        )
        assert response.status_code == 201
        assert response.json()["nome"] == "New Employee"

    async def test_get_employee_returns_200(self, client):
        company_id = await self._create_company(client)
        employee_id = await self._create_employee(client, company_id)

        response = await client.get(
            f"/commuting/companies/{company_id}/employees/{employee_id}"
        )
        assert response.status_code == 200

    async def test_set_habitual_transport_returns_201(self, client):
        company_id = await self._create_company(client)
        employee_id = await self._create_employee(client, company_id)

        payload = {"tipo_transporte": "metro", "distancia_km": 12.5}
        response = await client.post(
            f"/commuting/companies/{company_id}/employees/{employee_id}/habitual-transports",
            json=payload,
        )
        assert response.status_code == 201
        assert response.json()["tipo_transporte"] == "metro"

    async def test_list_habitual_transports_returns_200(self, client):
        company_id = await self._create_company(client)
        employee_id = await self._create_employee(client, company_id)

        response = await client.get(
            f"/commuting/companies/{company_id}/employees/{employee_id}/habitual-transports"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_commuting_record_returns_201(self, client):
        company_id = await self._create_company(client)
        employee_id = await self._create_employee(client, company_id)

        payload = {
            "colaborador_id": employee_id,
            "semana_inicio": "2024-01-15",
            "tipo_transporte": "bicicleta",
            "distancia_km": 8.0,
            "dias_utilizados": 5,
        }
        response = await client.post(
            f"/commuting/companies/{company_id}/employees/{employee_id}/records",
            json=payload,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["pontos_ganhos"] == 250

    async def test_list_commuting_records_returns_200(self, client):
        company_id = await self._create_company(client)
        employee_id = await self._create_employee(client, company_id)

        response = await client.get(
            f"/commuting/companies/{company_id}/employees/{employee_id}/records"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_medals_returns_200(self, client):
        response = await client.get("/commuting/medals")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_employee_medals_returns_200(self, client):
        company_id = await self._create_company(client)
        employee_id = await self._create_employee(client, company_id)

        response = await client.get(
            f"/commuting/companies/{company_id}/employees/{employee_id}/medals"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
