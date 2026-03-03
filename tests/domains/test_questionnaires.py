from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.questionnaires import service
from src.domains.questionnaires.models import QuestionarioSalvo
from src.domains.questionnaires.schemas import (
    DeslocamentoCreate,
    QuestionarioSalvoCreate,
    RespostaCreate,
)
from src.domains.organizations.models import Organizacao


class TestListQuestionnaires:
    async def test_returns_empty_list_when_no_questionnaires(self, database_session: AsyncSession):
        result = await service.list_questionnaires(None, database_session)
        assert result == []

    async def test_returns_all_questionnaires_when_no_filter(self, database_session: AsyncSession):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        database_session.add(QuestionarioSalvo(
            nome="Q1", organizacao_id=organization.id, token="token-1"
        ))
        database_session.add(QuestionarioSalvo(
            nome="Q2", organizacao_id=organization.id, token="token-2"
        ))
        await database_session.flush()

        result = await service.list_questionnaires(None, database_session)

        names = [questionnaire.nome for questionnaire in result]
        assert "Q1" in names
        assert "Q2" in names

    async def test_filters_by_organization_id(self, database_session: AsyncSession):
        organization_a = Organizacao(nome="Org A")
        organization_b = Organizacao(nome="Org B")
        database_session.add(organization_a)
        database_session.add(organization_b)
        await database_session.flush()

        database_session.add(QuestionarioSalvo(
            nome="Org A Q", organizacao_id=organization_a.id, token="token-a"
        ))
        database_session.add(QuestionarioSalvo(
            nome="Org B Q", organizacao_id=organization_b.id, token="token-b"
        ))
        await database_session.flush()

        result = await service.list_questionnaires(organization_a.id, database_session)

        assert all(q.organizacao_id == organization_a.id for q in result)
        names = [questionnaire.nome for questionnaire in result]
        assert "Org A Q" in names
        assert "Org B Q" not in names


class TestGetQuestionnaire:
    async def test_returns_questionnaire_when_found(self, database_session: AsyncSession):
        questionnaire = QuestionarioSalvo(nome="My Q", token="my-token")
        database_session.add(questionnaire)
        await database_session.flush()

        result = await service.get_questionnaire(questionnaire.id, database_session)

        assert result.id == questionnaire.id
        assert result.nome == "My Q"

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.get_questionnaire(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestGetQuestionnaireByToken:
    async def test_returns_questionnaire_when_token_is_valid(self, database_session: AsyncSession):
        questionnaire = QuestionarioSalvo(nome="Public Q", token="valid-public-token", ativo=True)
        database_session.add(questionnaire)
        await database_session.flush()

        result = await service.get_questionnaire_by_token("valid-public-token", database_session)

        assert result.token == "valid-public-token"
        assert result.nome == "Public Q"

    async def test_raises_404_when_token_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.get_questionnaire_by_token("nonexistent-token", database_session)

        assert exception_info.value.status_code == 404

    async def test_raises_404_when_questionnaire_is_inactive(self, database_session: AsyncSession):
        questionnaire = QuestionarioSalvo(
            nome="Inactive Q", token="inactive-token", ativo=False
        )
        database_session.add(questionnaire)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await service.get_questionnaire_by_token("inactive-token", database_session)

        assert exception_info.value.status_code == 404


class TestCreateQuestionnaire:
    async def test_creates_questionnaire_with_unique_token(self, database_session: AsyncSession):
        data = QuestionarioSalvoCreate(nome="New Questionnaire")

        result = await service.create_questionnaire(data, "creator-user", database_session)

        assert result.id is not None
        assert result.nome == "New Questionnaire"
        assert result.token is not None
        assert len(result.token) > 0
        assert result.created_by == "creator-user"
        assert result.ativo is True

    async def test_each_questionnaire_has_different_token(self, database_session: AsyncSession):
        data_one = QuestionarioSalvoCreate(nome="Q One")
        data_two = QuestionarioSalvoCreate(nome="Q Two")

        result_one = await service.create_questionnaire(data_one, "user", database_session)
        result_two = await service.create_questionnaire(data_two, "user", database_session)

        assert result_one.token != result_two.token

    async def test_creates_questionnaire_with_optional_organization(
        self, database_session: AsyncSession
    ):
        organization = Organizacao(nome="Org")
        database_session.add(organization)
        await database_session.flush()

        data = QuestionarioSalvoCreate(
            nome="Org Questionnaire",
            organizacao_id=organization.id,
            descricao="Test questionnaire",
        )
        result = await service.create_questionnaire(data, "user", database_session)

        assert result.organizacao_id == organization.id
        assert result.descricao == "Test questionnaire"


class TestDeleteQuestionnaire:
    async def test_deletes_existing_questionnaire(self, database_session: AsyncSession):
        questionnaire = QuestionarioSalvo(nome="Delete Me Q", token="delete-token")
        database_session.add(questionnaire)
        await database_session.flush()
        questionnaire_id = questionnaire.id

        await service.delete_questionnaire(questionnaire_id, database_session)
        await database_session.flush()

        with pytest.raises(HTTPException) as exception_info:
            await service.get_questionnaire(questionnaire_id, database_session)
        assert exception_info.value.status_code == 404

    async def test_raises_404_when_not_found(self, database_session: AsyncSession):
        with pytest.raises(HTTPException) as exception_info:
            await service.delete_questionnaire(uuid4(), database_session)

        assert exception_info.value.status_code == 404


class TestSubmitResponse:
    def _make_mock_request(self, client_host: str = "127.0.0.1") -> MagicMock:
        mock_request = MagicMock()
        mock_request.client = MagicMock()
        mock_request.client.host = client_host
        return mock_request

    async def test_submits_response_and_creates_respondent(self, database_session: AsyncSession):
        questionnaire = QuestionarioSalvo(
            nome="Response Q", token="response-token", ativo=True
        )
        database_session.add(questionnaire)
        await database_session.flush()

        data = RespostaCreate(
            nome="Jane Doe",
            email="jane@example.com",
            deslocamentos=[
                DeslocamentoCreate(transport="carro", distance=15.0),
            ],
        )
        respondent, displacements = await service.submit_response(
            "response-token", data, self._make_mock_request(), database_session
        )

        assert respondent.nome == "Jane Doe"
        assert respondent.email == "jane@example.com"
        assert len(displacements) == 1
        assert displacements[0].transport == "carro"

    async def test_updates_questionnaire_totals(self, database_session: AsyncSession):
        questionnaire = QuestionarioSalvo(
            nome="Totals Q",
            token="totals-token",
            ativo=True,
            total_deslocamentos=0,
            total_emissoes=0.0,
        )
        database_session.add(questionnaire)
        await database_session.flush()

        data = RespostaCreate(
            nome="Respondent",
            email="respondent@example.com",
            deslocamentos=[
                DeslocamentoCreate(transport="metro", distance=10.0),
                DeslocamentoCreate(transport="onibus", distance=5.0),
            ],
        )
        await service.submit_response(
            "totals-token", data, self._make_mock_request("192.168.1.1"), database_session
        )

        await database_session.flush()
        await database_session.refresh(questionnaire)
        assert questionnaire.total_deslocamentos == 2

    async def test_raises_404_for_invalid_token(self, database_session: AsyncSession):
        data = RespostaCreate(
            nome="Ghost",
            email="ghost@example.com",
            deslocamentos=[],
        )
        with pytest.raises(HTTPException) as exception_info:
            await service.submit_response(
                "invalid-token", data, self._make_mock_request(), database_session
            )

        assert exception_info.value.status_code == 404

    async def test_raises_404_for_inactive_questionnaire(self, database_session: AsyncSession):
        questionnaire = QuestionarioSalvo(
            nome="Inactive Q", token="inactive-submit-token", ativo=False
        )
        database_session.add(questionnaire)
        await database_session.flush()

        data = RespostaCreate(
            nome="User",
            email="user@example.com",
            deslocamentos=[],
        )
        with pytest.raises(HTTPException) as exception_info:
            await service.submit_response(
                "inactive-submit-token", data, self._make_mock_request(), database_session
            )

        assert exception_info.value.status_code == 404


class TestQuestionnaireRoutes:
    async def test_list_questionnaires_returns_200(self, client):
        response = await client.get("/questionnaires")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_questionnaire_returns_201(self, client):
        payload = {"nome": "Route Questionnaire"}
        response = await client.post("/questionnaires", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["nome"] == "Route Questionnaire"
        assert "token" in body
        assert body["ativo"] is True

    async def test_get_questionnaire_returns_200(self, client):
        create_response = await client.post(
            "/questionnaires", json={"nome": "Fetch Questionnaire"}
        )
        questionnaire_id = create_response.json()["id"]

        response = await client.get(f"/questionnaires/{questionnaire_id}")
        assert response.status_code == 200
        assert response.json()["nome"] == "Fetch Questionnaire"

    async def test_get_questionnaire_returns_404_for_unknown_id(self, client):
        response = await client.get(f"/questionnaires/{uuid4()}")
        assert response.status_code == 404

    async def test_delete_questionnaire_returns_204(self, client):
        create_response = await client.post(
            "/questionnaires", json={"nome": "Delete Questionnaire"}
        )
        questionnaire_id = create_response.json()["id"]

        response = await client.delete(f"/questionnaires/{questionnaire_id}")
        assert response.status_code == 204

    async def test_get_public_questionnaire_returns_200(self, client):
        create_response = await client.post(
            "/questionnaires", json={"nome": "Public Q"}
        )
        token = create_response.json()["token"]

        response = await client.get(f"/public/questionnaires/{token}")
        assert response.status_code == 200
        body = response.json()
        assert body["nome"] == "Public Q"
        assert "token" not in body

    async def test_get_public_questionnaire_returns_404_for_invalid_token(self, client):
        response = await client.get("/public/questionnaires/invalid-token-xyz")
        assert response.status_code == 404

    async def test_submit_response_returns_201(self, client):
        create_response = await client.post(
            "/questionnaires", json={"nome": "Submit Target Q"}
        )
        token = create_response.json()["token"]

        payload = {
            "nome": "Route Respondent",
            "email": "route@respondent.com",
            "deslocamentos": [
                {"transport": "metro", "distance": 12.0}
            ],
        }
        response = await client.post(
            f"/public/questionnaires/{token}/responses", json=payload
        )
        assert response.status_code == 201
        body = response.json()
        assert "respondente_id" in body
        assert len(body["deslocamentos"]) == 1
