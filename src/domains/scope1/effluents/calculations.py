"""
IPCC 2019 Tier 1 methodology for effluent treatment emissions.

CH4 emissions:
  TOW = Volume × (organic_load_in - organic_load_sludge)
  CH4_generated = TOW × B0 × MCF
  CH4_emitted = CH4_generated - CH4_recovered
  tCH4 = CH4_emitted / 1000

N2O emissions:
  N_effluent = Volume × nitrogen_concentration
  N2O_N = N_effluent × EF_N2O
  N2O = N2O_N × (44/28)
  tN2O = N2O / 1000

B0 (maximum CH4 producing capacity) = 0.6 kgCH4/kgBOD (IPCC default)
"""
from dataclasses import dataclass

_B0 = 0.6


@dataclass
class EffluentResult:
    emissoes_ch4: float
    emissoes_n2o: float
    emissoes_co2_biogenico: float
    emissoes_tco2e: float


def calculate(
    volume_efluente: float,
    carga_organica_entrada: float,
    carga_organica_lodo: float,
    mcf_tratamento: float,
    mcf_tratamento_2: float,
    mcf_disposicao: float,
    ch4_recuperado: float,
    nitrogenio_efluente: float,
    fator_n2o: float,
    tratamento_sequencial: bool,
    efluente_lancado_ambiente: bool,
    gwp_ch4: float = 27.9,
    gwp_n2o: float = 273.0,
) -> EffluentResult:
    carga_organica_degradavel = (carga_organica_entrada - carga_organica_lodo) * volume_efluente

    effective_mcf = mcf_tratamento
    if tratamento_sequencial:
        effective_mcf = (mcf_tratamento + mcf_tratamento_2) / 2
    if efluente_lancado_ambiente:
        effective_mcf = (effective_mcf + mcf_disposicao) / 2 if efluente_lancado_ambiente else effective_mcf

    ch4_gerado = carga_organica_degradavel * _B0 * effective_mcf
    ch4_emitido = max(0.0, ch4_gerado - ch4_recuperado)
    emissoes_ch4 = ch4_emitido / 1000

    nitrogenio_total = nitrogenio_efluente * volume_efluente
    n2o_n = nitrogenio_total * fator_n2o
    n2o_emitido = n2o_n * (44 / 28)
    emissoes_n2o = n2o_emitido / 1000

    co2_biogenico = ch4_recuperado * (44 / 16) / 1000

    emissoes_tco2e = (emissoes_ch4 * gwp_ch4) + (emissoes_n2o * gwp_n2o)

    return EffluentResult(
        emissoes_ch4=emissoes_ch4,
        emissoes_n2o=emissoes_n2o,
        emissoes_co2_biogenico=co2_biogenico,
        emissoes_tco2e=emissoes_tco2e,
    )
