from dataclasses import dataclass
from io import BytesIO
from uuid import UUID

from fpdf import FPDF
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...util.logger import retrieve_logger
from ..inventories.models import Inventario
from ..organizations.models import Organizacao
from ..scope1.effluents.models import EmissaoEfluente
from ..scope1.fugitive.models import EmissaoFugitiva
from ..scope1.mobile_combustion.models import EmissaoCombustaoMovel
from ..scope1.stationary_combustion.models import EmissaoEstacionaria
from ..scope2.energy.models import ConsumoEnergia
from ..scope3.business_travel.models import EmissaoViagemNegocio

_LOGGER = retrieve_logger(__name__)


@dataclass
class InventoryTotals:
    scope1_tco2e: float
    scope2_tco2e: float
    scope3_tco2e: float
    total_tco2e: float


async def _fetch_totals(inventory_id: UUID, session: AsyncSession) -> InventoryTotals:
    async def sum_column(model, column, org_id=None):
        rows = await session.execute(select(model))
        total = 0.0
        for row in rows.scalars().all():
            val = getattr(row, column, None)
            if val is not None:
                total += val
        return total

    inv_result = await session.execute(
        select(Inventario).where(Inventario.id == inventory_id))
    inv = inv_result.scalar_one_or_none()
    if not inv:
        return InventoryTotals(0.0, 0.0, 0.0, 0.0)

    org_id = inv.organizacao_id

    async def org_sum(model, emission_col, org_col="organizacao_id"):
        result = await session.execute(
            select(model).where(getattr(model, org_col) == org_id))
        return sum(
            (getattr(r, emission_col) or 0.0) for r in result.scalars().all()
        )

    mobile = await org_sum(EmissaoCombustaoMovel, "emissoes_tco2e_total")
    stationary = await org_sum(EmissaoEstacionaria, "emissoes_tco2e_total")
    fugitive = await org_sum(EmissaoFugitiva, "emissoes_tco2e")
    effluent = await org_sum(EmissaoEfluente, "emissoes_tco2e_total")
    scope1 = mobile + stationary + fugitive + effluent

    energy = await org_sum(ConsumoEnergia, "emissoes_energia_tco2e")
    scope2 = energy

    business_travel = await org_sum(EmissaoViagemNegocio, "emissoes_tco2e_total")
    scope3 = business_travel

    return InventoryTotals(
        scope1_tco2e=scope1,
        scope2_tco2e=scope2,
        scope3_tco2e=scope3,
        total_tco2e=scope1 + scope2 + scope3,
    )


async def generate_pdf(inventory_id: UUID, session: AsyncSession) -> bytes:
    _LOGGER.info("Generating PDF report for inventory %s", inventory_id)
    inv_result = await session.execute(
        select(Inventario).where(Inventario.id == inventory_id))
    inv = inv_result.scalar_one_or_none()

    org_name = ""
    if inv:
        org_result = await session.execute(
            select(Organizacao).where(Organizacao.id == inv.organizacao_id))
        org = org_result.scalar_one_or_none()
        org_name = org.nome if org else ""

    totals = await _fetch_totals(inventory_id, session)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Relatorio de Inventario de Emissoes GHG", ln=True, align="C")

    pdf.set_font("Helvetica", size=12)
    pdf.ln(4)
    if inv:
        pdf.cell(0, 8, f"Inventario: {inv.nome}", ln=True)
        pdf.cell(0, 8, f"Organizacao: {org_name}", ln=True)
        pdf.cell(0, 8, f"Ano base: {inv.ano_base}", ln=True)
        if inv.status:
            pdf.cell(0, 8, f"Status: {inv.status}", ln=True)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Resumo de Emissoes (tCO2e)", ln=True)

    pdf.set_font("Helvetica", size=12)
    rows = [
        ("Escopo 1 - Emissoes Diretas", totals.scope1_tco2e),
        ("Escopo 2 - Energia Eletrica", totals.scope2_tco2e),
        ("Escopo 3 - Outras Indiretas", totals.scope3_tco2e),
        ("TOTAL", totals.total_tco2e),
    ]
    for label, value in rows:
        is_total = label == "TOTAL"
        if is_total:
            pdf.set_font("Helvetica", "B", 12)
            pdf.ln(2)
        pdf.cell(120, 8, label)
        pdf.cell(40, 8, f"{value:,.3f}", align="R", ln=True)
        if is_total:
            pdf.set_font("Helvetica", size=12)

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Gerado automaticamente pelo sistema Pegada - Mercado Net Zero", ln=True)

    _LOGGER.info("PDF report generated for inventory %s", inventory_id)
    buf = BytesIO()
    buf.write(pdf.output())
    return buf.getvalue()
