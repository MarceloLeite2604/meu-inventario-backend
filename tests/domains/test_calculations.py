"""Unit tests for emission calculation functions (no I/O required)."""

import pytest

from src.domains.scope1.fugitive.calculations import calculate as fugitive_calculate
from src.domains.scope1.effluents.calculations import calculate as effluent_calculate
from src.domains.scope2.energy.calculations import calculate as energy_calculate
from src.domains.scope3.business_travel.calculations import (
    calculate_air,
    calculate_ground,
    classify_haul,
    haversine_km,
)


# ── Fugitive ────────────────────────────────────────────────────────────────

class TestFugitiveCalculations:
    def test_basic(self):
        # 1 kg of R-134a (GWP=1300) → 1.3 tCO2e
        result = fugitive_calculate(1.0, 1300.0)
        assert result == pytest.approx(1.3, rel=1e-6)

    def test_zero_quantity(self):
        assert fugitive_calculate(0.0, 1300.0) == 0.0

    def test_zero_gwp(self):
        assert fugitive_calculate(100.0, 0.0) == 0.0


# ── Energy ───────────────────────────────────────────────────────────────────

class TestEnergyCalculations:
    def test_basic(self):
        # 10 MWh × 0.09 tCO2e/MWh = 0.9 tCO2e
        result = energy_calculate(10.0, 0.09)
        assert result == pytest.approx(0.9, rel=1e-6)

    def test_zero_consumption(self):
        assert energy_calculate(0.0, 0.09) == 0.0


# ── Effluents ────────────────────────────────────────────────────────────────

class TestEffluentCalculations:
    def test_basic_domestic(self):
        """Domestic effluent: IPCC 2019 Tier 1."""
        result = effluent_calculate(
            volume_efluente=1000.0,
            carga_organica_entrada=0.5,
            carga_organica_lodo=0.05,
            mcf_tratamento=0.1,
            mcf_tratamento_2=0.0,
            mcf_disposicao=0.0,
            ch4_recuperado=0.0,
            nitrogenio_efluente=0.05,
            fator_n2o=0.005,
            tratamento_sequencial=False,
            efluente_lancado_ambiente=False,
        )
        assert result.emissoes_ch4 >= 0
        assert result.emissoes_n2o >= 0
        assert result.emissoes_tco2e >= 0


# ── Business Travel — Haversine ──────────────────────────────────────────────

class TestHaversine:
    def test_same_point(self):
        assert haversine_km(0.0, 0.0, 0.0, 0.0) == pytest.approx(0.0, abs=1e-6)

    def test_known_distance(self):
        # GRU (Sao Paulo) to GIG (Rio de Janeiro) ≈ 360 km
        gruso = (-23.4356, -46.4731)
        gig = (-22.8100, -43.2506)
        dist = haversine_km(*gruso, *gig)
        assert 330 < dist < 390


class TestClassifyHaul:
    def test_short(self):
        assert classify_haul(500) == "short"

    def test_medium(self):
        assert classify_haul(2000) == "medium"

    def test_long(self):
        assert classify_haul(5000) == "long"


class TestAirCalculations:
    def test_basic(self):
        result = calculate_air(
            distance_km=1000.0,
            round_trip=False,
            passengers=1,
            co2_per_pkm=0.133,
            ch4_per_pkm=0.000004,
            n2o_per_pkm=0.000041,
            route_factor=1.08,
        )
        assert result.total_tco2e > 0
        assert result.co2_tco2 > 0

    def test_round_trip_doubles(self):
        single = calculate_air(1000.0, False, 1, 0.133, 0.000004, 0.000041, 1.0)
        double = calculate_air(1000.0, True, 1, 0.133, 0.000004, 0.000041, 1.0)
        assert double.total_tco2e == pytest.approx(2 * single.total_tco2e, rel=1e-6)


class TestGroundCalculations:
    def test_zero_factors(self):
        result = calculate_ground(500.0, False, 10, 0.0, 0.0, 0.0)
        assert result.total_tco2e == 0.0

    def test_basic(self):
        result = calculate_ground(
            distance_km=100.0,
            round_trip=False,
            passengers=2,
            co2_per_pkm=0.089,
            ch4_per_pkm=0.000003,
            n2o_per_pkm=0.000004,
        )
        assert result.total_tco2e > 0
