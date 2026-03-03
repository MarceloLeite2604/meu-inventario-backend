from dataclasses import dataclass


@dataclass
class StationaryResult:
    emissoes_co2: float
    emissoes_ch4: float
    emissoes_n2o: float
    emissoes_co2_biogenico: float
    emissoes_ch4_biogenico: float
    emissoes_n2o_biogenico: float
    emissoes_total_tco2e: float


def calculate(
    quantidade_fossil: float,
    quantidade_biocombustivel: float,
    fator_co2: float,
    fator_ch4: float,
    fator_n2o: float,
    fator_co2_bio: float = 0.0,
    fator_ch4_bio: float = 0.0,
    fator_n2o_bio: float = 0.0,
    gwp_ch4: float = 27.9,
    gwp_n2o: float = 273.0,
) -> StationaryResult:
    co2 = quantidade_fossil * fator_co2
    ch4 = quantidade_fossil * fator_ch4
    n2o = quantidade_fossil * fator_n2o

    co2_bio = quantidade_biocombustivel * fator_co2_bio
    ch4_bio = quantidade_biocombustivel * fator_ch4_bio
    n2o_bio = quantidade_biocombustivel * fator_n2o_bio

    total_tco2e = co2 + (ch4 * gwp_ch4 / 1000) + (n2o * gwp_n2o / 1000)

    return StationaryResult(
        emissoes_co2=co2,
        emissoes_ch4=ch4,
        emissoes_n2o=n2o,
        emissoes_co2_biogenico=co2_bio,
        emissoes_ch4_biogenico=ch4_bio,
        emissoes_n2o_biogenico=n2o_bio,
        emissoes_total_tco2e=total_tco2e,
    )
