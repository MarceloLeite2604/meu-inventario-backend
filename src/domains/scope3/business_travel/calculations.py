import math
from dataclasses import dataclass


@dataclass
class AirEmissions:
    co2_tco2: float
    ch4_tco2e: float
    n2o_tco2e: float
    total_tco2e: float


@dataclass
class GroundEmissions:
    co2_tco2: float
    ch4_tco2e: float
    n2o_tco2e: float
    total_tco2e: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two coordinates in kilometres."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def classify_haul(distance_km: float) -> str:
    """Return short/medium/long-haul band per GHG Protocol conventions."""
    if distance_km < 1000:
        return "short"
    elif distance_km < 3700:
        return "medium"
    else:
        return "long"


def calculate_air(
    distance_km: float,
    round_trip: bool,
    passengers: int,
    co2_per_pkm: float,
    ch4_per_pkm: float,
    n2o_per_pkm: float,
    route_factor: float,
    gwp_ch4: float = 27.9,
    gwp_n2o: float = 273.0,
) -> AirEmissions:
    """
    Calculate air travel emissions.

    distance_km   — straight-line distance between airports (km)
    route_factor  — multiplier to account for actual routing vs great-circle (acrescimo_rota)
    *_per_pkm     — kg of gas per passenger-km
    """
    effective_distance = distance_km * route_factor * (2 if round_trip else 1)
    pkm = effective_distance * passengers

    co2_kg = pkm * co2_per_pkm
    ch4_kg = pkm * ch4_per_pkm
    n2o_kg = pkm * n2o_per_pkm

    co2_tco2 = co2_kg / 1000
    ch4_tco2e = ch4_kg * gwp_ch4 / 1000
    n2o_tco2e = n2o_kg * gwp_n2o / 1000

    return AirEmissions(
        co2_tco2=co2_tco2,
        ch4_tco2e=ch4_tco2e,
        n2o_tco2e=n2o_tco2e,
        total_tco2e=co2_tco2 + ch4_tco2e + n2o_tco2e,
    )


def calculate_ground(
    distance_km: float,
    round_trip: bool,
    passengers: int,
    co2_per_pkm: float,
    ch4_per_pkm: float,
    n2o_per_pkm: float,
    gwp_ch4: float = 27.9,
    gwp_n2o: float = 273.0,
) -> GroundEmissions:
    """
    Calculate ground transport emissions (bus, car, metro, train).

    *_per_pkm — kg of gas per passenger-km
    """
    effective_distance = distance_km * (2 if round_trip else 1)
    pkm = effective_distance * passengers

    co2_kg = pkm * co2_per_pkm
    ch4_kg = pkm * ch4_per_pkm
    n2o_kg = pkm * n2o_per_pkm

    co2_tco2 = co2_kg / 1000
    ch4_tco2e = ch4_kg * gwp_ch4 / 1000
    n2o_tco2e = n2o_kg * gwp_n2o / 1000

    return GroundEmissions(
        co2_tco2=co2_tco2,
        ch4_tco2e=ch4_tco2e,
        n2o_tco2e=n2o_tco2e,
        total_tco2e=co2_tco2 + ch4_tco2e + n2o_tco2e,
    )
