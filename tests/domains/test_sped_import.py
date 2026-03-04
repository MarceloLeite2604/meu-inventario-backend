"""Tests for SPED file import feature in stationary combustion."""

import io
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.scope1.stationary_combustion import service
from src.domains.scope1.stationary_combustion.schemas import SpedImportItem, SpedImportRequest
from src.domains.scope1.stationary_combustion.sped_parser import parse_sped


def _make_sped_content(*lines: str) -> bytes:
    full = "\n".join(lines) + "\n"
    return full.encode("latin-1")


class TestSpedParser:
    def test_returns_empty_list_for_empty_file(self):
        result = parse_sped(b"")

        assert result == []

    def test_returns_empty_list_when_no_bloco_c_records(self):
        content = _make_sped_content(
            "|0000|001|LECD|01012023|31012023|EMPRESA|12345678000100||1|",
            "|9999|1|",
        )

        result = parse_sped(content)

        assert result == []

    def test_parses_c170_record(self):
        content = _make_sped_content(
            "|C170|1|PROD001|Óleo Diesel S10|100,500|LT|1500.00|...|",
        )

        result = parse_sped(content)

        assert len(result) == 1
        assert result[0].codigo == "PROD001"
        assert result[0].descricao == "Óleo Diesel S10"
        assert result[0].quantidade == pytest.approx(100.5)
        assert result[0].unidade == "LT"

    def test_parses_c425_record(self):
        content = _make_sped_content(
            "|C425|GASOLINA001|250,000|LT|3750.00|",
        )

        result = parse_sped(content)

        assert len(result) == 1
        assert result[0].codigo == "GASOLINA001"
        assert result[0].descricao == "GASOLINA001"  # C425 uses codigo as descricao
        assert result[0].quantidade == pytest.approx(250.0)
        assert result[0].unidade == "LT"

    def test_aggregates_quantities_for_same_item(self):
        content = _make_sped_content(
            "|C170|1|PROD001|Óleo Diesel|50,000|LT|750.00|",
            "|C170|2|PROD001|Óleo Diesel|30,000|LT|450.00|",
        )

        result = parse_sped(content)

        assert len(result) == 1
        assert result[0].quantidade == pytest.approx(80.0)

    def test_auto_maps_diesel_fuel(self):
        content = _make_sped_content(
            "|C170|1|D001|Óleo Diesel Comum|200,000|LT|3000.00|",
        )

        result = parse_sped(content)

        assert result[0].combustivel_fossil_sugerido == "Óleo Diesel"

    def test_auto_maps_gasolina_fuel(self):
        content = _make_sped_content(
            "|C170|1|G001|Gasolina Automotiva C|150,000|LT|2250.00|",
        )

        result = parse_sped(content)

        assert result[0].combustivel_fossil_sugerido == "Gasolina Automotiva"

    def test_auto_maps_glp_fuel(self):
        content = _make_sped_content(
            "|C170|1|B001|GLP Botijão 13kg|10,000|UN|1300.00|",
        )

        result = parse_sped(content)

        assert result[0].combustivel_fossil_sugerido == "GLP"

    def test_auto_maps_etanol_fuel(self):
        content = _make_sped_content(
            "|C170|1|E001|Etanol Hidratado|100,000|LT|700.00|",
        )

        result = parse_sped(content)

        assert result[0].combustivel_fossil_sugerido == "Etanol"

    def test_returns_none_for_unrecognized_fuel(self):
        content = _make_sped_content(
            "|C170|1|P001|Produto Genérico XYZ|50,000|KG|500.00|",
        )

        result = parse_sped(content)

        assert result[0].combustivel_fossil_sugerido is None

    def test_skips_records_with_zero_quantity(self):
        content = _make_sped_content(
            "|C170|1|PROD001|Óleo Diesel|0,000|LT|0.00|",
        )

        result = parse_sped(content)

        assert result == []

    def test_skips_records_with_missing_codigo(self):
        content = _make_sped_content(
            "|C170|1||Produto sem código|50,000|LT|750.00|",
        )

        result = parse_sped(content)

        assert result == []

    def test_handles_crlf_line_endings(self):
        content = b"|C170|1|PROD001|Gasolina|100,000|LT|1500.00|\r\n"

        result = parse_sped(content)

        assert len(result) == 1
        assert result[0].codigo == "PROD001"

    def test_parses_multiple_record_types(self):
        content = _make_sped_content(
            "|C170|1|D001|Óleo Diesel|100,000|LT|1500.00|",
            "|C425|GASOLINA001|250,000|LT|3750.00|",
        )

        result = parse_sped(content)

        assert len(result) == 2


class TestSpedServiceParseSped:
    def test_returns_sped_items_from_valid_content(self):
        content = _make_sped_content(
            "|C170|1|PROD001|Óleo Diesel|100,000|LT|1500.00|",
        )

        result = service.parse_sped_file(content)

        assert len(result) == 1
        assert result[0].codigo == "PROD001"
        assert result[0].combustivel_fossil_sugerido == "Óleo Diesel"

    def test_returns_empty_list_for_empty_file(self):
        result = service.parse_sped_file(b"")

        assert result == []


class TestSpedServiceImportSped:
    async def test_creates_records_for_each_item(self, database_session: AsyncSession):
        request = SpedImportRequest(
            ano=2024,
            mes=1,
            descricao="Importação SPED Janeiro",
            items=[
                SpedImportItem(
                    codigo="D001",
                    descricao="Óleo Diesel",
                    quantidade=100.0,
                    unidade="LT",
                    combustivel_fossil="Óleo Diesel",
                ),
                SpedImportItem(
                    codigo="G001",
                    descricao="Gasolina",
                    quantidade=50.0,
                    unidade="LT",
                    combustivel_fossil="Gasolina Automotiva",
                ),
            ],
        )

        criados, records = await service.import_sped_items(request, database_session)

        assert criados == 2
        assert len(records) == 2

    async def test_returns_zero_for_empty_items(self, database_session: AsyncSession):
        request = SpedImportRequest(ano=2024, mes=1, items=[])

        criados, records = await service.import_sped_items(request, database_session)

        assert criados == 0
        assert records == []

    async def test_sets_correct_ano_mes_on_records(self, database_session: AsyncSession):
        request = SpedImportRequest(
            ano=2023,
            mes=6,
            items=[
                SpedImportItem(
                    codigo="D001",
                    descricao="Óleo Diesel",
                    quantidade=100.0,
                    unidade="LT",
                    combustivel_fossil="Óleo Diesel",
                )
            ],
        )

        _, records = await service.import_sped_items(request, database_session)

        assert records[0].ano == 2023
        assert records[0].mes == 6


class TestSpedRoutes:
    async def test_sped_preview_returns_200_with_parsed_items(self, client: AsyncClient):
        content = _make_sped_content(
            "|C170|1|PROD001|Óleo Diesel S10|100,500|LT|1500.00|",
        )
        inventory_id = uuid4()

        response = await client.post(
            f"/inventories/{inventory_id}/scope1/stationary-combustion/sped-preview",
            files={"file": ("sped.txt", io.BytesIO(content), "text/plain")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["codigo"] == "PROD001"
        assert data["items"][0]["combustivel_fossil_sugerido"] == "Óleo Diesel"

    async def test_sped_preview_returns_empty_items_for_no_bloco_c(self, client: AsyncClient):
        content = _make_sped_content("|0000|001|LECD|01012023|31012023|")
        inventory_id = uuid4()

        response = await client.post(
            f"/inventories/{inventory_id}/scope1/stationary-combustion/sped-preview",
            files={"file": ("sped.txt", io.BytesIO(content), "text/plain")},
        )

        assert response.status_code == 200
        assert response.json()["items"] == []

    async def test_sped_import_returns_201_and_correct_count(self, client: AsyncClient):
        inventory_id = uuid4()
        payload = {
            "ano": 2024,
            "mes": 3,
            "descricao": "Importação SPED Março",
            "items": [
                {
                    "codigo": "D001",
                    "descricao": "Óleo Diesel",
                    "quantidade": 100.0,
                    "unidade": "LT",
                    "combustivel_fossil": "Óleo Diesel",
                }
            ],
        }

        response = await client.post(
            f"/inventories/{inventory_id}/scope1/stationary-combustion/sped-import",
            json=payload,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["criados"] == 1
        assert len(data["registros"]) == 1
        assert data["registros"][0]["ano"] == 2024
        assert data["registros"][0]["mes"] == 3

    async def test_sped_import_returns_201_with_zero_records_for_empty_items(
        self, client: AsyncClient
    ):
        inventory_id = uuid4()
        payload = {"ano": 2024, "mes": 1, "items": []}

        response = await client.post(
            f"/inventories/{inventory_id}/scope1/stationary-combustion/sped-import",
            json=payload,
        )

        assert response.status_code == 201
        assert response.json()["criados"] == 0
