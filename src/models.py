from .base import Base
from .domains.organizations.models import Organizacao, OrganizacaoUsuario, OrganizacaoUsuarioModulo
from .domains.users.models import (
    CategoriaPermissao,
    Profile,
    UserPermissao,
    UserRole,
    UserSystem,
    UserTrialStatus,
)
from .domains.inventories.models import Inventario
from .domains.scope1.mobile_combustion.models import EmissaoCombustaoMovel
from .domains.scope1.stationary_combustion.models import EmissaoEstacionaria
from .domains.scope1.fugitive.models import EmissaoFugitiva
from .domains.scope1.effluents.models import EmissaoEfluente
from .domains.scope2.energy.models import ConsumoEnergia, EvidenciaConsumoEnergia, UnidadeConsumidora
from .domains.scope3.business_travel.models import Deslocamento, EmissaoViagemNegocio
from .domains.commuting.models import (
    CommutingColaborador,
    CommutingColaboradorMedalha,
    CommutingEmpresa,
    CommutingMedalha,
    CommutingRegistro,
    CommutingTransporteHabitual,
)
from .domains.questionnaires.models import (
    QuestionarioDeslocamento,
    QuestionarioRespondente,
    QuestionarioSalvo,
    RateLimit,
)
from .domains.reference_data.models import (
    AeroportoCoordenada,
    ComposicaoCombustivel,
    ConsumoUnidadeMedida,
    EquivalenciaVeiculo,
    FatorEmissaoAerea,
    FatorEmissaoEnergia,
    FatorEstacionaria,
    FatorFrotaTipoCombustivel,
    FatorTipoCombustivel,
    FatorTratamentoEfluente,
    FatorTransporteOnibus,
    FatorVariavelGhg,
    Gwp,
    TipoEfluenteIndustrial,
    TransporteMetro,
    TransporteTrem,
)

__all__ = [
    "Base",
    "Organizacao",
    "OrganizacaoUsuario",
    "OrganizacaoUsuarioModulo",
    "Profile",
    "UserRole",
    "UserSystem",
    "UserPermissao",
    "CategoriaPermissao",
    "UserTrialStatus",
    "Inventario",
    "EmissaoCombustaoMovel",
    "EmissaoEstacionaria",
    "EmissaoFugitiva",
    "EmissaoEfluente",
    "UnidadeConsumidora",
    "ConsumoEnergia",
    "EvidenciaConsumoEnergia",
    "EmissaoViagemNegocio",
    "Deslocamento",
    "CommutingEmpresa",
    "CommutingColaborador",
    "CommutingTransporteHabitual",
    "CommutingRegistro",
    "CommutingMedalha",
    "CommutingColaboradorMedalha",
    "QuestionarioSalvo",
    "QuestionarioRespondente",
    "QuestionarioDeslocamento",
    "RateLimit",
    "FatorTipoCombustivel",
    "FatorFrotaTipoCombustivel",
    "FatorEstacionaria",
    "FatorEmissaoEnergia",
    "FatorEmissaoAerea",
    "FatorTransporteOnibus",
    "FatorTratamentoEfluente",
    "FatorVariavelGhg",
    "Gwp",
    "ComposicaoCombustivel",
    "ConsumoUnidadeMedida",
    "EquivalenciaVeiculo",
    "AeroportoCoordenada",
    "TipoEfluenteIndustrial",
    "TransporteMetro",
    "TransporteTrem",
]
